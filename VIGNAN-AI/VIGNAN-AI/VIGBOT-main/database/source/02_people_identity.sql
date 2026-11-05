-- =====================================================================
-- 02_people_identity.sql : person supertype, role subtypes, RBAC, audit
-- =====================================================================

-- ---------------------------------------------------------------------
-- PEOPLE. One person row per human being known to the institution.
-- A person may simultaneously be a student, an alumnus and a guest lecturer.
-- Identity resolution across source systems happens here, once.
-- ---------------------------------------------------------------------
CREATE TABLE people.person (
    person_id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id   uuid NOT NULL REFERENCES core.institution,
    full_name        text NOT NULL,
    given_name       text,
    family_name      text,
    date_of_birth    date,
    gender           text CHECK (gender IN ('M','F','O','UNDISCLOSED')),
    primary_email    text,
    primary_phone    text,
    photo_ref        text,
    nationality      text,
    address          jsonb,
    -- demographic attributes used ONLY for statutory reporting and fairness audits
    social_category  text,
    is_differently_abled boolean DEFAULT false,
    mother_tongue    text,
    is_active        boolean NOT NULL DEFAULT true,
    merged_into      uuid REFERENCES people.person   -- duplicate resolution
);
CREATE INDEX idx_person_email ON people.person (lower(primary_email));
CREATE INDEX idx_person_name_trgm ON people.person USING gin (full_name gin_trgm_ops);

COMMENT ON COLUMN people.person.social_category IS
  'Statutory reporting and fairness auditing only. Must never be an input feature to any '
  'agentops model, nor a filter in placement.job matching. See agentops.fairness_audit.';

-- External identifiers from source systems, so identity resolution is auditable
CREATE TABLE people.person_identifier (
    person_identifier_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id      uuid NOT NULL REFERENCES people.person ON DELETE CASCADE,
    system_code    text NOT NULL,          -- 'ERP','BIOMETRIC','LMS','EXAM'
    identifier     text NOT NULL,
    is_primary     boolean NOT NULL DEFAULT false,
    UNIQUE (system_code, identifier)
);

CREATE TABLE people.student (
    student_id       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id        uuid NOT NULL UNIQUE REFERENCES people.person,
    admission_no     text NOT NULL,
    roll_no          text NOT NULL,
    register_no      text,                 -- university register number
    batch_id         uuid NOT NULL,        -- FK added in 03_curriculum
    admission_date   date NOT NULL,
    admission_category text,               -- CONVENER / MANAGEMENT / LATERAL / NRI
    entry_qualification jsonb,             -- board, marks, rank
    current_section_id uuid,               -- FK added in 03_curriculum
    current_year_of_study smallint,
    status           text NOT NULL DEFAULT 'ACTIVE'
                     CHECK (status IN ('ACTIVE','DETAINED','ON_LEAVE','DISCONTINUED',
                                       'TRANSFERRED','GRADUATED','DEBARRED')),
    status_changed_on date,
    graduation_date  date,
    UNIQUE (admission_no),
    UNIQUE (roll_no)
);
CREATE INDEX idx_student_batch ON people.student (batch_id, status);

CREATE TABLE people.guardian (
    guardian_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id   uuid NOT NULL REFERENCES people.student ON DELETE CASCADE,
    name         text NOT NULL,
    relation     text NOT NULL CHECK (relation IN ('FATHER','MOTHER','GUARDIAN','SPOUSE','OTHER')),
    phone        text,
    email        text,
    occupation   text,
    annual_income numeric(12,2),           -- scholarship eligibility
    is_primary_contact boolean NOT NULL DEFAULT false,
    contact_consent boolean NOT NULL DEFAULT true
);

CREATE TABLE people.faculty (
    faculty_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id      uuid NOT NULL UNIQUE REFERENCES people.person,
    employee_no    text NOT NULL UNIQUE,
    department_id  uuid NOT NULL REFERENCES core.department,
    designation    text NOT NULL,          -- ASSISTANT_PROFESSOR / ASSOCIATE / PROFESSOR
    cadre          text,                   -- used by governance.compliance (cadre ratio)
    employment_type text NOT NULL DEFAULT 'REGULAR'
                    CHECK (employment_type IN ('REGULAR','CONTRACT','ADJUNCT','VISITING','EMERITUS')),
    highest_qualification text,
    is_phd_holder  boolean NOT NULL DEFAULT false,
    phd_awarded_on date,
    date_of_joining date NOT NULL,
    date_of_leaving date,
    is_research_supervisor boolean NOT NULL DEFAULT false,
    status         text NOT NULL DEFAULT 'ACTIVE'
                   CHECK (status IN ('ACTIVE','ON_LEAVE','DEPUTED','RESIGNED','RETIRED'))
);
CREATE INDEX idx_faculty_dept ON people.faculty (department_id, status);

ALTER TABLE core.department
  ADD CONSTRAINT fk_dept_hod FOREIGN KEY (hod_faculty_id) REFERENCES people.faculty;

CREATE TABLE people.faculty_expertise (
    faculty_expertise_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id   uuid NOT NULL REFERENCES people.faculty ON DELETE CASCADE,
    area         text NOT NULL,
    proficiency  smallint CHECK (proficiency BETWEEN 1 AND 5),
    evidence_source text CHECK (evidence_source IN
                 ('DECLARED','QUALIFICATION','PUBLICATION','CERTIFICATION','TEACHING_HISTORY')),
    UNIQUE (faculty_id, area, evidence_source)
);

CREATE TABLE people.staff (
    staff_id      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id     uuid NOT NULL UNIQUE REFERENCES people.person,
    employee_no   text NOT NULL UNIQUE,
    department_id uuid REFERENCES core.department,
    designation   text NOT NULL,
    category      text CHECK (category IN ('TECHNICAL','ADMINISTRATIVE','SUPPORT')),
    date_of_joining date NOT NULL,
    status        text NOT NULL DEFAULT 'ACTIVE'
);

-- =====================================================================
-- IDENTITY : users, roles, permissions, scoped access, audit log
-- This is the table set that enforces every access guardrail described
-- in the agent specifications. Access is decided here, not in prompts.
-- =====================================================================

CREATE TABLE identity.app_user (
    user_id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id      uuid UNIQUE REFERENCES people.person,
    username       text NOT NULL UNIQUE,
    email          text NOT NULL,
    auth_provider  text NOT NULL DEFAULT 'SSO',
    is_active      boolean NOT NULL DEFAULT true,
    is_service_account boolean NOT NULL DEFAULT false,
    last_login_at  timestamptz
);

CREATE TABLE identity.role (
    role_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code        text NOT NULL UNIQUE,   -- STUDENT, FACULTY, MENTOR, HOD, DEAN, COE,
                                        -- IQAC, PLACEMENT, ACCOUNTS, COUNSELLOR, ADMIN
    name        text NOT NULL,
    description text,
    is_system   boolean NOT NULL DEFAULT false
);

CREATE TABLE identity.permission (
    permission_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code          text NOT NULL UNIQUE,  -- 'attendance.read','marks.write','counselling.read'
    resource      text NOT NULL,
    action        text NOT NULL CHECK (action IN ('READ','WRITE','APPROVE','DELETE','EXPORT')),
    sensitivity   text NOT NULL DEFAULT 'NORMAL'
                  CHECK (sensitivity IN ('PUBLIC','NORMAL','SENSITIVE','RESTRICTED'))
);

CREATE TABLE identity.role_permission (
    role_id       uuid NOT NULL REFERENCES identity.role ON DELETE CASCADE,
    permission_id uuid NOT NULL REFERENCES identity.permission ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- A role assignment is always scoped. Scope determines which ROWS the user sees.
-- Faculty see their own offerings; HoD sees their department; Dean sees the institution.
CREATE TABLE identity.user_role (
    user_role_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      uuid NOT NULL REFERENCES identity.app_user ON DELETE CASCADE,
    role_id      uuid NOT NULL REFERENCES identity.role,
    scope_type   text NOT NULL DEFAULT 'SELF'
                 CHECK (scope_type IN ('SELF','SECTION','COURSE_OFFERING','PROGRAMME',
                                       'DEPARTMENT','CAMPUS','INSTITUTION')),
    scope_id     uuid,                  -- null when scope_type = SELF or INSTITUTION
    valid_from   date NOT NULL DEFAULT current_date,
    valid_to     date,
    granted_by   uuid REFERENCES identity.app_user,
    UNIQUE (user_id, role_id, scope_type, scope_id, valid_from)
);
CREATE INDEX idx_user_role_lookup ON identity.user_role (user_id, valid_from, valid_to);

-- Delegation, e.g. HoD delegating approval during leave. Time-boxed by design.
CREATE TABLE identity.delegation (
    delegation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    from_user_id  uuid NOT NULL REFERENCES identity.app_user,
    to_user_id    uuid NOT NULL REFERENCES identity.app_user,
    role_id       uuid NOT NULL REFERENCES identity.role,
    reason        text,
    valid_from    timestamptz NOT NULL,
    valid_to      timestamptz NOT NULL,
    CHECK (valid_to > valid_from)
);

-- Append-only. No UPDATE or DELETE grant is ever issued on this table.
CREATE TABLE identity.audit_log (
    audit_id     bigserial,
    occurred_at  timestamptz NOT NULL DEFAULT now(),
    actor_user_id uuid,
    actor_role   text,
    on_behalf_of_agent text,             -- agentops.agent.code when an agent acted
    action       text NOT NULL,          -- READ / CREATE / UPDATE / DELETE / EXPORT / APPROVE
    object_schema text NOT NULL,
    object_table text NOT NULL,
    object_id    uuid,
    subject_person_id uuid,              -- whose data was touched
    before_value jsonb,
    after_value  jsonb,
    request_id   uuid,
    source_ip    inet,
    justification text,
    PRIMARY KEY (audit_id, occurred_at)
) PARTITION BY RANGE (occurred_at);

CREATE TABLE identity.audit_log_2026 PARTITION OF identity.audit_log
  FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE identity.audit_log_2027 PARTITION OF identity.audit_log
  FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');

CREATE INDEX idx_audit_subject ON identity.audit_log (subject_person_id, occurred_at DESC);
CREATE INDEX idx_audit_actor   ON identity.audit_log (actor_user_id, occurred_at DESC);

-- Data subject rights: access and correction requests (DPDP Act readiness)
CREATE TABLE identity.data_request (
    data_request_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id     uuid NOT NULL REFERENCES people.person,
    request_type  text NOT NULL CHECK (request_type IN
                  ('ACCESS','CORRECTION','ERASURE','CONSENT_WITHDRAWAL','GRIEVANCE')),
    details       text,
    status        text NOT NULL DEFAULT 'OPEN'
                  CHECK (status IN ('OPEN','IN_PROGRESS','FULFILLED','REJECTED')),
    raised_at     timestamptz NOT NULL DEFAULT now(),
    due_by        date,
    resolved_at   timestamptz,
    resolution    text
);

-- Purpose-bound consent record
CREATE TABLE identity.consent (
    consent_id   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id    uuid NOT NULL REFERENCES people.person ON DELETE CASCADE,
    purpose_code text NOT NULL,          -- 'ALUMNI_CONTACT','PUBLICITY_PHOTO','PARENT_SHARING'
    is_granted   boolean NOT NULL,
    granted_at   timestamptz NOT NULL DEFAULT now(),
    withdrawn_at timestamptz,
    evidence_ref text,
    UNIQUE (person_id, purpose_code, granted_at)
);

SELECT core.add_audit_columns('people.person');
SELECT core.add_audit_columns('people.student');
SELECT core.add_audit_columns('people.faculty');
SELECT core.add_audit_columns('identity.app_user');
SELECT core.add_audit_columns('identity.user_role');
