-- =====================================================================
-- 04_academics_attendance.sql
-- Serves Agents 3, 4, 5, 6, 7, 11, 16
--
-- KEY DESIGN DECISION: course_offering is the central grain of the whole
-- platform. It is one course_version, taught in one term, to one section.
-- Allocation, timetable, lesson plan, attendance, marks and CO attainment
-- all hang off it. Get this grain wrong and every downstream number is
-- ambiguous.
-- =====================================================================

CREATE TABLE academics.course_offering (
    course_offering_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_version_id  uuid NOT NULL REFERENCES curriculum.course_version,
    term_id            uuid NOT NULL REFERENCES core.term,
    section_id         uuid NOT NULL REFERENCES curriculum.section,
    department_id      uuid NOT NULL REFERENCES core.department,
    enrolled_count     smallint,
    delivery_mode      text NOT NULL DEFAULT 'OFFLINE'
                       CHECK (delivery_mode IN ('OFFLINE','ONLINE','BLENDED')),
    status             text NOT NULL DEFAULT 'PLANNED'
                       CHECK (status IN ('PLANNED','ACTIVE','COMPLETED','CANCELLED')),
    UNIQUE (course_version_id, term_id, section_id)
);
CREATE INDEX idx_offering_term ON academics.course_offering (term_id, department_id);

-- Which students are actually registered in this offering. Necessary because
-- electives, backlog re-registration and lateral entry all break the
-- assumption that section membership equals course registration.
CREATE TABLE academics.student_registration (
    student_registration_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_offering_id uuid NOT NULL REFERENCES academics.course_offering ON DELETE CASCADE,
    student_id     uuid NOT NULL REFERENCES people.student,
    registration_type text NOT NULL DEFAULT 'REGULAR'
                   CHECK (registration_type IN ('REGULAR','REPEAT','IMPROVEMENT','AUDIT','SUPPLEMENTARY')),
    attempt_no     smallint NOT NULL DEFAULT 1,
    registered_on  date NOT NULL DEFAULT current_date,
    status         text NOT NULL DEFAULT 'REGISTERED'
                   CHECK (status IN ('REGISTERED','WITHDRAWN','DETAINED','COMPLETED')),
    UNIQUE (course_offering_id, student_id)
);
CREATE INDEX idx_reg_student ON academics.student_registration (student_id, status);

CREATE TABLE academics.faculty_allocation (
    faculty_allocation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_offering_id uuid NOT NULL REFERENCES academics.course_offering ON DELETE CASCADE,
    faculty_id     uuid NOT NULL REFERENCES people.faculty,
    lab_batch_id   uuid REFERENCES curriculum.lab_batch,   -- lab allocations are per batch
    role           text NOT NULL DEFAULT 'PRIMARY'
                   CHECK (role IN ('PRIMARY','CO_FACULTY','LAB_INSTRUCTOR','GUEST')),
    load_share     numeric(4,3) NOT NULL DEFAULT 1.000 CHECK (load_share > 0 AND load_share <= 1),
    -- decision provenance: what the optimiser proposed vs what the HoD approved
    proposed_by_agent text,
    match_score    numeric(5,2),
    match_rationale text,
    approved_by    uuid REFERENCES identity.app_user,
    approved_at    timestamptz,
    override_reason text,
    valid_from     date NOT NULL DEFAULT current_date,
    valid_to       date,
    UNIQUE (course_offering_id, faculty_id, role, lab_batch_id, valid_from)
);
CREATE INDEX idx_alloc_faculty ON academics.faculty_allocation (faculty_id, valid_from);

-- ---------------------------------------------------------------------
-- Timetable
-- ---------------------------------------------------------------------
CREATE TABLE academics.time_slot (
    time_slot_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    day_of_week  smallint NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    period_no    smallint NOT NULL,
    start_time   time NOT NULL,
    end_time     time NOT NULL,
    slot_type    text NOT NULL DEFAULT 'CLASS'
                 CHECK (slot_type IN ('CLASS','BREAK','LUNCH','LIBRARY','SPORTS')),
    UNIQUE (institution_id, day_of_week, period_no),
    CHECK (end_time > start_time)
);

CREATE TABLE academics.timetable_version (
    timetable_version_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    term_id     uuid NOT NULL REFERENCES core.term,
    department_id uuid REFERENCES core.department,
    version_no  smallint NOT NULL,
    effective_from date NOT NULL,
    effective_to   date,
    status      text NOT NULL DEFAULT 'DRAFT'
                CHECK (status IN ('DRAFT','REVIEW','PUBLISHED','SUPERSEDED')),
    generated_by_agent text,
    solver_stats jsonb,
    published_by uuid REFERENCES identity.app_user,
    UNIQUE (term_id, department_id, version_no)
);

CREATE TABLE academics.timetable_entry (
    timetable_entry_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timetable_version_id uuid NOT NULL REFERENCES academics.timetable_version ON DELETE CASCADE,
    course_offering_id uuid NOT NULL REFERENCES academics.course_offering,
    time_slot_id   uuid NOT NULL REFERENCES academics.time_slot,
    room_id        uuid REFERENCES core.room,
    faculty_id     uuid NOT NULL REFERENCES people.faculty,
    lab_batch_id   uuid REFERENCES curriculum.lab_batch,
    duration_slots smallint NOT NULL DEFAULT 1,   -- labs occupy consecutive slots
    -- Hard-constraint enforcement. A published timetable must not violate these.
    UNIQUE (timetable_version_id, time_slot_id, faculty_id),
    UNIQUE (timetable_version_id, time_slot_id, room_id)
);
CREATE INDEX idx_tt_offering ON academics.timetable_entry (course_offering_id);

CREATE TABLE academics.timetable_clash (
    timetable_clash_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timetable_version_id uuid NOT NULL REFERENCES academics.timetable_version ON DELETE CASCADE,
    clash_type   text NOT NULL CHECK (clash_type IN
                 ('FACULTY','ROOM','SECTION','LAB_BATCH','CAPACITY','CONTACT_HOURS','SOFT')),
    severity     text NOT NULL CHECK (severity IN ('HARD','SOFT')),
    description  text NOT NULL,
    entry_refs   uuid[],
    resolved     boolean NOT NULL DEFAULT false
);

-- ---------------------------------------------------------------------
-- Lesson planning and delivery
-- ---------------------------------------------------------------------
CREATE TABLE academics.lesson_plan (
    lesson_plan_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_offering_id uuid NOT NULL UNIQUE REFERENCES academics.course_offering ON DELETE CASCADE,
    prepared_by_faculty_id uuid NOT NULL REFERENCES people.faculty,
    total_planned_sessions smallint,
    buffer_sessions smallint DEFAULT 0,
    status      text NOT NULL DEFAULT 'DRAFT'
                CHECK (status IN ('DRAFT','SUBMITTED','APPROVED','REVISED')),
    approved_by uuid REFERENCES identity.app_user,
    approved_at timestamptz
);

CREATE TABLE academics.lesson_plan_session (
    lesson_plan_session_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_plan_id  uuid NOT NULL REFERENCES academics.lesson_plan ON DELETE CASCADE,
    seq_no          smallint NOT NULL,
    planned_date    date,
    course_topic_id uuid REFERENCES curriculum.course_topic,
    course_unit_id  uuid REFERENCES curriculum.course_unit,
    course_outcome_id uuid REFERENCES curriculum.course_outcome,
    teaching_method text CHECK (teaching_method IN
                    ('LECTURE','TUTORIAL','DEMO','PROBLEM_SOLVING','FLIPPED','SEMINAR',
                     'LAB','CASE_STUDY','GUEST','BUFFER','REVISION')),
    resource_ref    text,
    UNIQUE (lesson_plan_id, seq_no)
);

-- A class_session is an actual, conducted (or cancelled) class.
-- Attendance hangs off this, not off the timetable, because reality differs.
CREATE TABLE academics.class_session (
    class_session_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_offering_id uuid NOT NULL REFERENCES academics.course_offering,
    session_date   date NOT NULL,
    time_slot_id   uuid REFERENCES academics.time_slot,
    faculty_id     uuid NOT NULL REFERENCES people.faculty,
    room_id        uuid REFERENCES core.room,
    lab_batch_id   uuid REFERENCES curriculum.lab_batch,
    session_type   text NOT NULL DEFAULT 'REGULAR'
                   CHECK (session_type IN ('REGULAR','COMPENSATION','EXTRA','REMEDIAL','SUBSTITUTED')),
    status         text NOT NULL DEFAULT 'SCHEDULED'
                   CHECK (status IN ('SCHEDULED','CONDUCTED','CANCELLED','RESCHEDULED')),
    lesson_plan_session_id uuid REFERENCES academics.lesson_plan_session,
    topic_covered  text,
    substituted_for_faculty_id uuid REFERENCES people.faculty,
    marked_at      timestamptz,
    UNIQUE (course_offering_id, session_date, time_slot_id, lab_batch_id)
);
CREATE INDEX idx_class_session_offering_date ON academics.class_session (course_offering_id, session_date);

CREATE TABLE academics.topic_progress (
    topic_progress_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_offering_id uuid NOT NULL REFERENCES academics.course_offering ON DELETE CASCADE,
    course_topic_id uuid NOT NULL REFERENCES curriculum.course_topic,
    status       text NOT NULL DEFAULT 'PENDING'
                 CHECK (status IN ('PENDING','IN_PROGRESS','COMPLETED','SKIPPED')),
    completed_on date,
    class_session_id uuid REFERENCES academics.class_session,
    remarks      text,
    UNIQUE (course_offering_id, course_topic_id)
);

-- Derived weekly snapshot written by Agent 6. Kept as a table, not a view,
-- because the variance history is itself the reportable artefact.
CREATE TABLE academics.coverage_snapshot (
    coverage_snapshot_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_offering_id uuid NOT NULL REFERENCES academics.course_offering ON DELETE CASCADE,
    as_of_date     date NOT NULL,
    planned_sessions_to_date smallint,
    conducted_sessions smallint,
    planned_topics_to_date smallint,
    completed_topics smallint,
    coverage_pct   numeric(5,2),
    variance_pct   numeric(6,2),
    status         text CHECK (status IN ('ON_TRACK','MINOR_SLIPPAGE','SIGNIFICANT_SLIPPAGE','CRITICAL')),
    recovery_sessions_needed smallint,
    computed_by_agent text,
    UNIQUE (course_offering_id, as_of_date)
);

-- =====================================================================
-- ATTENDANCE
-- Grain: one row per student per class_session. Partitioned by date.
-- =====================================================================

CREATE TABLE attendance.attendance_record (
    attendance_record_id uuid NOT NULL DEFAULT gen_random_uuid(),
    class_session_id uuid NOT NULL,
    student_id     uuid NOT NULL,
    session_date   date NOT NULL,
    status         text NOT NULL CHECK (status IN ('PRESENT','ABSENT','LATE','ON_DUTY','EXCUSED_LEAVE')),
    marked_by_user_id uuid,
    marked_at      timestamptz NOT NULL DEFAULT now(),
    source         text NOT NULL DEFAULT 'MANUAL'
                   CHECK (source IN ('MANUAL','BIOMETRIC','RFID','LMS','IMPORT')),
    corrected_from text,
    correction_reason text,
    PRIMARY KEY (attendance_record_id, session_date),
    UNIQUE (class_session_id, student_id, session_date)
) PARTITION BY RANGE (session_date);

CREATE TABLE attendance.attendance_record_2026 PARTITION OF attendance.attendance_record
  FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE attendance.attendance_record_2027 PARTITION OF attendance.attendance_record
  FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');

CREATE INDEX idx_att_student_date ON attendance.attendance_record (student_id, session_date);
CREATE INDEX idx_att_session ON attendance.attendance_record (class_session_id);

CREATE TABLE attendance.student_leave (
    student_leave_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  uuid NOT NULL REFERENCES people.student,
    leave_type  text NOT NULL CHECK (leave_type IN ('MEDICAL','ON_DUTY','PERSONAL','SPORTS','PLACEMENT')),
    from_date   date NOT NULL,
    to_date     date NOT NULL,
    reason      text,
    evidence_ref uuid,                  -- knowledge.document; medical certs restricted
    status      text NOT NULL DEFAULT 'PENDING'
                CHECK (status IN ('PENDING','APPROVED','REJECTED','CANCELLED')),
    approved_by uuid REFERENCES identity.app_user,
    approved_at timestamptz,
    CHECK (to_date >= from_date)
);
CREATE INDEX idx_student_leave ON attendance.student_leave (student_id, from_date, to_date);

-- Written by Agent 11 on each analysis run. Both raw and adjusted are stored
-- so a report always states which basis it used.
CREATE TABLE attendance.attendance_summary (
    attendance_summary_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id     uuid NOT NULL REFERENCES people.student,
    course_offering_id uuid REFERENCES academics.course_offering,  -- null = term aggregate
    term_id        uuid NOT NULL REFERENCES core.term,
    as_of_date     date NOT NULL,
    classes_held   smallint NOT NULL,
    classes_attended smallint NOT NULL,
    on_duty_count  smallint NOT NULL DEFAULT 0,
    excused_count  smallint NOT NULL DEFAULT 0,
    raw_pct        numeric(5,2) NOT NULL,
    adjusted_pct   numeric(5,2) NOT NULL,
    trend_slope    numeric(6,3),        -- pct points per week; negative = declining
    projected_end_pct numeric(5,2),     -- headline figure for student communication
    band           text CHECK (band IN ('GTE_75','B70_75','B65_70','B60_65','B50_60','LT_50')),
    risk_level     text CHECK (risk_level IN ('NONE','WATCH','AT_RISK','CRITICAL')),
    computed_by_agent text,
    agent_run_id   uuid,
    UNIQUE (student_id, course_offering_id, term_id, as_of_date)
);
CREATE INDEX idx_att_summary_band ON attendance.attendance_summary (term_id, band, risk_level);

CREATE TABLE attendance.condonation (
    condonation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  uuid NOT NULL REFERENCES people.student,
    term_id     uuid NOT NULL REFERENCES core.term,
    attendance_pct numeric(5,2) NOT NULL,
    category    text CHECK (category IN ('CONDONABLE','NOT_CONDONABLE','DETAINED')),
    fee_paid    boolean DEFAULT false,
    status      text NOT NULL DEFAULT 'PENDING'
                CHECK (status IN ('PENDING','APPROVED','REJECTED')),
    approved_by uuid REFERENCES identity.app_user,
    approved_at timestamptz,
    UNIQUE (student_id, term_id)
);

-- Data quality gate. Agent 11 must not analyse until validation passes.
CREATE TABLE attendance.ingestion_batch (
    ingestion_batch_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source        text NOT NULL,
    file_ref      text,
    department_id uuid REFERENCES core.department,
    term_id       uuid REFERENCES core.term,
    row_count     integer,
    accepted_count integer,
    rejected_count integer,
    validation_report jsonb,
    status        text NOT NULL DEFAULT 'RECEIVED'
                  CHECK (status IN ('RECEIVED','VALIDATING','FAILED','PARTIAL','ACCEPTED')),
    received_at   timestamptz NOT NULL DEFAULT now(),
    processed_at  timestamptz
);

SELECT core.add_audit_columns('academics.course_offering');
SELECT core.add_audit_columns('academics.faculty_allocation');
SELECT core.add_audit_columns('academics.timetable_entry');
SELECT core.add_audit_columns('academics.class_session');
SELECT core.add_audit_columns('attendance.student_leave');
SELECT core.add_audit_columns('attendance.condonation');
