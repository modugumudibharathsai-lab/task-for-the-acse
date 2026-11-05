# VIGBOT Benchmark Audit & Data Leakage Assessment

**Document**: `benchmark_leakage_audit.md`  
**Phase**: Phase 14 — Independent Real-World Validation & Adversarial Testing  
**Auditor**: Senior AI Systems Architect & Evaluation Specialist  
**Target Artifacts**: `ml/generate_capability_tests.py`, `ml/evaluate_capability_suite.py`, `BACKEND/artifacts/capability_test_suite.json`

---

## 1. Executive Summary

Phase 13 reported a 100.00% benchmark score across 504 test cases. While the architectural hardening (regex word-boundary enforcement, false-action guards, anaphora discourse resolution) was genuine and demonstrably resolved the initial Lost & Found issue, **the 504-case capability test suite suffers from severe synthetic data leakage and circular generation patterns**.

A 100% score on this benchmark does **NOT** prove production readiness or universal real-world understanding. It primarily proves that the system reliably recognizes queries synthesized from the exact keywords and capability names hardcoded into its own capability registry.

---

## 2. Comprehensive Leakage & Independence Analysis

### 2.1. Were benchmark questions written independently of routing rules?
**Verdict: NO (Direct Code Dependency)**
- `ml/generate_capability_tests.py` directly imports `APPLICATION_CAPABILITIES` from `app.agent.capability_registry`.
- The generator iterates through each capability dictionary:
  ```python
  primary_kw = keywords[0] if keywords else cap_id
  second_kw = keywords[1] if len(keywords) > 1 else primary_kw
  third_kw = keywords[2] if len(keywords) > 2 else second_kw
  ```
- Because the queries are generated directly by indexing the capability dictionary, there is zero epistemic separation between the test author and the system under test.

### 2.2. Did test phrases directly reuse capability names, keywords, or templates?
**Verdict: YES (100% Keyword & Template Re-use)**
- Inspecting `generate_tests_for_capability()` reveals that all 18 dimensions are fixed template strings with keyword slot-filling:
  - Direct: `f"Where can I find information about {primary_kw}?"`
  - Indirect: `f"Is there a dedicated section on the portal to handle {second_kw}?"`
  - Conversational: `f"Could you please explain how {cap_name} works at our university?"`
  - Informal: `f"Hey where do I go for {third_kw} stuff?"`
  - Hinglish: `f"{primary_kw} kahan se check kar sakte hain?"`
  - Navigation: `f"Open {cap_name}"`
  - Short/Incomplete: `f"{cap_name}"`
- Since `find_matching_capability()` in `capability_registry.py` matches against `cap["keywords"]` and `re.escape(k)`, any template containing `primary_kw` is guaranteed to score high on the exact keyword being tested.

### 2.3. Were expected answers generated using the same logic being evaluated?
**Verdict: YES (Circular Labeling)**
- In `generate_tests_for_capability()`, the expected metadata is assigned from the loop variable:
  ```python
  "feature_id": cap_id,
  "expected_tab": cap["frontend_tab"],
  "expected_intent": CommunicationIntent.INFORMATION_REQUEST
  ```
- No independent human annotator or secondary classifier validated whether the query realistically implied that capability or whether a real student would expect that tab.

### 2.4. Did the "unseen generalization" category contain genuinely held-out questions?
**Verdict: NO (Synthetic Keyword Insertion)**
- In `ml/generate_capability_tests.py` lines 217–226:
  ```python
  # Dimension 16: Generalization / Unseen Language
  "query": f"How am I supposed to get my {primary_kw} sorted out?"
  ```
- This is not unseen language. It is simply the primary keyword wrapped in a single alternative English clause.
- Genuine held-out queries describe a student's real-world circumstance **without** naming the capability keyword.
  - *Example of synthetic generalization*: "How am I supposed to get my lost-and-found sorted out?"
  - *Example of genuine held-out situation*: "I left my blue water bottle on the 2nd floor desk during lunch break, has anyone seen it?" (Zero mention of "lost" or "found", yet unambiguously Lost & Found).

### 2.5. Did the benchmark test real backend execution or only classification?
**Verdict: ONLY NLU DICTIONARY CLASSIFICATION**
- `ml/evaluate_capability_suite.py` checked:
  1. `detected_cap["feature_id"] == expected_feat`
  2. `detected_intent == expected_intent`
  3. `res_redirect == expected_tab`
  4. `"SR-2026-" not in res_content` (for false write prevention)
- It **NEVER**:
  - Executed a real API call or database transaction.
  - Verified whether mandatory parameters (e.g. item description, location, contact info) were validated before writing.
  - Verified whether user confirmation was requested and cryptographically verified.
  - Tested whether frontend button click events trigger state transitions in the actual React/Next.js application.

---

## 3. Methodological Remediation Required for Phase 14

To provide authentic, audit-grade verification:

1. **Independent Test Dataset Creation (Phase 2)**:
   - Hand-authored and independently labeled without referencing `cap["keywords"]` or using slot-filling templates.
   - Situational scenarios written in the voice of stressed, confused, informal, and colloquial students.
   - Genuine out-of-scope, unsupported, adversarial, and negative instructions.

2. **Full Action Lifecycle & Parameter Verification (Phases 3 & 4)**:
   - For all 48 operations, verify mandatory parameter enforcement, state mutation, idempotency, and confirmation tokens on an isolated test database.

3. **End-to-End Frontend Routing Verification (Phase 5)**:
   - Verify every route and navigation action directly against the React component tree and URL parameter handler.

4. **Transparent, Multi-Metric Reporting (Phase 8)**:
   - Disaggregate results into separate, un-blended metrics: Feature ID, Intent Accuracy, Parameter Extraction, Backend Execution, Navigation Accuracy, False Write Count, and Latency.

