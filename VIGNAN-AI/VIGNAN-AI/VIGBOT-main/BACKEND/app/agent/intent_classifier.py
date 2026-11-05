"""
VIGBOT: Intent Classifier Service (app/agent/intent_classifier.py)
Loads the trained intent classification pipeline and threshold configuration.
Enforces safety rules:
- Strictly loads only artifacts/intent_model.joblib and artifacts/intent_config.json.
- Refuses to load pipeline_test_ or preliminary_ models unless ALLOW_PIPELINE_TEST_MODEL=True.
- When ALLOW_PIPELINE_TEST_MODEL=True, logs a loud warning and sets routed_by to 'classifier_pipeline_test'.
- If the model file is missing or fails to load, gracefully falls back to the existing pipeline.
- Privacy constraint: Logs only intent, confidence, and routed_by. NEVER logs student query text.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger("vigbot.intent_classifier")

class IntentClassifierService:
    _instance: Optional["IntentClassifierService"] = None

    def __init__(self):
        self.model = None
        self.config: Dict[str, Any] = {}
        self.general_threshold: float = 0.15
        self.distress_threshold: float = 0.10
        self.out_of_scope_threshold: float = 0.50
        self.routed_by_label: str = "classifier"
        self.is_loaded: bool = False
        self._load_artifacts()

    @classmethod
    def get_instance(cls) -> "IntentClassifierService":
        if cls._instance is None:
            cls._instance = IntentClassifierService()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Used in unit tests to reload with new environment variables."""
        cls._instance = None

    def _resolve_path(self, relative_path: str) -> str:
        """Resolves path relative to BACKEND directory or project root."""
        base_backend = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        # Check relative to BACKEND
        cand1 = os.path.join(base_backend, relative_path)
        if os.path.exists(cand1):
            return cand1
        # Check relative to current working directory
        if os.path.exists(relative_path):
            return os.path.abspath(relative_path)
        # Check without BACKEND prefix if already prefixed
        cand3 = os.path.join(base_backend, relative_path.replace("BACKEND/", "").replace("BACKEND\\", ""))
        if os.path.exists(cand3):
            return cand3
        return cand1

    def _load_artifacts(self):
        from app.config import settings

        model_path_setting = getattr(settings, "INTENT_MODEL_PATH", "artifacts/intent_model.joblib")
        config_path_setting = getattr(settings, "INTENT_CONFIG_PATH", "artifacts/intent_config.json")
        allow_pipeline_test = getattr(settings, "ALLOW_PIPELINE_TEST_MODEL", False)

        resolved_model_path = self._resolve_path(model_path_setting)
        resolved_config_path = self._resolve_path(config_path_setting)
        model_filename = os.path.basename(resolved_model_path)

        # 1. Enforce rejection of pipeline_test_ and preliminary_ models unless explicitly allowed
        is_test_or_prelim = model_filename.startswith("pipeline_test_") or model_filename.startswith("preliminary_")

        if is_test_or_prelim:
            if not allow_pipeline_test:
                logger.error(
                    "REFUSING to load non-production intent model artifact '%s'. "
                    "ALLOW_PIPELINE_TEST_MODEL is false. Fallback to existing pipeline.",
                    model_filename,
                )
                self.model = None
                self.is_loaded = False
                return
            else:
                logger.warning(
                    "⚠️ [WARNING] ALLOW_PIPELINE_TEST_MODEL=True: Loading non-production intent model artifact '%s'. "
                    "ROUTED_BY tag will be set to 'classifier_pipeline_test' to prevent confusion with real model.",
                    model_filename,
                )
                self.routed_by_label = "classifier_pipeline_test"
        else:
            self.routed_by_label = "classifier"

        # 2. Check if model file exists
        if not os.path.exists(resolved_model_path):
            logger.warning(
                "Intent model artifact not found at '%s'. Intent classifier disabled (falling back to existing pipeline).",
                resolved_model_path,
            )
            self.model = None
            self.is_loaded = False
            return

        # 3. Load Joblib Model
        try:
            import joblib
            self.model = joblib.load(resolved_model_path)
            self.is_loaded = True
            logger.info("Successfully loaded intent classifier model from '%s'", resolved_model_path)
        except Exception as e:
            logger.error("Failed to load intent model from '%s': %s. Intent classifier disabled.", resolved_model_path, e)
            self.model = None
            self.is_loaded = False
            return

        # 4. Load Threshold Configuration JSON
        if os.path.exists(resolved_config_path):
            try:
                with open(resolved_config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                thresholds = self.config.get("thresholds", {})
                self.general_threshold = float(thresholds.get("general_threshold", 0.15))
                self.distress_threshold = float(thresholds.get("distress_threshold", 0.10))
                self.out_of_scope_threshold = float(thresholds.get("out_of_scope_threshold", 0.50))
                logger.info(
                    "Loaded intent thresholds: general=%.2f, distress=%.2f, out_of_scope=%.2f",
                    self.general_threshold,
                    self.distress_threshold,
                    self.out_of_scope_threshold,
                )
            except Exception as e:
                logger.warning("Could not read intent config at '%s': %s. Using default safety thresholds.", resolved_config_path, e)
        else:
            logger.info("Intent config JSON not found at '%s'. Using default safety thresholds.", resolved_config_path)

    def classify(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Classifies query text into one of the 18 intents.
        Privacy Rule: Logs ONLY intent, confidence, and routed_by. NEVER logs text.
        Returns:
            Dict with intent, confidence, threshold, is_confident, and routed_by,
            or None if model is not loaded.
        """
        if not self.is_loaded or self.model is None:
            return None

        try:
            import numpy as np
            proba = np.asarray(self.model.predict_proba([text])[0])
            best_idx = int(proba.argmax())
            predicted_intent = str(self.model.classes_[best_idx])
            confidence = float(proba[best_idx])

            # Determine specific threshold for the predicted intent
            if predicted_intent == "distress_support":
                threshold = self.distress_threshold
            elif predicted_intent == "out_of_scope":
                threshold = self.out_of_scope_threshold
            else:
                threshold = self.general_threshold

            is_confident = bool(confidence >= threshold)

            # Privacy constraint: Log ONLY intent, confidence, is_confident, and routed_by.
            # NEVER log the query text.
            logger.info(
                "Intent classification: intent=%s confidence=%.4f is_confident=%s routed_by=%s",
                predicted_intent,
                confidence,
                is_confident,
                self.routed_by_label,
            )

            return {
                "intent": predicted_intent,
                "confidence": confidence,
                "threshold": threshold,
                "is_confident": is_confident,
                "routed_by": self.routed_by_label,
            }
        except Exception as e:
            logger.error("Intent classification prediction error: %s", e)
            return None
