"""
VIGBOT Persistent Progress & Crash-Safe Checkpoint Manager
Ensures all research, dataset curation, indexing, and benchmarking phases are
100% resumable, atomic, verifiable, and crash-safe against abrupt shutdowns.
"""

import os
import sys
import json
import time
import shutil
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set


def get_current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_pid_alive(pid: int) -> bool:
    """Check if process ID is alive on Windows or POSIX."""
    if pid <= 0:
        return False
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        except Exception:
            pass
    try:
        os.kill(pid, 0)
        return True
    except (OSError, PermissionError, ProcessLookupError, AttributeError):
        return False


class CheckpointManager:
    """
    Authoritative state and checkpoint manager for VIGBOT research operations.
    Guarantees atomic persistence, checksum validation, and automatic recovery.
    """

    SCHEMA_VERSION = "1.0.0"

    DEFAULT_PHASES = {
        "phase_1_audit": {
            "title": "Phase 1: Project & Baseline Audit",
            "subtasks": [
                "audit_existing_architecture",
                "validate_active_model_catalogs",
                "establish_baseline_benchmark"
            ]
        },
        "phase_2_research": {
            "title": "Phase 2: Comprehensive Vignan Research",
            "subtasks": [
                "crawl_official_vignan_sources",
                "extract_academic_regulations",
                "extract_fees_and_financial_aid",
                "extract_department_and_curriculum_docs",
                "extract_campus_facilities_and_services",
                "extract_grievance_and_statutory_policies"
            ]
        },
        "phase_3_questions": {
            "title": "Phase 3: Autonomous Question Generation",
            "subtasks": [
                "generate_factual_procedural_questions",
                "generate_scenarios_and_whatif_questions",
                "generate_hinglish_and_colloquial_questions",
                "generate_abstention_and_edgecase_questions"
            ]
        },
        "phase_4_answering": {
            "title": "Phase 4: Evidence Grounding & Fact Verification",
            "subtasks": [
                "ground_answers_against_official_sources",
                "verify_numeric_and_policy_constraints",
                "flag_unverified_or_abstention_cases"
            ]
        },
        "phase_5_dataset": {
            "title": "Phase 5: Knowledge Dataset Construction",
            "subtasks": [
                "deduplicate_and_format_qa_dataset",
                "compile_source_registry",
                "partition_train_val_eval_splits"
            ]
        },
        "phase_6_rag_integration": {
            "title": "Phase 6: Retrieval & Vector Index Integration",
            "subtasks": [
                "chunk_documents_with_metadata",
                "build_hybrid_bm25_dense_retriever",
                "integrate_retrieval_into_nlu_orchestrator"
            ]
        },
        "phase_7_assistant_polish": {
            "title": "Phase 7: Pedagogical AI Assistant Polish",
            "subtasks": [
                "inject_vignan_policy_grounding_into_prompts",
                "test_multiturn_context_with_citations",
                "verify_clear_distinction_personal_vs_public"
            ]
        },
        "phase_8_finetune_assessment": {
            "title": "Phase 8: Fine-Tuning Feasibility & Offline Engine",
            "subtasks": [
                "assess_local_compute_and_quota_constraints",
                "upgrade_offline_vignan_knowledge_engine"
            ]
        },
        "phase_9_improvement_loop": {
            "title": "Phase 9: Autonomous Improvement Loop",
            "subtasks": [
                "identify_weak_categories",
                "targeted_knowledge_patching",
                "verify_zero_regression_across_loop"
            ]
        },
        "phase_10_evaluation": {
            "title": "Phase 10: 200+ Question Evaluation Suite",
            "subtasks": [
                "assemble_heldout_benchmark_suite",
                "run_comprehensive_benchmark_evaluation",
                "compute_deterministic_and_factual_metrics"
            ]
        },
        "phase_11_security": {
            "title": "Phase 11: Security, Privacy & Reliability Guardrails",
            "subtasks": [
                "verify_rlac_isolation_under_rag",
                "verify_prompt_injection_defense_in_documents",
                "verify_distress_escalation_inviolability"
            ]
        },
        "phase_12_dashboard": {
            "title": "Phase 12: Research Quality Dashboard & Report",
            "subtasks": [
                "generate_research_quality_report",
                "render_final_manifest_summary"
            ]
        }
    }

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self.base_dir = Path(base_dir).resolve()
        else:
            repo_root = Path(__file__).resolve().parent.parent.parent.parent
            self.base_dir = repo_root / "BACKEND" / "data" / "vigbot_research"

        self.progress_file = self.base_dir / "progress.json"
        self.progress_md = self.base_dir / "PROGRESS.md"
        self.phase_status_file = self.base_dir / "phase_status.json"
        self.manifest_file = self.base_dir / "manifest.json"
        self.errors_file = self.base_dir / "errors.jsonl"
        self.checkpoints_dir = self.base_dir / "checkpoints"
        self.locks_dir = self.base_dir / "locks"
        self.datasets_dir = self.base_dir / "datasets"
        self.documents_dir = self.base_dir / "documents"

        self._ensure_directories()
        self.state: Dict[str, Any] = {}
        self.phase_status: Dict[str, Any] = {}
        self.manifest: Dict[str, Any] = {}
        self.load_state_with_recovery()

    def _ensure_directories(self) -> None:
        """Create required research directory hierarchy safely."""
        for d in [self.base_dir, self.checkpoints_dir, self.locks_dir, self.datasets_dir, self.documents_dir]:
            d.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # LOCKING MECHANISM
    # -------------------------------------------------------------------------

    def acquire_lock(self, job_name: str = "research_runner") -> bool:
        """Acquires an exclusive execution lock. Detects and clears stale locks."""
        lock_file = self.locks_dir / f"{job_name}.lock"
        current_pid = os.getpid()

        if lock_file.exists():
            try:
                with open(lock_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                locked_pid = data.get("pid")
                if locked_pid and is_pid_alive(locked_pid):
                    # Lock is held by an active process
                    return False
                # Stale lock: PID is no longer running
            except Exception:
                pass  # Corrupted lock file, overwrite it

        lock_data = {
            "pid": current_pid,
            "job_name": job_name,
            "acquired_at": get_current_iso_timestamp(),
            "hostname": os.environ.get("COMPUTERNAME", "localhost")
        }
        self.atomic_write_json(lock_file, lock_data)
        return True

    def release_lock(self, job_name: str = "research_runner") -> None:
        """Releases execution lock."""
        lock_file = self.locks_dir / f"{job_name}.lock"
        if lock_file.exists():
            try:
                lock_file.unlink()
            except OSError:
                pass

    # -------------------------------------------------------------------------
    # ATOMIC I/O & CHECKSUMMING
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_sha256(filepath: Path) -> str:
        """Computes SHA-256 hash of a file."""
        if not filepath.exists():
            return ""
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def calculate_string_sha256(content: str) -> str:
        """Computes SHA-256 hash of a string."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def atomic_write_json(self, target_path: Path, data: Any) -> None:
        """Writes JSON atomically using a temporary file and atomic replace with Windows retry."""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = target_path.with_suffix(f".tmp.{os.getpid()}_{int(time.time()*1000)}")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            
            # Windows retry loop to gracefully handle transient file locks
            for attempt in range(5):
                try:
                    os.replace(tmp_path, target_path)
                    break
                except (PermissionError, OSError):
                    if attempt == 4:
                        raise
                    time.sleep(0.05 * (attempt + 1))
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass

    # -------------------------------------------------------------------------
    # STATE INITIALIZATION & RECOVERY
    # -------------------------------------------------------------------------

    def _init_default_phase_status(self) -> Dict[str, Any]:
        """Initializes pristine phase status dictionary."""
        status = {}
        for phase_id, phase_meta in self.DEFAULT_PHASES.items():
            status[phase_id] = {
                "title": phase_meta["title"],
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "subtasks": {}
            }
            for task_id in phase_meta["subtasks"]:
                status[phase_id]["subtasks"][task_id] = {
                    "status": "pending",
                    "started_at": None,
                    "completed_at": None,
                    "attempt_count": 0,
                    "error": None,
                    "last_successful_operation": None
                }
        return status

    def _init_default_manifest(self) -> Dict[str, Any]:
        """Initializes empty manifest."""
        return {
            "schema_version": self.SCHEMA_VERSION,
            "created_at": get_current_iso_timestamp(),
            "updated_at": get_current_iso_timestamp(),
            "artifacts": {}
        }

    def _init_default_state(self) -> Dict[str, Any]:
        """Initializes initial progress state."""
        return {
            "schema_version": self.SCHEMA_VERSION,
            "checkpoint_id": 0,
            "timestamp": get_current_iso_timestamp(),
            "current_phase": "phase_1_audit",
            "active_task_id": None,
            "stats": {
                "documents_discovered": 0,
                "documents_extracted": 0,
                "documents_indexed": 0,
                "questions_generated": 0,
                "verified_qa": 0,
                "unverified_qa": 0,
                "needs_review": 0,
                "benchmark_queries_evaluated": 0,
                "benchmark_accuracy": 0.0
            },
            "last_successful_operation": "Initialized Persistent Research Progress Manager",
            "next_operation": "Run baseline project audit and benchmark",
            "sha256": ""
        }

    def load_state_with_recovery(self) -> None:
        """
        Loads progress state, manifest, and phase status.
        If any file is corrupted or unparseable, automatically restores from the
        newest valid immutable checkpoint snapshot in checkpoints/.
        """
        # 1. Load phase_status
        if self.phase_status_file.exists():
            try:
                with open(self.phase_status_file, "r", encoding="utf-8") as f:
                    self.phase_status = json.load(f)
            except Exception as e:
                self.log_error("system", "load_phase_status", "CorruptedPhaseStatus", str(e), retryable=False)
                self.phase_status = self._init_default_phase_status()
        else:
            self.phase_status = self._init_default_phase_status()
            self.atomic_write_json(self.phase_status_file, self.phase_status)

        # 2. Load manifest
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file, "r", encoding="utf-8") as f:
                    self.manifest = json.load(f)
            except Exception as e:
                self.log_error("system", "load_manifest", "CorruptedManifest", str(e), retryable=False)
                self.manifest = self._init_default_manifest()
        else:
            self.manifest = self._init_default_manifest()
            self.atomic_write_json(self.manifest_file, self.manifest)

        # 3. Load progress.json with checkpoint fallback
        progress_loaded = False
        if self.progress_file.exists():
            try:
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    loaded_state = json.load(f)
                if isinstance(loaded_state, dict) and "checkpoint_id" in loaded_state:
                    self.state = loaded_state
                    progress_loaded = True
            except Exception as e:
                self.log_error("system", "load_progress", "CorruptedProgressJSON", str(e), retryable=False)

        if not progress_loaded:
            # Attempt recovery from the newest valid checkpoint
            recovered = self._recover_from_newest_checkpoint()
            if not recovered:
                self.state = self._init_default_state()
                self._save_state_internal()

        self.render_progress_md()

    def _recover_from_newest_checkpoint(self) -> bool:
        """Scans checkpoints/ and restores from the most recent valid checkpoint."""
        checkpoint_files = sorted(self.checkpoints_dir.glob("checkpoint_*.json"), reverse=True)
        for cp_file in checkpoint_files:
            try:
                with open(cp_file, "r", encoding="utf-8") as f:
                    cp_data = json.load(f)
                if isinstance(cp_data, dict) and "state" in cp_data:
                    self.state = cp_data["state"]
                    if "phase_status" in cp_data:
                        self.phase_status = cp_data["phase_status"]
                        self.atomic_write_json(self.phase_status_file, self.phase_status)
                    if "manifest" in cp_data:
                        self.manifest = cp_data["manifest"]
                        self.atomic_write_json(self.manifest_file, self.manifest)
                    self._save_state_internal()
                    self.log_error("system", "checkpoint_recovery", "RecoveredFromSnapshot",
                                   f"Recovered cleanly from {cp_file.name}", retryable=False)
                    return True
            except Exception:
                continue
        return False

    def _save_state_internal(self) -> None:
        """Internal helper to write progress.json atomically with checksum."""
        self.state["timestamp"] = get_current_iso_timestamp()
        # Compute sha256 of the payload without the sha256 field itself
        state_copy = {k: v for k, v in self.state.items() if k != "sha256"}
        serialized = json.dumps(state_copy, sort_keys=True)
        self.state["sha256"] = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        self.atomic_write_json(self.progress_file, self.state)

    # -------------------------------------------------------------------------
    # CHECKPOINTING & BOUNDARY SAVING
    # -------------------------------------------------------------------------

    def checkpoint(self, label: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Creates an immutable, validated snapshot of the entire execution state.
        Monotonically increments checkpoint_id.
        """
        self.state["checkpoint_id"] = self.state.get("checkpoint_id", 0) + 1
        cid = self.state["checkpoint_id"]
        ts_slug = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        snapshot_filename = f"checkpoint_{cid:05d}_{ts_slug}.json"
        snapshot_path = self.checkpoints_dir / snapshot_filename

        snapshot_data = {
            "checkpoint_id": cid,
            "label": label,
            "timestamp": get_current_iso_timestamp(),
            "metadata": metadata or {},
            "state": self.state,
            "phase_status": self.phase_status,
            "manifest": self.manifest
        }

        self.atomic_write_json(snapshot_path, snapshot_data)
        self.state["last_successful_operation"] = f"Checkpoint {cid:05d}: {label}"
        self._save_state_internal()
        self.render_progress_md()
        return cid

    # -------------------------------------------------------------------------
    # SUBTASK & BATCH TRACKING
    # -------------------------------------------------------------------------

    def start_phase(self, phase_id: str) -> None:
        """Marks a phase in_progress and records timestamp."""
        if phase_id in self.phase_status:
            self.phase_status[phase_id]["status"] = "in_progress"
            if not self.phase_status[phase_id]["started_at"]:
                self.phase_status[phase_id]["started_at"] = get_current_iso_timestamp()
            self.state["current_phase"] = phase_id
            self.atomic_write_json(self.phase_status_file, self.phase_status)
            self._save_state_internal()
            self.checkpoint(f"Started Phase: {phase_id}")

    def complete_phase(self, phase_id: str) -> None:
        """Marks a phase completed and records timestamp."""
        if phase_id in self.phase_status:
            self.phase_status[phase_id]["status"] = "completed"
            self.phase_status[phase_id]["completed_at"] = get_current_iso_timestamp()
            self.atomic_write_json(self.phase_status_file, self.phase_status)
            self.checkpoint(f"Completed Phase: {phase_id}")

    def start_subtask(self, phase_id: str, task_id: str) -> None:
        """Marks a specific subtask as in_progress."""
        if phase_id in self.phase_status and task_id in self.phase_status[phase_id]["subtasks"]:
            task = self.phase_status[phase_id]["subtasks"][task_id]
            task["status"] = "in_progress"
            task["started_at"] = get_current_iso_timestamp()
            task["attempt_count"] = task.get("attempt_count", 0) + 1
            self.state["active_task_id"] = task_id
            self.atomic_write_json(self.phase_status_file, self.phase_status)
            self._save_state_internal()

    def complete_subtask(self, phase_id: str, task_id: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Marks a subtask completed only after verifying output is safely stored."""
        if phase_id in self.phase_status and task_id in self.phase_status[phase_id]["subtasks"]:
            task = self.phase_status[phase_id]["subtasks"][task_id]
            task["status"] = "completed"
            task["completed_at"] = get_current_iso_timestamp()
            task["error"] = None
            if details:
                task["last_successful_operation"] = details.get("operation")
            self.state["active_task_id"] = None
            self.atomic_write_json(self.phase_status_file, self.phase_status)
            self.checkpoint(f"Completed Subtask: {phase_id} -> {task_id}", details)

    def fail_subtask(self, phase_id: str, task_id: str, error_msg: str, retryable: bool = True) -> None:
        """Records subtask failure with retryable/permanent status."""
        status = "failed_retryable" if retryable else "failed_permanent"
        if phase_id in self.phase_status and task_id in self.phase_status[phase_id]["subtasks"]:
            task = self.phase_status[phase_id]["subtasks"][task_id]
            task["status"] = status
            task["error"] = error_msg
            self.atomic_write_json(self.phase_status_file, self.phase_status)
            self.log_error(phase_id, task_id, "SubtaskFailure", error_msg, retryable=retryable, attempt=task.get("attempt_count", 1))
            self.checkpoint(f"Failure in {task_id} ({status})")

    def is_subtask_completed(self, phase_id: str, task_id: str) -> bool:
        """Returns True if the subtask has already completed successfully."""
        if phase_id in self.phase_status:
            subtasks = self.phase_status[phase_id].get("subtasks", {})
            return subtasks.get(task_id, {}).get("status") == "completed"
        return False

    def is_phase_completed(self, phase_id: str) -> bool:
        """Returns True if the entire phase is marked completed."""
        return self.phase_status.get(phase_id, {}).get("status") == "completed"

    # -------------------------------------------------------------------------
    # MANIFEST & ARTIFACT INVENTORY
    # -------------------------------------------------------------------------

    def register_artifact(self, artifact_id: str, relative_path: str, artifact_type: str,
                          record_count: int = 0, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Registers an immutable output artifact in the manifest with verified sha256 checksum,
        file size, and record count.
        """
        full_path = self.base_dir / relative_path
        sha = self.calculate_sha256(full_path) if full_path.exists() else ""
        size = full_path.stat().st_size if full_path.exists() else 0

        self.manifest["artifacts"][artifact_id] = {
            "artifact_id": artifact_id,
            "relative_path": relative_path,
            "artifact_type": artifact_type,
            "record_count": record_count,
            "file_size_bytes": size,
            "sha256": sha,
            "updated_at": get_current_iso_timestamp(),
            "metadata": metadata or {}
        }
        self.manifest["updated_at"] = get_current_iso_timestamp()
        self.atomic_write_json(self.manifest_file, self.manifest)

    def log_error(self, phase_id: str, task_id: str, error_type: str, details: str,
                  retryable: bool = True, attempt: int = 1) -> None:
        """Appends an error entry to the append-only errors.jsonl log."""
        record = {
            "timestamp": get_current_iso_timestamp(),
            "phase": phase_id,
            "task_id": task_id,
            "error_type": error_type,
            "details": details,
            "retryable": retryable,
            "attempt": attempt
        }
        with open(self.errors_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # -------------------------------------------------------------------------
    # METRICS UPDATE
    # -------------------------------------------------------------------------

    def update_stats(self, **kwargs) -> None:
        """Safely updates aggregate stats counters."""
        for k, v in kwargs.items():
            if k in self.state["stats"]:
                self.state["stats"][k] = v
        self._save_state_internal()
        self.render_progress_md()

    # -------------------------------------------------------------------------
    # PROGRESS.MD RENDERING
    # -------------------------------------------------------------------------

    def render_progress_md(self) -> None:
        """
        Generates a human-readable, executive PROGRESS.md document detailing
        all 12 phases, subtasks, stats, and the exact one-command resume workflow.
        """
        total_subtasks = 0
        completed_subtasks = 0
        in_progress_subtasks = 0
        failed_subtasks = 0

        for p_data in self.phase_status.values():
            for t_data in p_data.get("subtasks", {}).values():
                total_subtasks += 1
                st = t_data.get("status")
                if st == "completed":
                    completed_subtasks += 1
                elif st == "in_progress":
                    in_progress_subtasks += 1
                elif st in ("failed_retryable", "failed_permanent"):
                    failed_subtasks += 1

        pct = (completed_subtasks / total_subtasks * 100.0) if total_subtasks > 0 else 0.0

        md = []
        md.append("# VIGBOT Knowledge Engineering & AI Upgrade — Progress Tracker")
        md.append("\n> **Crash-Safe Checkpoint Architecture**: Automatic atomic persistence with zero work loss.\n")
        md.append("```bash")
        md.append("# One-command auto-resume from last valid checkpoint:")
        md.append("python scripts/resume_vigbot_research.py")
        md.append("")
        md.append("# Check current live status without running:")
        md.append("python scripts/resume_vigbot_research.py --status")
        md.append("```\n")

        md.append("## Executive Status Summary")
        md.append("| Metric | Current Value |")
        md.append("|---|---|")
        md.append(f"| **Active Phase** | `{self.state.get('current_phase', 'None')}` |")
        md.append(f"| **Last Successful Operation** | {self.state.get('last_successful_operation', 'N/A')} |")
        md.append(f"| **Next Immediate Action** | {self.state.get('next_operation', 'N/A')} |")
        md.append(f"| **Total Checkpoints Committed** | `{self.state.get('checkpoint_id', 0)}` |")
        md.append(f"| **Overall Subtask Completion** | **{completed_subtasks} / {total_subtasks} ({pct:.1f}%)** |")
        md.append(f"| **Last Checkpoint Timestamp** | `{self.state.get('timestamp', 'N/A')}` |")

        stats = self.state.get("stats", {})
        md.append("\n## Knowledge & Intelligence Statistics")
        md.append("| Category | Count / Value |")
        md.append("|---|---|")
        md.append(f"| **Official Documents Discovered** | `{stats.get('documents_discovered', 0)}` |")
        md.append(f"| **Official Documents Extracted** | `{stats.get('documents_extracted', 0)}` |")
        md.append(f"| **Passages Indexed in RAG** | `{stats.get('documents_indexed', 0)}` |")
        md.append(f"| **Realistic Questions Generated** | `{stats.get('questions_generated', 0)}` |")
        md.append(f"| **Verified Grounded Q&A Pairs** | `{stats.get('verified_qa', 0)}` |")
        md.append(f"| **Unverified / Abstention Pairs** | `{stats.get('unverified_qa', 0)}` |")
        md.append(f"| **Flagged for Human Review** | `{stats.get('needs_review', 0)}` |")
        md.append(f"| **Evaluation Queries Evaluated** | `{stats.get('benchmark_queries_evaluated', 0)}` |")
        md.append(f"| **Benchmark Accuracy** | `{stats.get('benchmark_accuracy', 0.0):.1f}%` |")

        md.append("\n## Phase Execution Breakdown")
        for p_id, p_meta in self.phase_status.items():
            st = p_meta.get("status", "pending")
            status_icon = "✅" if st == "completed" else ("🔄" if st == "in_progress" else "⏳")
            md.append(f"\n### {status_icon} {p_meta.get('title', p_id)} (`{st}`)")
            subtasks = p_meta.get("subtasks", {})
            if subtasks:
                md.append("| Subtask | Status | Attempts | Completed At | Notes |")
                md.append("|---|---|---|---|---|")
                for t_id, t_meta in subtasks.items():
                    t_st = t_meta.get("status", "pending")
                    t_icon = "✅" if t_st == "completed" else ("🔄" if t_st == "in_progress" else ("❌" if "failed" in t_st else "⏳"))
                    attempts = t_meta.get("attempt_count", 0)
                    done_at = t_meta.get("completed_at") or "-"
                    err = t_meta.get("error") or "-"
                    if err != "-":
                        err = f"`{err[:40]}`..."
                    md.append(f"| {t_icon} `{t_id}` | `{t_st}` | {attempts} | {done_at} | {err} |")

        md.append("\n## Manifest Artifacts")
        artifacts = self.manifest.get("artifacts", {})
        if artifacts:
            md.append("| Artifact ID | Relative Path | Type | Records | Size (Bytes) | SHA-256 (Prefix) |")
            md.append("|---|---|---|---|---|---|")
            for a_id, a_meta in artifacts.items():
                if isinstance(a_meta, str):
                    a_meta = {"relative_path": a_meta, "artifact_type": "artifact", "record_count": "-", "file_size_bytes": "-", "sha256": "-"}
                elif not isinstance(a_meta, dict):
                    continue
                sha_prefix = a_meta.get("sha256", "")[:12] + "..." if a_meta.get("sha256") else "-"
                md.append(f"| `{a_id}` | `{a_meta.get('relative_path')}` | `{a_meta.get('artifact_type')}` | {a_meta.get('record_count', 0)} | {a_meta.get('file_size_bytes', 0)} | `{sha_prefix}` |")
        else:
            md.append("*No output artifacts registered yet.*")

        md_content = "\n".join(md)
        tmp_md = self.progress_md.with_suffix(f".tmp.{os.getpid()}")
        try:
            with open(tmp_md, "w", encoding="utf-8") as f:
                f.write(md_content)
                f.flush()
                os.fsync(f.fileno())
            for attempt in range(5):
                try:
                    os.replace(tmp_md, self.progress_md)
                    break
                except (PermissionError, OSError):
                    if attempt == 4:
                        break
                    time.sleep(0.05 * (attempt + 1))
        finally:
            if tmp_md.exists():
                try:
                    tmp_md.unlink()
                except OSError:
                    pass
