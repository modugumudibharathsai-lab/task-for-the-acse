-- =====================================================================
-- 10_agentops.sql
-- The schema that makes the platform agentic rather than a set of reports.
-- Every agent run, every recommendation, every human decision and every
-- measured outcome is recorded here. This is what allows the institution
-- to answer "why did the system say that" and "did it actually help".
-- =====================================================================

CREATE TABLE agentops.agent (
    agent_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code text NOT NULL UNIQUE,            -- 'A11_ATTENDANCE_ANALYSIS'
    agent_no smallint,                    -- 1..72, maps to the catalogue
    name text NOT NULL,
    domain text NOT NULL,
    agent_class smallint NOT NULL CHECK (agent_class IN (1,2,3)),
    -- 1 = retrieval, 2 = analytical, 3 = predictive/prescriptive
    scope_statement text NOT NULL,
    out_of_scope text,
    reasoning_policy text NOT NULL CHECK (reasoning_policy IN
        ('RETRIEVE_ONLY','COMPUTE','RECOMMEND','ACT_WITH_APPROVAL')),
    requires_human_approval boolean NOT NULL DEFAULT false,
    escalation_rule text,
    owner_user_id uuid REFERENCES identity.app_user,
    version text NOT NULL DEFAULT '1.0',
    status text NOT NULL DEFAULT 'DEVELOPMENT'
           CHECK (status IN ('DEVELOPMENT','PILOT','ACTIVE','SUSPENDED','RETIRED')),
    deployed_on date
);
COMMENT ON COLUMN agentops.agent.owner_user_id IS
  'Every agent needs a named human owner responsible for its accuracy, knowledge base '
  'currency and escalations. Agents without owners degrade silently.';

-- Declared tool set. An agent cannot reach data outside this list.
CREATE TABLE agentops.agent_tool (
    agent_tool_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id uuid NOT NULL REFERENCES agentops.agent ON DELETE CASCADE,
    tool_name text NOT NULL,
    resource_schema text,
    resource_object text,
    access_mode text NOT NULL CHECK (access_mode IN ('READ','WRITE','EXECUTE','EXTERNAL_API')),
    row_scope_rule text,                  -- e.g. 'own_offerings','department','self'
    UNIQUE (agent_id, tool_name, resource_schema, resource_object)
);

CREATE TABLE agentops.agent_run (
    agent_run_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id uuid NOT NULL REFERENCES agentops.agent,
    agent_version text NOT NULL,
    trigger_type text NOT NULL CHECK (trigger_type IN ('USER','SCHEDULED','EVENT','CHAINED')),
    parent_run_id uuid REFERENCES agentops.agent_run,   -- orchestration chains
    invoked_by_user_id uuid REFERENCES identity.app_user,
    effective_role_id uuid REFERENCES identity.role,
    scope jsonb,                          -- term, department, offering, student set
    request_text text,
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz,
    latency_ms integer,
    token_input integer, token_output integer, cost_estimate numeric(10,4),
    status text NOT NULL DEFAULT 'RUNNING'
           CHECK (status IN ('RUNNING','SUCCEEDED','FAILED','PARTIAL','BLOCKED')),
    failure_reason text
);
CREATE INDEX idx_run_agent_time ON agentops.agent_run (agent_id, started_at DESC);

-- Provenance: exactly which records fed a given run. Without this, an
-- accreditation figure cannot be walked back to its source.
CREATE TABLE agentops.agent_run_input (
    agent_run_input_id bigserial PRIMARY KEY,
    agent_run_id uuid NOT NULL REFERENCES agentops.agent_run ON DELETE CASCADE,
    source_schema text NOT NULL,
    source_table text NOT NULL,
    source_id uuid,
    record_count integer,
    filter_expression text
);

CREATE TABLE agentops.agent_output (
    agent_output_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_run_id uuid NOT NULL REFERENCES agentops.agent_run ON DELETE CASCADE,
    output_type text NOT NULL CHECK (output_type IN
        ('ANSWER','REPORT','RECOMMENDATION','CLASSIFICATION','PREDICTION','ALERT','DRAFT','ACTION_PROPOSAL')),
    subject_type text,                    -- STUDENT, FACULTY, COURSE_OFFERING, DEPARTMENT
    subject_id uuid,
    payload jsonb NOT NULL,
    reasoning_summary text,               -- shown to the user; the "show your working" rule
    citations jsonb,                      -- document/clause references for retrieval agents
    interpretation jsonb,                 -- metric, filters, period applied (Agent 63 rule)
    confidence numeric(4,3),
    requires_approval boolean NOT NULL DEFAULT false,
    approval_status text NOT NULL DEFAULT 'NOT_REQUIRED'
           CHECK (approval_status IN ('NOT_REQUIRED','PENDING','APPROVED','MODIFIED','REJECTED','EXPIRED')),
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_output_subject ON agentops.agent_output (subject_type, subject_id, created_at DESC);
CREATE INDEX idx_output_pending ON agentops.agent_output (approval_status) WHERE approval_status = 'PENDING';

-- The human approval gate. Rejection reasons are the most valuable
-- improvement signal the platform produces.
CREATE TABLE agentops.human_review (
    human_review_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_output_id uuid NOT NULL REFERENCES agentops.agent_output ON DELETE CASCADE,
    reviewer_user_id uuid NOT NULL REFERENCES identity.app_user,
    decision text NOT NULL CHECK (decision IN ('APPROVE','MODIFY','REJECT','ESCALATE')),
    modified_payload jsonb,
    reason text,
    reason_category text,                 -- WRONG_DATA, WRONG_LOGIC, MISSING_CONTEXT, POLICY
    reviewed_at timestamptz NOT NULL DEFAULT now(),
    time_to_review_seconds integer
);

CREATE TABLE agentops.agent_feedback (
    agent_feedback_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_output_id uuid REFERENCES agentops.agent_output,
    agent_run_id uuid REFERENCES agentops.agent_run,
    user_id uuid REFERENCES identity.app_user,
    rating smallint CHECK (rating IN (-1, 1)),
    comment text,
    submitted_at timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- Risk flags, interventions and outcome measurement.
-- This is the detect - decide - act - measure loop. Most institutional
-- analytics stops at detect; the last table is what makes it worth building.
-- ---------------------------------------------------------------------
CREATE TABLE agentops.risk_flag (
    risk_flag_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id uuid NOT NULL REFERENCES agentops.agent,
    agent_run_id uuid REFERENCES agentops.agent_run,
    subject_type text NOT NULL CHECK (subject_type IN ('STUDENT','FACULTY','COURSE_OFFERING','DEPARTMENT')),
    student_id uuid REFERENCES people.student,
    faculty_id uuid REFERENCES people.faculty,
    course_offering_id uuid REFERENCES academics.course_offering,
    flag_type text NOT NULL CHECK (flag_type IN
        ('ATTENDANCE_SHORTFALL','ACADEMIC_DIFFICULTY','DISENGAGEMENT','BACKLOG_ACCUMULATION',
         'FINANCIAL_DIFFICULTY','WELLBEING_CONCERN','SYLLABUS_SLIPPAGE','RESULT_DECLINE',
         'SCHOLARSHIP_RISK','PLACEMENT_GAP')),
    severity text NOT NULL CHECK (severity IN ('WATCH','MODERATE','HIGH','CRITICAL')),
    -- Deviation from the subject's OWN baseline, not a cohort average
    baseline_value numeric(10,3),
    observed_value numeric(10,3),
    deviation_summary text,
    contributing_signals jsonb NOT NULL,  -- multi-signal evidence, shown to the responder
    suggested_first_action text,
    raised_at timestamptz NOT NULL DEFAULT now(),
    responder_user_id uuid REFERENCES identity.app_user,
    respond_by timestamptz,
    responded_at timestamptz,
    -- Calibration feedback: was the concern real?
    confirmed_by_human boolean,
    confirmation_note text,
    status text NOT NULL DEFAULT 'OPEN'
           CHECK (status IN ('OPEN','ACKNOWLEDGED','IN_PROGRESS','RESOLVED','FALSE_POSITIVE','ESCALATED','EXPIRED')),
    routed_to_confidential boolean NOT NULL DEFAULT false
);
CREATE INDEX idx_flag_open ON agentops.risk_flag (responder_user_id, status, respond_by)
  WHERE status IN ('OPEN','ACKNOWLEDGED');
CREATE INDEX idx_flag_student ON agentops.risk_flag (student_id, raised_at DESC);

COMMENT ON COLUMN agentops.risk_flag.confirmed_by_human IS
  'Populated when the responder closes the flag. Feeds threshold recalibration and the '
  'false-positive rate that must be published. An alert system that cries wolf is ignored, '
  'and then it is worse than nothing.';
COMMENT ON COLUMN agentops.risk_flag.routed_to_confidential IS
  'WELLBEING_CONCERN flags route to the counselling protocol, never to academic escalation, '
  'and their contributing signals are not written to the academic record.';

CREATE TABLE agentops.intervention (
    intervention_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_flag_id uuid REFERENCES agentops.risk_flag,
    cohort_key text,                      -- groups students sharing one remedial need
    intervention_type text NOT NULL CHECK (intervention_type IN
        ('REMEDIAL_CLASS','PEER_LEARNING','EXTRA_ASSIGNMENT','PRACTICE_TEST','MENTOR_MEETING',
         'FACULTY_COUNSELLING','BRIDGE_COURSE','PARENT_COMMUNICATION','COUNSELLING_REFERRAL',
         'FINANCIAL_SUPPORT','SKILL_TRAINING')),
    description text,
    owner_user_id uuid REFERENCES identity.app_user,
    course_offering_id uuid REFERENCES academics.course_offering,
    scheduled_from timestamptz, scheduled_to timestamptz,
    room_id uuid REFERENCES core.room,
    proposed_by_agent text,
    approved_by_user_id uuid REFERENCES identity.app_user,
    status text NOT NULL DEFAULT 'PROPOSED'
           CHECK (status IN ('PROPOSED','APPROVED','SCHEDULED','DELIVERED','CANCELLED','DECLINED'))
);

CREATE TABLE agentops.intervention_participant (
    intervention_id uuid NOT NULL REFERENCES agentops.intervention ON DELETE CASCADE,
    student_id uuid NOT NULL REFERENCES people.student,
    attended boolean,
    PRIMARY KEY (intervention_id, student_id)
);

CREATE TABLE agentops.intervention_outcome (
    intervention_outcome_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    intervention_id uuid NOT NULL REFERENCES agentops.intervention ON DELETE CASCADE,
    measured_at date NOT NULL,
    metric_name text NOT NULL,            -- 'internal_marks','attendance_pct','co_attainment'
    pre_value numeric(10,3),
    post_value numeric(10,3),
    comparison_group_delta numeric(10,3), -- similar students who did NOT attend
    net_effect numeric(10,3),
    sample_size smallint,
    notes text
);
COMMENT ON TABLE agentops.intervention_outcome IS
  'comparison_group_delta is the column that distinguishes measurement from wishful thinking. '
  'Without a comparison group, improvement cannot be attributed to the intervention.';

CREATE TABLE agentops.alert (
    alert_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_user_id uuid NOT NULL REFERENCES identity.app_user,
    agent_id uuid REFERENCES agentops.agent,
    risk_flag_id uuid REFERENCES agentops.risk_flag,
    severity text NOT NULL CHECK (severity IN ('INFO','WARNING','URGENT','CRITICAL')),
    title text NOT NULL,
    body text,
    channel text CHECK (channel IN ('IN_APP','EMAIL','SMS','WHATSAPP','PUSH','PHONE')),
    created_at timestamptz NOT NULL DEFAULT now(),
    delivered_at timestamptz, read_at timestamptz, actioned_at timestamptz,
    escalated_at timestamptz,
    escalated_to_user_id uuid REFERENCES identity.app_user
);
CREATE INDEX idx_alert_unread ON agentops.alert (recipient_user_id, created_at DESC)
  WHERE read_at IS NULL;

-- ---------------------------------------------------------------------
-- Model governance
-- ---------------------------------------------------------------------
CREATE TABLE agentops.model_version (
    model_version_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id uuid NOT NULL REFERENCES agentops.agent,
    version text NOT NULL,
    model_type text,                      -- LOGISTIC, GBM, RULE_BASED, LLM_PROMPT
    feature_list jsonb NOT NULL,
    excluded_features jsonb,              -- explicitly prohibited inputs, e.g. social_category
    training_period_start date, training_period_end date,
    training_cohorts text[],
    holdout_accuracy numeric(5,4),
    holdout_precision numeric(5,4), holdout_recall numeric(5,4),
    false_positive_rate numeric(5,4),
    validated_on date,
    approved_by_user_id uuid REFERENCES identity.app_user,
    status text NOT NULL DEFAULT 'CANDIDATE'
           CHECK (status IN ('CANDIDATE','VALIDATED','ACTIVE','DEPRECATED','WITHDRAWN')),
    UNIQUE (agent_id, version)
);
COMMENT ON COLUMN agentops.model_version.excluded_features IS
  'Prohibited inputs are declared, not merely omitted, so that a later change reintroducing '
  'a protected attribute or its proxy is visible in review.';

CREATE TABLE agentops.fairness_audit (
    fairness_audit_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id uuid NOT NULL REFERENCES agentops.agent,
    model_version_id uuid REFERENCES agentops.model_version,
    audit_period_start date NOT NULL, audit_period_end date NOT NULL,
    group_attribute text NOT NULL CHECK (group_attribute IN
        ('GENDER','SOCIAL_CATEGORY','ADMISSION_ROUTE','REGION','LANGUAGE','RURAL_URBAN','DIFFERENTLY_ABLED')),
    group_metrics jsonb NOT NULL,         -- per-group flag rate, precision, recall
    disparity_ratio numeric(6,3),
    explained_by_academic_data boolean,
    proxy_risk_findings text,
    verdict text CHECK (verdict IN ('NO_CONCERN','MONITOR','ACTION_REQUIRED')),
    action_taken text,
    audited_at timestamptz NOT NULL DEFAULT now(),
    audited_by_user_id uuid REFERENCES identity.app_user,
    published_internally boolean NOT NULL DEFAULT false,
    UNIQUE (agent_id, group_attribute, audit_period_start, audit_period_end)
);
COMMENT ON TABLE agentops.fairness_audit IS
  'Mandatory each term for every agent_class = 3 agent. An unpublished fairness audit tends '
  'not to be acted on, hence published_internally is tracked.';

CREATE TABLE agentops.agent_incident (
    agent_incident_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id uuid NOT NULL REFERENCES agentops.agent,
    agent_output_id uuid REFERENCES agentops.agent_output,
    reported_at timestamptz NOT NULL DEFAULT now(),
    reported_by_user_id uuid REFERENCES identity.app_user,
    severity text NOT NULL CHECK (severity IN ('LOW','MEDIUM','HIGH','SEVERE')),
    category text CHECK (category IN
        ('WRONG_OUTPUT','DATA_LEAK','ACCESS_VIOLATION','HARMFUL_LANGUAGE','MISSED_ESCALATION','AVAILABILITY')),
    description text NOT NULL,
    affected_person_count integer,
    persons_notified boolean NOT NULL DEFAULT false,
    root_cause text,
    remediation text,
    fix_verified_at timestamptz,
    status text NOT NULL DEFAULT 'OPEN'
           CHECK (status IN ('OPEN','INVESTIGATING','REMEDIATED','CLOSED'))
);

-- Scheduled sweeps. Output must be pushed to a named responder, not left
-- on a dashboard nobody opens after the first fortnight.
CREATE TABLE agentops.schedule (
    schedule_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id uuid NOT NULL REFERENCES agentops.agent,
    cron_expression text NOT NULL,
    scope jsonb,
    push_to_role_id uuid REFERENCES identity.role,
    response_expected_hours smallint,
    is_active boolean NOT NULL DEFAULT true,
    last_run_at timestamptz, next_run_at timestamptz
);

SELECT core.add_audit_columns('agentops.agent');
SELECT core.add_audit_columns('agentops.risk_flag');
SELECT core.add_audit_columns('agentops.intervention');
SELECT core.add_audit_columns('agentops.model_version');
