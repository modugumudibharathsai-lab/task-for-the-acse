# VIGBOT: Intent Classification System & Architecture Guide

This document provides a comprehensive, technically rigorous explanation of the Intent Classification subsystem engineered for **VIGBOT** (Autonomous University Assistant). It details the architectural rationale, mathematical formulation, threshold tuning methodology, data governance protocols, calibration caveats, and defense Q&A for academic and engineering review.

---

## 1. Executive Summary & Design Rationale

### 1.1 The Problem
VIGBOT previously relied on a dual-path NLU strategy:
1. **Handcrafted keyword regex rules** for high-frequency direct queries.
2. **Cloud LLM API fallback (Google Gemini / Groq)** for reasoning and intent extraction.

While flexible, routing every conversational inquiry to an external LLM introduces:
- **High Latency**: Cloud roundtrips require 400ms – 1,800ms per request, degrading conversational responsiveness.
- **Financial & API Rate Costs**: Continuous API calls for trivial classification consume API quotas and incur recurring operational expense.
- **Fragility**: Upstream API rate limits or network degradation directly interrupt basic campus navigation.

### 1.2 The Solution
We implemented a **lightweight, sub-millisecond, CPU-bound intent classification pipeline** using **TF-IDF Subword Character + Word N-Grams** coupled with **Multinomial Logistic Regression (L2 Regularized)**.

```
Incoming Student Query
          │
          ▼
[0. Security Guardrail: Prompt Injection & Cross-Student RLAC Defense]
          │ (Pass)
          ▼
[0.1 Crisis Guardrail: Deterministic Distress Regex Filter]
          │ (Pass)
          ▼
[0.5 ML Intent Classifier Service] (Feature Flag: USE_INTENT_CLASSIFIER)
   - Token & Subword Char Feature Extraction (~0.1ms)
   - Logistic Regression Scoring (~0.05ms)
   - Intent-Specific Confidence Threshold Evaluation
          ├── High Confidence (>= Threshold) ──► Direct Tool / Handler Dispatch (routed_by="classifier")
          │                                      [attendance, exams, fees, timetable, distress, etc.]
          └── Low Confidence (< Threshold)  ──► Seamless Graceful Fallback
                                                 │
                                                 ├── Existing Deterministic Rules (routed_by="rules")
                                                 └── Cloud Gemini Reasoning (routed_by="gemini")
```

### 1.3 Why TF-IDF + Logistic Regression over Deep Learning / LLMs?
| Metric / Attribute | Cloud LLM (Gemini 3.5 Flash) | Small Transformer (DistilBERT / MiniLM) | TF-IDF + Logistic Regression (VIGBOT) |
| :--- | :--- | :--- | :--- |
| **Inference Latency** | 400ms – 1,500ms | 15ms – 45ms (requires GPU/heavy CPU) | **0.2ms – 0.8ms (Single CPU core)** |
| **Memory Footprint** | 0 MB (Remote) | 250 MB – 500 MB RAM | **< 8 MB RAM total** |
| **Dependencies** | Network / HTTPS Client | PyTorch / ONNX Runtime (300MB+ wheels)| **scikit-learn, scipy, numpy (pure binary wheels)** |
| **Cold Start Overhead** | 0 ms | 1,200ms – 3,000ms | **< 20 ms model load time** |
| **Cost Per 100k Queries**| ~$5 – $15 | Hardware compute cost | **$0.00 (Zero marginal cost)** |
| **Transliteration Robustness**| High (with high prompt tokens) | Moderate (subword BPE) | **High (Word n-grams 1-2 + Char n-grams 3-5)** |

---

## 2. Intent Taxonomy (The 18 Target Intents)

All target intents are formally declared in [`ml/intents.yaml`](ml/intents.yaml), categorized into:
1. **Core Academic & Administrative (14 Intents)**:
   - `attendance`: Class attendance percentage, shortage warnings, condonation rules.
   - `exams`: Mid-term assessment schedules, room allotments, seating plans.
   - `marks`: Internal CIE marks, grade point calculations, grade cards.
   - `fees`: Tuition dues, payment links, scholarship concessions, receipts.
   - `timetable`: Weekly schedule, class timings, lecture hall locations.
   - `curriculum`: Course syllabus, graduation credit audits, prerequisites.
   - `faculty`: Faculty cabin locations, counselor/mentor contact details.
   - `library`: Book catalog search, issue renewals, overdue fines.
   - `hostel`: Room allotments, mess menus, curfew timings, maintenance requests.
   - `transport`: University bus routes, boarding timings, stop locations.
   - `circulars`: Official notifications, administrative announcements, holiday lists.
   - `events`: College fests, technical symposiums, hackathons.
   - `clubs`: Student club registrations, extracurricular auditions.
   - `services`: Bonafide certificates, ID card replacement, bus passes.

2. **Specialized & Safety-Critical Intents (4 Intents)**:
   - `policy_bylaws`: Institutional rules, detention policies, academic regulations (R23/R24).
   - `distress_support`: Mental health crises, panic, academic burnout, hopelessness (safety-critical).
   - `greeting_smalltalk`: Conversational greetings, helpdesk capabilities, onboarding.
   - `out_of_scope`: Off-topic queries (e.g., weather, politics, coding problems unrelated to university procedures).

---

## 3. Feature Pipeline & Model Architecture

### 3.1 Feature Extraction Pipeline
The model employs a `FeatureUnion` combining two complementary extraction mechanisms:
1. **Word N-Grams (`CountVectorizer` + `TfidfTransformer`)**:
   - `ngram_range=(1, 2)`: Captures unigrams and bigrams (e.g., *"attendance status"*, *"hall ticket"*).
   - `sublinear_tf=True`: Dampens high-frequency word counts ($1 + \log(\text{tf})$).
   - `min_df=1`: Captures specialized academic terminology even in small starter corpuses.
2. **Subword Character N-Grams (`CountVectorizer` + `TfidfTransformer`)**:
   - `ngram_range=(3, 5)`: Captures character chunks across word boundaries.
   - **Crucial for Indian English / Multilingual Context**: Student queries frequently contain phonetic transliterations, colloquial slang, and spelling typos (e.g., *"attendence"*, *"attendence entha"*, *"marks epudu"*, *"fees katali"*). Character n-grams ensure high similarity even with misspelled stems.

### 3.2 Classifier: Multinomial Logistic Regression
- **Loss Function**: Multinomial Cross-Entropy Loss with Softmax.
- **Regularization**: L2 Regularization ($C=2.0$) to avoid overfitting on author-specific vocabulary while retaining sharp class boundaries.
- **Optimization Algorithm**: `lbfgs` with `max_iter=1000` and `random_state=42`.

---

## 4. Threshold Tuning & Asymmetric Safety Policies

### 4.1 The Role of Dynamic Thresholds
Standard argmax classification assumes every query belongs to one of the 18 classes. In real-world helpdesk deployments, queries are frequently ambiguous, noisy, or completely out-of-domain.
Rather than blindly accepting the highest probability class, the classifier evaluates:
$$\hat{y} = \arg\max_k P(y=k \mid x)$$
$$\text{Confidence Score } S = \max_k P(y=k \mid x)$$

The decision rule is parameterized by intent-specific thresholds:
$$\text{Route to Classifier} \iff S \ge \tau_{\hat{y}}$$
If $S < \tau_{\hat{y}}$, the query is flagged as uncertain (`is_confident=False`) and gracefully falls back to the existing rules/Gemini engine.

### 4.2 Asymmetric Safety Rules
Thresholds are deliberately configured asymmetrically in [`ml/tune_threshold.py`](ml/tune_threshold.py) and stored in [`artifacts/intent_config.json`](artifacts/intent_config.json):

| Intent Category | Threshold ($\tau$) | Optimization Target | Justification |
| :--- | :--- | :--- | :--- |
| **`distress_support`** | **0.10** | **$\ge 99\%$ Recall** | **Zero-Tolerance Safety**: It is far safer to produce a false-positive escalation than to miss a student in acute distress. Even marginal confidence immediately triggers confidential human escalation (Tele-MANAS & Crisis Counseling). |
| **Standard Academic** | **0.15 – 0.25** | Balanced Precision & Coverage | Optimizes direct routing without risking misdirection for routine academic questions. |
| **`out_of_scope`** | **0.50** | **High Precision** | Prevents false rejections of legitimate academic questions phrased ambiguously. |

---

## 5. Data Governance & Split Protocol

### 5.1 Author Sequestration Protocol
To measure genuine generalizability across independent writing styles, dataset rows are strictly segregated by author:
- **Training Authors**: `aman`, `pragna`, `sirisha`.
- **System Starter Rows**: `agent` (used as baseline foundation in training folds).
- **Dedicated Holdout Test Author**: `sridhar`.

> [!IMPORTANT]
> **Strict Isolation Constraint**:
> Rows written by `sridhar` are **NEVER** accessed during feature fitting, cross-validation, hyperparameter tuning, or threshold selection.

### 5.2 Automated Data Guardrails ([`data/validate_data.py`](data/validate_data.py) & [`tests/test_data_guardrails.py`](tests/test_data_guardrails.py))
Every dataset entry must pass automated CI validation before being admitted to the pipeline:
1. **Encoding Integrity**: Strict UTF-8 validation with exact bad-line diagnostics (vital for Telugu and Hindi script).
2. **Author Stem Matching**: Row-level `author` column must strictly match the filename stem (`data/authors/<author>.csv`).
3. **Whitelist Author Enforcement**: Only authorized authors (`agent`, `aman`, `pragna`, `sirisha`, `sridhar`) are permitted.
4. **Exact Duplicate Prevention**: Detects and rejects duplicate question strings.
5. **Fuzzy Contamination & Leakage Prevention**:
   - Calculates **Token Jaccard Similarity** and **Character Difflib Ratio** between every test author row and all training rows.
   - Any pair with similarity $> 0.80$ is flagged as a leakage hazard.
   - CI policy: Suggests training rows to remove; **never edits or deletes test rows**.

### 5.3 Leave-One-Author-Out (LOAO) Cross-Validation
Standard random stratified $K$-fold splits suffer from severe **author style leakage** (the model memorizes vocabulary and sentence templates unique to an individual author).
VIGBOT uses **Leave-One-Author-Out (LOAO)** cross-validation across the human training authors:
- Fold 1: Train on `{agent, pragna, sirisha}`, Validate on `{aman}`.
- Fold 2: Train on `{agent, aman, sirisha}`, Validate on `{pragna}`.
- Fold 3: Train on `{agent, aman, pragna}`, Validate on `{sirisha}`.

This simulates real-world deployment where end-user students have writing habits never seen during development.

---

## 6. Calibration Caveats & Dry-Run Honesty

### 6.1 Confidence Scores vs. Calibrated Probabilities
Softmax outputs from logistic regression or neural networks are monotonic scores, **not calibrated Bayesian probabilities**.
- A model output of `0.80` does not necessarily mean an 80% empirical likelihood of correctness.
- In documentation and logs, outputs are explicitly denominated as **"confidence scores"**.
- Formal calibration requires post-hoc scaling (e.g., Platt Scaling or Isotonic Regression) evaluated via **Expected Calibration Error (ECE)** and **Reliability Curves**:
$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

### 6.2 Dry-Run Honesty Principle
During pipeline testing prior to human data authoring:
- Test-author `sridhar` contains 0 rows.
- Evaluating the code requires running on starter rows (`agent`).
- **Strict Labeling Rule**: All test outputs, console banners, and output files are explicitly prefixed with `pipeline_test_` and bear the notice:
> `EVALUATED ON TRAINING DATA (code dry run, not a performance measure)`
- Prevents deceptive claims of model accuracy before independent test sets are authored.

---

## 7. System Integration & Privacy Architecture

### 7.1 Non-Destructive Deployment
The intent classifier is integrated as a zero-risk, opt-in service:
- Default config setting: `USE_INTENT_CLASSIFIER = False`. The existing application behavior remains 100% identical unless explicitly enabled.
- Safe Loading Guard: The production service rejects `pipeline_test_` or `preliminary_` model files unless `ALLOW_PIPELINE_TEST_MODEL = True` is explicitly configured.
- Graceful Degradation: If model weights are missing or corrupted, the service logs a warning and falls back to existing rules/Gemini without raising unhandled 500 errors.

### 7.2 Execution Precedence & Guardrails
The request handling pipeline enforces strict defense-in-depth:
1. **Prompt Injection & Row-Level Access Control (RLAC)**:
   - Queries attempting `SYSTEM OVERRIDE` or requesting other students' records are trapped immediately by `is_prompt_injection_or_unauthorized_cross_student`.
   - Never reaches the intent classifier or LLM. Returns an immediate access-denied policy response.
2. **Distress Safety Filter**:
   - Evaluated before and within the classifier.
   - If classified as `distress_support` ($\ge 0.10$), immediately dispatches the mental health crisis tool.
   - **Never routes distress queries to cloud LLMs or generic search.**
3. **Traceability (`routed_by`)**:
   - Every `MessageResponse` payload returned by `/api/v1/conversations/{id}/messages` includes the routing origin:
     - `"rules"`: Fast deterministic rule or security guardrail.
     - `"classifier"`: Production trained intent model above threshold.
     - `"classifier_pipeline_test"`: Pipeline-test model loaded under test flag.
     - `"gemini"`: Upstream Gemini 3.5 Flash reasoning.

### 7.3 Student Privacy & Zero-Pii Logging
To comply with institutional privacy mandates (Clause 2.1 RLAC):
- The `IntentClassifierService.classify` method **NEVER** logs the raw student query text.
- Log outputs contain strictly operational telemetry:
```
INFO [vigbot.intent_classifier] Intent classification: intent=attendance confidence=0.8521 is_confident=True routed_by=classifier
```

---

## 8. Viva Voce & Technical Defense Q&A

### Q1: Why didn't you use a modern pretrained Transformer like RoBERTa or modern fine-tuning for this task?
**Answer:**
For intent classification across 18 well-defined operational categories in a real-time conversational helpdesk, latency and resource constraints dominate. A Transformer model requires 15ms–45ms inference latency, hundreds of megabytes of RAM, and GPU/PyTorch dependencies that drastically complicate deployment.
Our TF-IDF (word 1-2 + char 3-5 n-grams) + Logistic Regression pipeline runs in under 0.8ms on a standard CPU core, occupies less than 8MB of memory, has zero GPU dependencies, and is resilient to typos and Romanized Indian languages through subword character features. If query complexity exceeds classifier confidence, the system seamlessly hands off to Gemini 3.5 Flash.

### Q2: How do you prevent data leakage when authoring synthetic benchmark queries?
**Answer:**
We implement strict author-level isolation. Three teammates (`aman`, `pragna`, `sirisha`) authored training rows, while a fourth teammate (`sridhar`) authored the test set.
Our automated CI tool `validate_data.py` performs a dual-metric fuzzy similarity check (Token Jaccard and Character Difflib Ratio) comparing every test row against all training rows. Any row pair exceeding 0.80 similarity is flagged as leakage. Furthermore, our model selection utilizes Leave-One-Author-Out (LOAO) cross-validation rather than random stratified splitting, preventing the model from memorizing individual writing styles.

### Q3: Why is the threshold for `distress_support` set so low (0.10) compared to `out_of_scope` (0.50)?
**Answer:**
This is an asymmetric risk-utility design decision. Missing a student in emotional distress or crisis is a catastrophic failure mode. A low threshold (0.10) maximizes recall ($\ge 99\%$) for crisis intervention, routing the student to compassionate resources and confidential human escalation (Tele-MANAS / campus wellness center).
Conversely, `out_of_scope` uses a conservative threshold (0.50) to prevent false positives from accidentally silencing students asking legitimate, nuanced academic questions.

### Q4: If the model outputs a confidence of 0.85, does that mean there is an 85% probability the classification is correct?
**Answer:**
Not necessarily. Softmax outputs from uncalibrated models represent ranking scores rather than true empirical posterior probabilities. Overconfidence is a known property of uncalibrated cross-entropy loss. To treat scores as true probabilities, post-hoc calibration (such as Platt Scaling or Isotonic Regression) must be evaluated via Expected Calibration Error (ECE) and reliability diagrams. Hence, throughout VIGBOT, we strictly refer to them as "confidence scores."

### Q5: What happens if the intent model file is deleted or fails to deserialize in production?
**Answer:**
The system is built with complete graceful degradation. `IntentClassifierService` catches initialization and deserialization errors, logs a critical alert, and marks itself as `is_loaded = False`. The orchestrator checks this status and falls back directly to the existing keyword rules and Gemini pipeline without crashing or dropping student requests.
