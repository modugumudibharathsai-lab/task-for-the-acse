-- =====================================================================
-- 08_studentlife_placement_hr.sql : Agents 44-52, 58-61
-- =====================================================================

CREATE TABLE studentlife.mentorship (
    mentorship_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  uuid NOT NULL REFERENCES people.student,
    mentor_faculty_id uuid NOT NULL REFERENCES people.faculty,
    from_date   date NOT NULL, to_date date,
    is_current  boolean NOT NULL DEFAULT true,
    reallocation_reason text,
    UNIQUE (student_id, mentor_faculty_id, from_date)
);
CREATE INDEX idx_mentorship_mentor ON studentlife.mentorship (mentor_faculty_id) WHERE is_current;

CREATE TABLE studentlife.mentor_meeting (
    mentor_meeting_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    mentorship_id uuid NOT NULL REFERENCES studentlife.mentorship ON DELETE CASCADE,
    scheduled_on date, held_on date,
    mode        text CHECK (mode IN ('IN_PERSON','PHONE','ONLINE')),
    brief_ref   uuid,                    -- agentops.agent_output: pre-meeting brief
    academic_notes text,
    attendance_notes text,
    career_notes text,
    personal_notes text,                 -- restricted; see RLS
    escalated_to text CHECK (escalated_to IN ('NONE','HOD','COUNSELLING','ACCOUNTS','PLACEMENT')),
    status      text NOT NULL DEFAULT 'SCHEDULED'
                CHECK (status IN ('SCHEDULED','HELD','MISSED','CANCELLED'))
);

-- Generic action item, reused by mentoring, committees, compliance, attainment
CREATE TABLE studentlife.action_item (
    action_item_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_schema text NOT NULL,
    source_table  text NOT NULL,
    source_id     uuid NOT NULL,
    description   text NOT NULL,
    owner_user_id uuid REFERENCES identity.app_user,
    due_date      date,
    priority      text CHECK (priority IN ('LOW','MEDIUM','HIGH','URGENT')),
    status        text NOT NULL DEFAULT 'OPEN'
                  CHECK (status IN ('OPEN','IN_PROGRESS','COMPLETED','DEFERRED','DROPPED')),
    closed_on     date,
    closure_note  text
);
CREATE INDEX idx_action_owner ON studentlife.action_item (owner_user_id, status, due_date);
CREATE INDEX idx_action_source ON studentlife.action_item (source_table, source_id);

CREATE TABLE studentlife.grievance (
    grievance_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    grievance_no text NOT NULL UNIQUE,
    student_id  uuid REFERENCES people.student,     -- null when anonymous
    is_anonymous boolean NOT NULL DEFAULT false,
    category    text NOT NULL CHECK (category IN
                ('ACADEMIC','EXAMINATION','FEE','HOSTEL','TRANSPORT','INFRASTRUCTURE',
                 'FACULTY_CONDUCT','HARASSMENT','DISCRIMINATION','RAGGING','SAFETY','OTHER')),
    severity    text NOT NULL DEFAULT 'NORMAL' CHECK (severity IN ('LOW','NORMAL','HIGH','CRITICAL')),
    is_statutory_route boolean NOT NULL DEFAULT false,
    description text NOT NULL,
    submitted_at timestamptz NOT NULL DEFAULT now(),
    submitted_via text,
    assigned_to_user_id uuid REFERENCES identity.app_user,
    committee_id uuid,                    -- FK added in governance
    sla_due_at  timestamptz,
    status      text NOT NULL DEFAULT 'RECEIVED'
                CHECK (status IN ('RECEIVED','ASSIGNED','IN_PROGRESS','RESOLVED','CLOSED','APPEALED','ESCALATED')),
    resolved_at timestamptz,
    resolution  text,
    satisfaction_rating smallint CHECK (satisfaction_rating BETWEEN 1 AND 5)
);
CREATE INDEX idx_grievance_sla ON studentlife.grievance (status, sla_due_at);
COMMENT ON COLUMN studentlife.grievance.is_statutory_route IS
  'HARASSMENT, DISCRIMINATION, RAGGING and SAFETY bypass normal routing and go directly '
  'to the statutory committee with a shortened SLA. Never triaged autonomously.';

CREATE TABLE studentlife.grievance_event (
    grievance_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    grievance_id uuid NOT NULL REFERENCES studentlife.grievance ON DELETE CASCADE,
    occurred_at timestamptz NOT NULL DEFAULT now(),
    event_type  text NOT NULL CHECK (event_type IN
                ('SUBMITTED','ACKNOWLEDGED','ASSIGNED','REASSIGNED','COMMENT',
                 'ESCALATED','RESOLVED','APPEALED','CLOSED')),
    actor_user_id uuid REFERENCES identity.app_user,
    notes       text
);

CREATE TABLE studentlife.disciplinary_case (
    disciplinary_case_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    case_no     text NOT NULL UNIQUE,
    student_id  uuid NOT NULL REFERENCES people.student,
    offence_category text NOT NULL,
    incident_date date NOT NULL,
    incident_location text,
    reported_by_user_id uuid REFERENCES identity.app_user,
    description text NOT NULL,
    committee_id uuid,
    decision    text,
    sanction    text,
    decided_on  date,
    appeal_status text,
    status      text NOT NULL DEFAULT 'REPORTED'
                CHECK (status IN ('REPORTED','NOTICE_ISSUED','HEARING','DECIDED','APPEALED','CLOSED','EXPUNGED')),
    retention_until date NOT NULL
);
COMMENT ON TABLE studentlife.disciplinary_case IS
  'RESTRICTED. Never surfaced in general student profile views, placement views or faculty '
  'views. retention_until is enforced by a scheduled expunge job. The platform never '
  'determines guilt or recommends sanction; it records process compliance only.';

CREATE TABLE studentlife.disciplinary_step (
    disciplinary_step_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    disciplinary_case_id uuid NOT NULL REFERENCES studentlife.disciplinary_case ON DELETE CASCADE,
    step_name   text NOT NULL,           -- NOTICE, RESPONSE_WINDOW, HEARING, DECISION
    required_by_policy boolean NOT NULL DEFAULT true,
    due_date    date, completed_on date,
    evidence_ref uuid,
    status      text NOT NULL DEFAULT 'PENDING'
                CHECK (status IN ('PENDING','COMPLETED','SKIPPED','OVERDUE'))
);

CREATE TABLE studentlife.achievement (
    achievement_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  uuid NOT NULL REFERENCES people.student,
    category    text NOT NULL CHECK (category IN
                ('TECHNICAL_COMPETITION','HACKATHON','PAPER_PRESENTATION','PUBLICATION',
                 'PATENT','SPORTS','CULTURAL','ENTREPRENEURSHIP','SOCIAL_SERVICE','SCHOLARSHIP_AWARD')),
    title       text NOT NULL,
    organiser   text,
    level       text CHECK (level IN ('INSTITUTIONAL','UNIVERSITY','DISTRICT','STATE','NATIONAL','INTERNATIONAL')),
    position    text,
    event_date  date,
    evidence_ref uuid,
    extraction_confidence numeric(4,3),
    verification_status text NOT NULL DEFAULT 'PENDING'
                CHECK (verification_status IN ('PENDING','VERIFIED','REJECTED','UNVERIFIABLE')),
    verified_by_faculty_id uuid REFERENCES people.faculty,
    verified_at timestamptz,
    weight_points numeric(6,2)
);
CREATE INDEX idx_achievement_student ON studentlife.achievement (student_id, verification_status);

CREATE TABLE studentlife.certification_catalog (
    certification_catalog_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL, provider text NOT NULL,
    domain text, level text CHECK (level IN ('FOUNDATION','ASSOCIATE','PROFESSIONAL','EXPERT')),
    typical_cost numeric(10,2), duration_hours smallint, validity_months smallint,
    verification_url_pattern text,
    industry_demand_score numeric(5,2),
    is_recommended boolean NOT NULL DEFAULT false,
    UNIQUE (provider, name)
);

CREATE TABLE studentlife.student_certification (
    student_certification_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  uuid NOT NULL REFERENCES people.student,
    certification_catalog_id uuid REFERENCES studentlife.certification_catalog,
    name text NOT NULL, provider text,
    credential_id text, credential_url text,
    issued_on date, expires_on date,
    score numeric(6,2),
    evidence_ref uuid,
    verification_status text NOT NULL DEFAULT 'PENDING'
                CHECK (verification_status IN ('PENDING','VERIFIED','REJECTED','UNVERIFIABLE')),
    mapped_course_version_id uuid REFERENCES curriculum.course_version
);

-- =====================================================================
-- CONFIDENTIAL : counselling and health. Separate schema, separate grants.
-- =====================================================================
CREATE TABLE confidential.counselling_case (
    counselling_case_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  uuid NOT NULL REFERENCES people.student,
    referral_source text NOT NULL CHECK (referral_source IN ('SELF','MENTOR','FACULTY','AGENT_FLAG','PARENT','PEER')),
    referred_by_user_id uuid REFERENCES identity.app_user,
    opened_at   timestamptz NOT NULL DEFAULT now(),
    urgency     text NOT NULL CHECK (urgency IN ('ROUTINE','PRIORITY','URGENT','CRISIS')),
    counsellor_user_id uuid REFERENCES identity.app_user,
    status      text NOT NULL DEFAULT 'OPEN'
                CHECK (status IN ('OPEN','IN_PROGRESS','REFERRED_EXTERNAL','CLOSED')),
    closed_at   timestamptz
);

CREATE TABLE confidential.counselling_note (
    counselling_note_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    counselling_case_id uuid NOT NULL REFERENCES confidential.counselling_case ON DELETE CASCADE,
    counsellor_user_id uuid NOT NULL REFERENCES identity.app_user,
    session_at  timestamptz NOT NULL DEFAULT now(),
    note_encrypted bytea NOT NULL,       -- application-layer encryption
    next_session_on date
);

CREATE TABLE confidential.crisis_escalation (
    crisis_escalation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  uuid NOT NULL REFERENCES people.student,
    counselling_case_id uuid REFERENCES confidential.counselling_case,
    detected_at timestamptz NOT NULL DEFAULT now(),
    detected_by text NOT NULL,           -- agent code or user id
    channel_used text NOT NULL,
    escalated_to_user_id uuid NOT NULL REFERENCES identity.app_user,
    acknowledged_at timestamptz,
    response_time_seconds integer,
    outcome     text
);
COMMENT ON TABLE confidential.crisis_escalation IS
  'Any indication of self-harm or risk to safety writes here AND pages a named human '
  'immediately. Never queued, never batched, never handled conversationally by an agent. '
  'response_time_seconds is monitored as a safety KPI.';

CREATE TABLE confidential.academic_accommodation (
    academic_accommodation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  uuid NOT NULL REFERENCES people.student,
    accommodation_type text NOT NULL,    -- DEFERRAL, EXTRA_TIME, ATTENDANCE_RELAXATION
    course_offering_id uuid REFERENCES academics.course_offering,
    valid_from date, valid_to date,
    approved_by uuid REFERENCES identity.app_user,
    -- reason deliberately NOT stored here; it lives in the counselling case
    status text NOT NULL DEFAULT 'ACTIVE'
);

-- =====================================================================
-- PLACEMENT : Agents 49-52
-- =====================================================================

CREATE TABLE placement.company (
    company_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    name text NOT NULL, sector text, website text,
    tier text CHECK (tier IN ('SUPER_DREAM','DREAM','CORE','MASS','STARTUP')),
    hr_contact_name text, hr_contact_email text, hr_contact_phone text,
    industry_partner_id uuid REFERENCES engagement.industry_partner,
    alumni_connect_person_id uuid REFERENCES people.person,
    UNIQUE (institution_id, name)
);

CREATE TABLE placement.job_opening (
    job_opening_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id uuid NOT NULL REFERENCES placement.company,
    academic_year_id uuid NOT NULL REFERENCES core.academic_year,
    role_title text NOT NULL,
    opening_type text NOT NULL CHECK (opening_type IN ('FULL_TIME','INTERNSHIP','INTERN_PPO','PART_TIME')),
    job_description text,
    required_skills text[], preferred_skills text[],
    eligibility jsonb NOT NULL,          -- {min_cgpa, max_backlogs, programmes[], gap_years}
    ctc_min numeric(12,2), ctc_max numeric(12,2),
    locations text[],
    positions_open smallint,
    drive_date date, application_deadline date,
    status text NOT NULL DEFAULT 'ANNOUNCED'
           CHECK (status IN ('ANNOUNCED','OPEN','CLOSED','DRIVE_COMPLETED','CANCELLED'))
);
COMMENT ON COLUMN placement.job_opening.eligibility IS
  'Eligibility is a hard filter and must reference academic criteria only. Filtering or '
  'ranking on gender, caste, religion or region — directly or by proxy — is prohibited '
  'and audited by agentops.fairness_audit.';

CREATE TABLE placement.drive_application (
    drive_application_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    job_opening_id uuid NOT NULL REFERENCES placement.job_opening ON DELETE CASCADE,
    student_id uuid NOT NULL REFERENCES people.student,
    applied_at timestamptz NOT NULL DEFAULT now(),
    match_score numeric(5,2),
    match_reason text,
    current_round text,
    status text NOT NULL DEFAULT 'APPLIED'
           CHECK (status IN ('APPLIED','SHORTLISTED','IN_PROCESS','SELECTED','REJECTED','WITHDRAWN','NOT_ELIGIBLE')),
    UNIQUE (job_opening_id, student_id)
);

CREATE TABLE placement.offer (
    offer_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id uuid NOT NULL REFERENCES people.student,
    company_id uuid NOT NULL REFERENCES placement.company,
    job_opening_id uuid REFERENCES placement.job_opening,
    role_title text, ctc numeric(12,2), location text,
    offer_date date NOT NULL,
    is_ppo boolean NOT NULL DEFAULT false,
    joining_date date,
    status text NOT NULL DEFAULT 'OFFERED'
           CHECK (status IN ('OFFERED','ACCEPTED','DECLINED','REVOKED','JOINED'))
);
CREATE INDEX idx_offer_student ON placement.offer (student_id, offer_date);

CREATE TABLE placement.readiness_assessment (
    readiness_assessment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id uuid NOT NULL REFERENCES people.student,
    assessed_on date NOT NULL,
    dimension text NOT NULL CHECK (dimension IN
              ('ACADEMIC','TECHNICAL','APTITUDE','COMMUNICATION','PROJECT_EXPERIENCE','CERTIFICATION','OVERALL')),
    score numeric(5,2),
    max_score numeric(5,2) DEFAULT 100,
    evidence jsonb,
    computed_by_agent text,
    UNIQUE (student_id, assessed_on, dimension)
);

CREATE TABLE placement.readiness_summary (
    readiness_summary_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id uuid NOT NULL REFERENCES people.student,
    assessed_on date NOT NULL,
    overall_score numeric(5,2),
    readiness_band text CHECK (readiness_band IN ('READY','NEAR_READY','NEEDS_PREPARATION')),
    qualifying_company_count smallint,   -- the figure students actually respond to
    binding_constraint text,             -- the single dimension unlocking most openings
    preparation_plan jsonb,
    UNIQUE (student_id, assessed_on)
);

CREATE TABLE placement.internship (
    internship_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id uuid NOT NULL REFERENCES people.student,
    company_id uuid REFERENCES placement.company,
    company_name text NOT NULL,
    domain text,
    from_date date NOT NULL, to_date date NOT NULL,
    mode text CHECK (mode IN ('ONSITE','REMOTE','HYBRID')),
    stipend numeric(10,2),
    source text CHECK (source IN ('INSTITUTION','STUDENT_SOURCED','ALUMNI','MOU')),
    legitimacy_verified boolean NOT NULL DEFAULT false,
    verified_by_user_id uuid REFERENCES identity.app_user,
    faculty_mentor_id uuid REFERENCES people.faculty,
    industry_supervisor text,
    is_credit_bearing boolean NOT NULL DEFAULT false,
    course_version_id uuid REFERENCES curriculum.course_version,
    final_grade text,
    converted_to_ppo boolean NOT NULL DEFAULT false,
    status text NOT NULL DEFAULT 'PROPOSED'
           CHECK (status IN ('PROPOSED','APPROVED','ONGOING','COMPLETED','DISCONTINUED')),
    CHECK (to_date >= from_date)
);

CREATE TABLE placement.internship_evaluation (
    internship_evaluation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    internship_id uuid NOT NULL REFERENCES placement.internship ON DELETE CASCADE,
    evaluator_type text NOT NULL CHECK (evaluator_type IN ('INDUSTRY','FACULTY_MENTOR','PANEL')),
    evaluation_stage text CHECK (evaluation_stage IN ('MID_TERM','FINAL','REPORT','PRESENTATION')),
    score numeric(5,2), max_score numeric(5,2),
    criteria_scores jsonb,
    remarks text,
    evaluated_on date
);

CREATE TABLE placement.alumni (
    alumni_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id uuid NOT NULL UNIQUE REFERENCES people.person,
    student_id uuid REFERENCES people.student,
    programme_id uuid REFERENCES curriculum.programme,
    graduation_year smallint NOT NULL,
    current_organisation text, current_designation text, sector text,
    location text, linkedin_url text,
    higher_study_institution text,
    outcome_category text CHECK (outcome_category IN ('EMPLOYED','HIGHER_STUDIES','ENTREPRENEUR','OTHER','UNKNOWN')),
    engagement_level text CHECK (engagement_level IN ('ACTIVE','OCCASIONAL','DORMANT','UNREACHABLE')),
    contact_consent boolean NOT NULL DEFAULT false,
    publicity_consent boolean NOT NULL DEFAULT false,
    last_updated_on date, updated_via text
);
CREATE INDEX idx_alumni_year ON placement.alumni (graduation_year, programme_id);

CREATE TABLE placement.alumni_contribution (
    alumni_contribution_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    alumni_id uuid NOT NULL REFERENCES placement.alumni ON DELETE CASCADE,
    contribution_type text NOT NULL CHECK (contribution_type IN
              ('GUEST_LECTURE','MENTORING','PLACEMENT_REFERRAL','INTERNSHIP_HOST',
               'FINANCIAL','EQUIPMENT','SCHOLARSHIP_FUNDING','COLLABORATION')),
    description text,
    contributed_on date,
    value numeric(12,2),
    acknowledged boolean NOT NULL DEFAULT false
);

-- =====================================================================
-- HR : workload, appraisal, leave (Agents 58-61)
-- =====================================================================

CREATE TABLE hr.workload_norm (
    workload_norm_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    designation text NOT NULL,
    min_hours numeric(5,2), expected_hours numeric(5,2), max_hours numeric(5,2),
    activity_weights jsonb NOT NULL,     -- {LECTURE:1.0, LAB:0.5, PROJECT_GUIDE:0.25, ...}
    effective_from date NOT NULL, effective_to date,
    UNIQUE (institution_id, designation, effective_from)
);

CREATE TABLE hr.admin_role_assignment (
    admin_role_assignment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id uuid NOT NULL REFERENCES people.faculty,
    role_name text NOT NULL,             -- HOD, NBA_COORDINATOR, EXAM_CELL, WARDEN
    workload_weight numeric(5,2),
    from_date date NOT NULL, to_date date,
    order_ref text
);

CREATE TABLE hr.faculty_workload (
    faculty_workload_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id uuid NOT NULL REFERENCES people.faculty,
    term_id uuid NOT NULL REFERENCES core.term,
    computed_at timestamptz NOT NULL DEFAULT now(),
    lecture_hours numeric(6,2) DEFAULT 0,
    lab_hours numeric(6,2) DEFAULT 0,
    tutorial_hours numeric(6,2) DEFAULT 0,
    supervision_load numeric(6,2) DEFAULT 0,
    admin_load numeric(6,2) DEFAULT 0,
    research_load numeric(6,2) DEFAULT 0,
    total_weighted_load numeric(6,2),
    norm_expected numeric(6,2),
    variance_pct numeric(6,2),
    status text CHECK (status IN ('UNDERLOAD','WITHIN_NORM','OVERLOAD','SEVERE_OVERLOAD')),
    UNIQUE (faculty_id, term_id, computed_at)
);

CREATE TABLE hr.appraisal_cycle (
    appraisal_cycle_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    academic_year_id uuid NOT NULL REFERENCES core.academic_year,
    rubric jsonb NOT NULL,               -- dimensions, weights, bands (published in advance)
    rubric_published_on date,
    opens_on date, closes_on date,
    status text NOT NULL DEFAULT 'PLANNED'
           CHECK (status IN ('PLANNED','OPEN','REVIEW','CLOSED')),
    UNIQUE (institution_id, academic_year_id)
);

CREATE TABLE hr.appraisal_record (
    appraisal_record_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    appraisal_cycle_id uuid NOT NULL REFERENCES hr.appraisal_cycle,
    faculty_id uuid NOT NULL REFERENCES people.faculty,
    auto_populated jsonb,                -- system-derived evidence per dimension
    faculty_additions jsonb,
    dimension_scores jsonb,
    context_factors jsonb,               -- load, course difficulty, admin burden
    total_score numeric(6,2),
    hod_remarks text,
    faculty_response text,
    contested boolean NOT NULL DEFAULT false,
    contest_resolution text,
    agreed_goals jsonb,
    status text NOT NULL DEFAULT 'DRAFT'
           CHECK (status IN ('DRAFT','FACULTY_REVIEW','HOD_REVIEW','FINALISED','CONTESTED')),
    UNIQUE (appraisal_cycle_id, faculty_id)
);
COMMENT ON TABLE hr.appraisal_record IS
  'Every computed score must be traceable to auto_populated evidence and contestable via '
  'faculty_response/contested. The score informs a human decision; it never is one. '
  'Student feedback alone must never drive a performance conclusion.';

CREATE TABLE hr.development_plan (
    development_plan_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id uuid NOT NULL REFERENCES people.faculty,
    appraisal_cycle_id uuid REFERENCES hr.appraisal_cycle,
    competency_area text NOT NULL,
    gap_description text,
    recommended_action text NOT NULL,
    action_type text CHECK (action_type IN ('FDP','CERTIFICATION','MOOC','INDUSTRY_IMMERSION','PHD','MENTORING','CONFERENCE')),
    target_date date,
    event_id uuid REFERENCES engagement.event,
    status text NOT NULL DEFAULT 'PROPOSED'
           CHECK (status IN ('PROPOSED','AGREED','IN_PROGRESS','COMPLETED','APPLIED','DROPPED')),
    application_evidence text
);

CREATE TABLE hr.leave_type (
    leave_type_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    code text NOT NULL, name text NOT NULL,
    annual_entitlement numeric(5,1),
    is_carry_forward boolean DEFAULT false,
    requires_document boolean DEFAULT false,
    is_health_related boolean NOT NULL DEFAULT false,
    UNIQUE (institution_id, code)
);

CREATE TABLE hr.leave_balance (
    faculty_id uuid NOT NULL REFERENCES people.faculty,
    leave_type_id uuid NOT NULL REFERENCES hr.leave_type,
    year smallint NOT NULL,
    entitled numeric(5,1) NOT NULL DEFAULT 0,
    availed numeric(5,1) NOT NULL DEFAULT 0,
    balance numeric(5,1) GENERATED ALWAYS AS (entitled - availed) STORED,
    PRIMARY KEY (faculty_id, leave_type_id, year)
);

CREATE TABLE hr.faculty_leave (
    faculty_leave_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id uuid NOT NULL REFERENCES people.faculty,
    leave_type_id uuid NOT NULL REFERENCES hr.leave_type,
    from_date date NOT NULL, to_date date NOT NULL,
    days numeric(5,1) NOT NULL,
    reason_restricted text,              -- medical reason: restricted visibility
    document_ref uuid,
    affected_sessions jsonb,             -- computed class/exam/committee impact
    substitution_arranged boolean NOT NULL DEFAULT false,
    status text NOT NULL DEFAULT 'APPLIED'
           CHECK (status IN ('APPLIED','RECOMMENDED','APPROVED','REJECTED','CANCELLED','AVAILED')),
    approved_by uuid REFERENCES identity.app_user,
    approved_at timestamptz,
    CHECK (to_date >= from_date)
);
COMMENT ON COLUMN hr.faculty_leave.reason_restricted IS
  'Health information. Visible to HR and the approving authority only. Must never appear '
  'in the substitution notification sent to students or colleagues.';

CREATE TABLE hr.class_substitution (
    class_substitution_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    class_session_id uuid NOT NULL REFERENCES academics.class_session,
    original_faculty_id uuid NOT NULL REFERENCES people.faculty,
    substitute_faculty_id uuid REFERENCES people.faculty,
    faculty_leave_id uuid REFERENCES hr.faculty_leave,
    arrangement_type text CHECK (arrangement_type IN ('SUBSTITUTE','COMPENSATION_CLASS','SELF_STUDY','CANCELLED')),
    compensation_session_id uuid REFERENCES academics.class_session,
    status text NOT NULL DEFAULT 'PROPOSED'
           CHECK (status IN ('PROPOSED','CONFIRMED','COMPLETED','NOT_COMPENSATED'))
);

CREATE TABLE hr.faculty_attendance (
    faculty_attendance_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id uuid NOT NULL REFERENCES people.faculty,
    attendance_date date NOT NULL,
    first_in time, last_out time,
    source text CHECK (source IN ('BIOMETRIC','MANUAL','RFID')),
    status text CHECK (status IN ('PRESENT','ABSENT','ON_LEAVE','ON_DUTY','HOLIDAY','UNEXPLAINED')),
    reconciled_with_leave boolean NOT NULL DEFAULT false,
    UNIQUE (faculty_id, attendance_date)
);

SELECT core.add_audit_columns('studentlife.grievance');
SELECT core.add_audit_columns('studentlife.disciplinary_case');
SELECT core.add_audit_columns('studentlife.achievement');
SELECT core.add_audit_columns('placement.job_opening');
SELECT core.add_audit_columns('placement.offer');
SELECT core.add_audit_columns('placement.internship');
SELECT core.add_audit_columns('placement.alumni');
SELECT core.add_audit_columns('hr.appraisal_record');
SELECT core.add_audit_columns('hr.faculty_leave');
SELECT core.add_audit_columns('confidential.counselling_case');
