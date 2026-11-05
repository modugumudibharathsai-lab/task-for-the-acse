-- =====================================================================
-- 09_governance_quality_knowledge.sql : Agents 53-57, 62-64, 71
-- =====================================================================

CREATE TABLE governance.policy_document (
    policy_document_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    title text NOT NULL,
    document_type text NOT NULL CHECK (document_type IN
        ('REGULATION','ORDINANCE','POLICY','SOP','STATUTE','GUIDELINE','MANUAL')),
    issuing_authority text,
    version text NOT NULL,
    effective_from date NOT NULL,
    effective_to date,
    supersedes_id uuid REFERENCES governance.policy_document,
    document_ref uuid,                   -- knowledge.document
    owner_role_id uuid REFERENCES identity.role,
    review_due_on date,
    status text NOT NULL DEFAULT 'ACTIVE'
           CHECK (status IN ('DRAFT','ACTIVE','SUPERSEDED','WITHDRAWN')),
    UNIQUE (institution_id, title, version)
);

CREATE TABLE governance.policy_clause (
    policy_clause_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_document_id uuid NOT NULL REFERENCES governance.policy_document ON DELETE CASCADE,
    clause_no text NOT NULL,
    clause_path text,                    -- '4.2.1' hierarchy for precise citation
    heading text,
    clause_text text NOT NULL,
    applies_to text[],                   -- STUDENT, FACULTY, PROGRAMME codes
    UNIQUE (policy_document_id, clause_no)
);
CREATE INDEX idx_clause_text_trgm ON governance.policy_clause USING gin (clause_text gin_trgm_ops);

CREATE TABLE governance.policy_conflict (
    policy_conflict_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    clause_a_id uuid NOT NULL REFERENCES governance.policy_clause,
    clause_b_id uuid NOT NULL REFERENCES governance.policy_clause,
    description text NOT NULL,
    detected_by_agent text,
    detected_at timestamptz NOT NULL DEFAULT now(),
    status text NOT NULL DEFAULT 'OPEN'
           CHECK (status IN ('OPEN','CONFIRMED','RESOLVED','NOT_A_CONFLICT'))
);

CREATE TABLE governance.circular (
    circular_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    circular_no text NOT NULL,
    title text NOT NULL,
    body text,
    document_ref uuid,
    issued_by_user_id uuid REFERENCES identity.app_user,
    issued_on date,
    effective_from date,
    expires_on date,
    supersedes_id uuid REFERENCES governance.circular,
    modifies_policy_clause_id uuid REFERENCES governance.policy_clause,
    audience jsonb NOT NULL,             -- {roles:[], departments:[], batches:[]}
    requires_acknowledgement boolean NOT NULL DEFAULT false,
    status text NOT NULL DEFAULT 'DRAFT'
           CHECK (status IN ('DRAFT','APPROVAL','ISSUED','SUPERSEDED','WITHDRAWN','EXPIRED')),
    UNIQUE (institution_id, circular_no)
);

CREATE TABLE governance.circular_recipient (
    circular_recipient_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    circular_id uuid NOT NULL REFERENCES governance.circular ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES identity.app_user,
    delivered_at timestamptz, read_at timestamptz, acknowledged_at timestamptz,
    UNIQUE (circular_id, user_id)
);

CREATE TABLE governance.committee (
    committee_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    name text NOT NULL,
    committee_type text CHECK (committee_type IN ('STATUTORY','ACADEMIC','ADMINISTRATIVE','ADVISORY','AD_HOC')),
    is_statutory boolean NOT NULL DEFAULT false,
    constituting_authority text,
    mandate text,
    composition_requirement jsonb,       -- {min_members, external_min, student_rep, gender_min}
    quorum smallint,
    meeting_frequency_months smallint,
    constituted_on date,
    valid_until date,
    status text NOT NULL DEFAULT 'ACTIVE'
           CHECK (status IN ('ACTIVE','RECONSTITUTION_DUE','DISSOLVED')),
    UNIQUE (institution_id, name)
);

ALTER TABLE studentlife.grievance
  ADD CONSTRAINT fk_grievance_committee FOREIGN KEY (committee_id) REFERENCES governance.committee;
ALTER TABLE studentlife.disciplinary_case
  ADD CONSTRAINT fk_disc_committee FOREIGN KEY (committee_id) REFERENCES governance.committee;

CREATE TABLE governance.committee_member (
    committee_member_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    committee_id uuid NOT NULL REFERENCES governance.committee ON DELETE CASCADE,
    person_id uuid REFERENCES people.person,
    external_name text, external_affiliation text,
    member_role text NOT NULL CHECK (member_role IN
        ('CHAIRPERSON','CONVENER','MEMBER','MEMBER_SECRETARY','SPECIAL_INVITEE','STUDENT_REPRESENTATIVE')),
    is_external boolean NOT NULL DEFAULT false,
    from_date date NOT NULL, to_date date,
    UNIQUE (committee_id, person_id, from_date)
);

CREATE TABLE governance.committee_compliance (
    committee_compliance_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    committee_id uuid NOT NULL REFERENCES governance.committee ON DELETE CASCADE,
    checked_at timestamptz NOT NULL DEFAULT now(),
    composition_compliant boolean,
    composition_gaps jsonb,
    meetings_due smallint,
    last_meeting_on date,
    tenure_expiring_count smallint,
    status text CHECK (status IN ('COMPLIANT','AT_RISK','NON_COMPLIANT'))
);

CREATE TABLE governance.meeting (
    meeting_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    committee_id uuid NOT NULL REFERENCES governance.committee,
    meeting_no text NOT NULL,
    meeting_date date NOT NULL,
    venue text, mode text,
    agenda_circulated_on date,
    members_present smallint,
    quorum_met boolean,
    status text NOT NULL DEFAULT 'SCHEDULED'
           CHECK (status IN ('SCHEDULED','HELD','ADJOURNED','CANCELLED','MINUTES_APPROVED')),
    minutes_ref uuid,
    UNIQUE (committee_id, meeting_no)
);

CREATE TABLE governance.meeting_attendance (
    meeting_id uuid NOT NULL REFERENCES governance.meeting ON DELETE CASCADE,
    committee_member_id uuid NOT NULL REFERENCES governance.committee_member,
    attended boolean NOT NULL DEFAULT false,
    PRIMARY KEY (meeting_id, committee_member_id)
);

CREATE TABLE governance.meeting_item (
    meeting_item_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id uuid NOT NULL REFERENCES governance.meeting ON DELETE CASCADE,
    item_no text NOT NULL,
    subject text NOT NULL,
    discussion text,
    decision text,
    is_action_required boolean NOT NULL DEFAULT false,
    UNIQUE (meeting_id, item_no)
);

CREATE TABLE governance.compliance_framework (
    compliance_framework_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code text NOT NULL UNIQUE,           -- AICTE, UGC, NBA, NAAC, NIRF, UNIVERSITY
    name text NOT NULL,
    version text,
    effective_from date
);

CREATE TABLE governance.compliance_requirement (
    compliance_requirement_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    compliance_framework_id uuid NOT NULL REFERENCES governance.compliance_framework,
    clause_ref text NOT NULL,
    description text NOT NULL,
    metric_expression text,              -- how it is measured
    data_source text,                    -- schema.table or agent code
    target_value text,
    comparison text CHECK (comparison IN ('GTE','LTE','EQ','RANGE','BOOLEAN')),
    severity text CHECK (severity IN ('CRITICAL','MAJOR','MINOR')),
    lead_time_months smallint,           -- how long a fix realistically takes
    check_frequency text,
    UNIQUE (compliance_framework_id, clause_ref)
);

CREATE TABLE governance.compliance_check (
    compliance_check_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    compliance_requirement_id uuid NOT NULL REFERENCES governance.compliance_requirement,
    scope_type text, scope_id uuid,
    checked_at timestamptz NOT NULL DEFAULT now(),
    actual_value text,
    status text NOT NULL CHECK (status IN ('COMPLIANT','AT_RISK','NON_COMPLIANT','NO_DATA')),
    gap_description text,
    owner_user_id uuid REFERENCES identity.app_user,
    remediation_due date,
    remediation_status text,
    checked_by_agent text
);
CREATE INDEX idx_compliance_status ON governance.compliance_check (status, checked_at DESC);

-- =====================================================================
-- QUALITY : KPI, evidence, feedback, accreditation
-- =====================================================================

CREATE TABLE quality.kpi_definition (
    kpi_definition_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    code text NOT NULL,
    name text NOT NULL,
    domain text NOT NULL CHECK (domain IN
        ('ACADEMIC','STUDENT_OUTCOME','RESEARCH','FACULTY','INFRASTRUCTURE',
         'GOVERNANCE','FINANCE','PLACEMENT','OUTREACH','SAFETY')),
    definition text NOT NULL,
    formula text NOT NULL,
    unit text,
    source_agent text,
    source_query text,
    target_value numeric(14,4),
    direction text CHECK (direction IN ('HIGHER_BETTER','LOWER_BETTER','TARGET_RANGE')),
    frequency text CHECK (frequency IN ('DAILY','WEEKLY','MONTHLY','TERM','ANNUAL')),
    framework_mapping jsonb,             -- {NAAC:'2.6.3', NIRF:'GO', NBA:'4.2'}
    owner_role_id uuid REFERENCES identity.role,
    is_active boolean NOT NULL DEFAULT true,
    UNIQUE (institution_id, code)
);
COMMENT ON TABLE quality.kpi_definition IS
  'The single definition of every institutional metric. Ranking submissions, accreditation '
  'submissions and internal dashboards must all read from here, or the same figure will be '
  'reported three different ways.';

CREATE TABLE quality.kpi_value (
    kpi_value_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_definition_id uuid NOT NULL REFERENCES quality.kpi_definition,
    scope_type text NOT NULL CHECK (scope_type IN ('INSTITUTION','DEPARTMENT','PROGRAMME','BATCH')),
    scope_id uuid,
    period_start date NOT NULL, period_end date NOT NULL,
    value numeric(14,4),
    target_value numeric(14,4),
    previous_value numeric(14,4),
    variance_pct numeric(8,2),
    trend text CHECK (trend IN ('IMPROVING','STABLE','DETERIORATING')),
    status text CHECK (status IN ('ON_TARGET','BELOW_TARGET','ABOVE_TARGET','NO_DATA')),
    computed_at timestamptz NOT NULL DEFAULT now(),
    computed_by_agent text,
    validated_by_user_id uuid REFERENCES identity.app_user,
    validated_at timestamptz,
    UNIQUE (kpi_definition_id, scope_type, scope_id, period_start, period_end)
);
CREATE INDEX idx_kpi_value_period ON quality.kpi_value (kpi_definition_id, period_end DESC);

CREATE TABLE quality.accreditation_criterion (
    accreditation_criterion_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    compliance_framework_id uuid NOT NULL REFERENCES governance.compliance_framework,
    code text NOT NULL,
    parent_id uuid REFERENCES quality.accreditation_criterion,
    title text NOT NULL,
    weightage numeric(6,2),
    evidence_specification text,
    responsible_role_id uuid REFERENCES identity.role,
    UNIQUE (compliance_framework_id, code)
);

CREATE TABLE quality.evidence_item (
    evidence_item_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    accreditation_criterion_id uuid REFERENCES quality.accreditation_criterion,
    title text NOT NULL,
    evidence_type text CHECK (evidence_type IN ('REPORT','CERTIFICATE','MINUTES','PHOTO','DATA_EXPORT','LETTER','PUBLICATION')),
    period_start date, period_end date,
    document_ref uuid,
    source_schema text, source_table text, source_id uuid,   -- traceability
    generated_by_agent text,
    content_hash text,                   -- tamper evidence
    approved_by_user_id uuid REFERENCES identity.app_user,
    approved_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_evidence_criterion ON quality.evidence_item (accreditation_criterion_id, period_end);

CREATE TABLE quality.criterion_readiness (
    criterion_readiness_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    accreditation_criterion_id uuid NOT NULL REFERENCES quality.accreditation_criterion,
    cycle_label text NOT NULL,
    assessed_at timestamptz NOT NULL DEFAULT now(),
    evidence_required smallint, evidence_present smallint,
    readiness_pct numeric(5,2),
    gaps jsonb,
    owner_user_id uuid REFERENCES identity.app_user,
    status text CHECK (status IN ('READY','PARTIAL','GAP','NOT_STARTED')),
    UNIQUE (accreditation_criterion_id, cycle_label, assessed_at)
);

CREATE TABLE quality.feedback_instrument (
    feedback_instrument_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    name text NOT NULL,
    audience text NOT NULL CHECK (audience IN ('STUDENT','FACULTY','ALUMNI','PARENT','EMPLOYER','PEER')),
    purpose text CHECK (purpose IN ('COURSE_FEEDBACK','FACULTY_FEEDBACK','CURRICULUM','FACILITIES','EXIT','EMPLOYER')),
    term_id uuid REFERENCES core.term,
    questions jsonb NOT NULL,
    is_anonymous boolean NOT NULL DEFAULT true,
    opens_on date, closes_on date,
    status text NOT NULL DEFAULT 'DRAFT'
);

CREATE TABLE quality.feedback_response (
    feedback_response_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback_instrument_id uuid NOT NULL REFERENCES quality.feedback_instrument ON DELETE CASCADE,
    respondent_token text,               -- hashed; not linkable back when anonymous
    target_type text CHECK (target_type IN ('COURSE_OFFERING','FACULTY','PROGRAMME','INSTITUTION')),
    target_id uuid,
    answers jsonb NOT NULL,
    submitted_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_feedback_target ON quality.feedback_response (target_type, target_id);

-- =====================================================================
-- KNOWLEDGE : documents, chunks, embeddings, extraction (Agents 53, 64, 65)
-- =====================================================================

CREATE TABLE knowledge.document (
    document_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    title text NOT NULL,
    document_class text NOT NULL CHECK (document_class IN
        ('POLICY','CIRCULAR','SYLLABUS','REGULATION','MINUTES','REPORT','CERTIFICATE',
         'MARKS_CARD','APPLICATION_DOC','MOU','MANUAL','FAQ','OTHER')),
    mime_type text,
    storage_uri text NOT NULL,
    content_hash text NOT NULL,
    page_count smallint,
    language text,
    version text,
    effective_from date, effective_to date,
    supersedes_id uuid REFERENCES knowledge.document,
    owner_role_id uuid REFERENCES identity.role,
    sensitivity text NOT NULL DEFAULT 'NORMAL'
        CHECK (sensitivity IN ('PUBLIC','NORMAL','SENSITIVE','RESTRICTED')),
    is_retrievable_by_agents boolean NOT NULL DEFAULT true,
    review_due_on date,
    uploaded_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (content_hash)
);
COMMENT ON COLUMN knowledge.document.is_retrievable_by_agents IS
  'Retrieval agents may only cite documents where this is true AND sensitivity permits the '
  'requesting role. Question papers, counselling notes and disciplinary files are excluded.';

CREATE TABLE knowledge.document_chunk (
    document_chunk_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id uuid NOT NULL REFERENCES knowledge.document ON DELETE CASCADE,
    seq_no integer NOT NULL,
    heading_path text,                   -- for precise citation, e.g. '4 > 4.2 > 4.2.1'
    page_no smallint,
    chunk_text text NOT NULL,
    token_count smallint,
    UNIQUE (document_id, seq_no)
);
CREATE INDEX idx_chunk_text_trgm ON knowledge.document_chunk USING gin (chunk_text gin_trgm_ops);

-- With pgvector installed, replace embedding with: embedding vector(1536)
-- and add: CREATE INDEX ON knowledge.chunk_embedding USING hnsw (embedding vector_cosine_ops);
CREATE TABLE knowledge.chunk_embedding (
    chunk_embedding_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    document_chunk_id uuid NOT NULL REFERENCES knowledge.document_chunk ON DELETE CASCADE,
    model text NOT NULL,
    dimensions smallint NOT NULL,
    embedding real[] NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (document_chunk_id, model)
);

CREATE TABLE knowledge.extraction_job (
    extraction_job_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id uuid REFERENCES knowledge.document,
    source_uri text,
    detected_document_type text,
    extraction_method text CHECK (extraction_method IN ('TEXT','OCR','TABLE','HYBRID')),
    status text NOT NULL DEFAULT 'QUEUED'
           CHECK (status IN ('QUEUED','RUNNING','COMPLETED','FAILED','NEEDS_REVIEW')),
    started_at timestamptz, finished_at timestamptz,
    error_detail text
);

CREATE TABLE knowledge.extracted_field (
    extracted_field_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    extraction_job_id uuid NOT NULL REFERENCES knowledge.extraction_job ON DELETE CASCADE,
    field_name text NOT NULL,
    raw_value text,
    normalised_value text,
    confidence numeric(4,3) NOT NULL,
    page_no smallint, bounding_box jsonb,
    verification_status text NOT NULL DEFAULT 'AUTO'
           CHECK (verification_status IN ('AUTO','NEEDS_REVIEW','VERIFIED','CORRECTED','REJECTED')),
    corrected_value text,
    verified_by_user_id uuid REFERENCES identity.app_user,
    verified_at timestamptz,
    UNIQUE (extraction_job_id, field_name)
);
COMMENT ON COLUMN knowledge.extracted_field.confidence IS
  'Below the configured threshold the field must be routed to NEEDS_REVIEW and must not '
  'enter an academic or financial record. A transposed digit in a roll number attaches one '
  'student''s result to another.';

SELECT core.add_audit_columns('governance.policy_document');
SELECT core.add_audit_columns('governance.circular');
SELECT core.add_audit_columns('governance.committee');
SELECT core.add_audit_columns('governance.meeting');
SELECT core.add_audit_columns('quality.kpi_definition');
SELECT core.add_audit_columns('quality.kpi_value');
SELECT core.add_audit_columns('knowledge.document');
