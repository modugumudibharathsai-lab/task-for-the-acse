-- =====================================================================
-- 05_assessment_exams_outcomes.sql
-- Serves Agents 8, 12, 15, 30, 31, 32, 33, 34, 35
--
-- KEY DESIGN DECISION: question-wise marks are stored, not just totals.
-- CO attainment (Agent 8) is impossible to automate without them, and
-- retrofitting question-level capture after a year of totals-only data
-- means a year of accreditation evidence has to be reconstructed by hand.
-- =====================================================================

CREATE TABLE assessment.assessment_type (
    assessment_type_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    code       text NOT NULL,            -- FA1, MID1, ASSIGN, QUIZ, LAB, END_SEM
    name       text NOT NULL,
    category   text NOT NULL CHECK (category IN ('INTERNAL','EXTERNAL','FORMATIVE','LAB')),
    default_max_marks smallint,
    counts_toward_internal boolean NOT NULL DEFAULT true,
    UNIQUE (institution_id, code)
);

CREATE TABLE assessment.assessment (
    assessment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_offering_id uuid NOT NULL REFERENCES academics.course_offering ON DELETE CASCADE,
    assessment_type_id uuid NOT NULL REFERENCES assessment.assessment_type,
    name          text NOT NULL,
    sequence_no   smallint,
    max_marks     numeric(6,2) NOT NULL,
    weightage     numeric(5,2),          -- contribution to internal total
    conducted_on  date,
    syllabus_scope jsonb,                -- unit ids covered
    status        text NOT NULL DEFAULT 'PLANNED'
                  CHECK (status IN ('PLANNED','CONDUCTED','EVALUATED','PUBLISHED','LOCKED')),
    entry_due_date date,
    UNIQUE (course_offering_id, assessment_type_id, sequence_no)
);
CREATE INDEX idx_assessment_offering ON assessment.assessment (course_offering_id, status);

-- ---------------------------------------------------------------------
-- Question bank and papers (Agents 31, 32)
-- ---------------------------------------------------------------------
CREATE TABLE assessment.question_bank_item (
    question_bank_item_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_version_id uuid NOT NULL REFERENCES curriculum.course_version,
    course_unit_id    uuid REFERENCES curriculum.course_unit,
    course_outcome_id uuid REFERENCES curriculum.course_outcome,
    question_text     text NOT NULL,
    answer_key        text,
    marks             numeric(5,2) NOT NULL,
    bloom_level       smallint CHECK (bloom_level BETWEEN 1 AND 6),
    difficulty        text CHECK (difficulty IN ('EASY','MODERATE','DIFFICULT')),
    question_type     text CHECK (question_type IN ('MCQ','SHORT','LONG','NUMERICAL','DIAGRAM','PROGRAM')),
    origin            text NOT NULL DEFAULT 'FACULTY'
                      CHECK (origin IN ('FACULTY','AGENT_GENERATED','IMPORTED')),
    validation_status text NOT NULL DEFAULT 'PENDING'
                      CHECK (validation_status IN ('PENDING','VALIDATED','REJECTED','RETIRED')),
    validated_by_faculty_id uuid REFERENCES people.faculty,
    validated_at      timestamptz,
    times_used        smallint NOT NULL DEFAULT 0,
    last_used_on      date,
    contributed_by_faculty_id uuid REFERENCES people.faculty
);
CREATE INDEX idx_qbank_lookup ON assessment.question_bank_item
  (course_version_id, course_unit_id, course_outcome_id, bloom_level, difficulty)
  WHERE validation_status = 'VALIDATED';

COMMENT ON COLUMN assessment.question_bank_item.validation_status IS
  'Agent-generated questions enter as PENDING. A paper may only draw VALIDATED items. '
  'This constraint is what prevents an unvetted generated question reaching an exam hall.';

CREATE TABLE assessment.paper_blueprint (
    paper_blueprint_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_version_id uuid REFERENCES curriculum.course_version,
    assessment_type_id uuid NOT NULL REFERENCES assessment.assessment_type,
    name           text NOT NULL,
    total_marks    numeric(6,2) NOT NULL,
    duration_minutes smallint,
    structure      jsonb NOT NULL,       -- sections, choice pattern
    unit_distribution jsonb,             -- {unit_no: target_pct}
    co_distribution   jsonb,
    bloom_distribution jsonb,
    difficulty_distribution jsonb,
    is_active      boolean NOT NULL DEFAULT true
);

CREATE TABLE assessment.question_paper (
    question_paper_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id  uuid REFERENCES assessment.assessment,
    exam_schedule_id uuid,               -- FK added after exams.exam_schedule
    paper_blueprint_id uuid REFERENCES assessment.paper_blueprint,
    course_version_id uuid NOT NULL REFERENCES curriculum.course_version,
    version_no     smallint NOT NULL DEFAULT 1,
    set_code       text,                 -- 'A','B' for multiple sets
    generated_by_agent text,
    status         text NOT NULL DEFAULT 'DRAFT'
                   CHECK (status IN ('DRAFT','MODERATION','APPROVED','SEALED','USED','CANCELLED')),
    setter_faculty_id    uuid REFERENCES people.faculty,
    moderator_faculty_id uuid REFERENCES people.faculty,
    approved_by    uuid REFERENCES identity.app_user,
    approved_at    timestamptz,
    -- confidentiality
    sensitivity    text NOT NULL DEFAULT 'RESTRICTED',
    access_opens_at  timestamptz,
    access_closes_at timestamptz
);

COMMENT ON TABLE assessment.question_paper IS
  'RESTRICTED. Row access is time-boxed via access_opens_at/closes_at and enforced by RLS. '
  'Content must never be passed into a general-purpose model context.';

CREATE TABLE assessment.paper_question (
    paper_question_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    question_paper_id uuid NOT NULL REFERENCES assessment.question_paper ON DELETE CASCADE,
    question_bank_item_id uuid REFERENCES assessment.question_bank_item,
    section_code   text,
    question_no    text NOT NULL,        -- '1a','2b'
    sub_question_of uuid REFERENCES assessment.paper_question,
    question_text  text NOT NULL,
    marks          numeric(5,2) NOT NULL,
    course_outcome_id uuid REFERENCES curriculum.course_outcome,
    course_unit_id uuid REFERENCES curriculum.course_unit,
    bloom_level    smallint,
    is_optional    boolean NOT NULL DEFAULT false,
    choice_group   text,
    UNIQUE (question_paper_id, question_no)
);

CREATE TABLE assessment.paper_quality_review (
    paper_quality_review_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    question_paper_id uuid NOT NULL REFERENCES assessment.question_paper ON DELETE CASCADE,
    reviewed_by_agent text,
    reviewed_at    timestamptz NOT NULL DEFAULT now(),
    blueprint_compliance jsonb,
    repetition_findings  jsonb,
    issues         jsonb,                -- [{severity, question_no, issue}]
    overall_verdict text CHECK (overall_verdict IN ('PASS','PASS_WITH_CHANGES','FAIL')),
    moderator_action text
);

-- ---------------------------------------------------------------------
-- Marks
-- ---------------------------------------------------------------------
CREATE TABLE assessment.student_assessment_mark (
    student_assessment_mark_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id uuid NOT NULL REFERENCES assessment.assessment ON DELETE CASCADE,
    student_id    uuid NOT NULL REFERENCES people.student,
    marks_obtained numeric(6,2),
    is_absent     boolean NOT NULL DEFAULT false,
    is_malpractice boolean NOT NULL DEFAULT false,
    entered_by_user_id uuid REFERENCES identity.app_user,
    entered_at    timestamptz,
    is_locked     boolean NOT NULL DEFAULT false,
    UNIQUE (assessment_id, student_id),
    CHECK (marks_obtained IS NULL OR marks_obtained >= 0)
);
CREATE INDEX idx_sam_student ON assessment.student_assessment_mark (student_id);

-- The table that makes Agent 8 possible.
CREATE TABLE assessment.student_question_mark (
    student_question_mark_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_question_id uuid NOT NULL REFERENCES assessment.paper_question ON DELETE CASCADE,
    student_id     uuid NOT NULL REFERENCES people.student,
    marks_obtained numeric(5,2),
    attempted      boolean NOT NULL DEFAULT true,
    UNIQUE (paper_question_id, student_id)
);
CREATE INDEX idx_sqm_student ON assessment.student_question_mark (student_id);

CREATE TABLE assessment.mark_change_log (
    mark_change_log_id bigserial PRIMARY KEY,
    student_assessment_mark_id uuid,
    student_id     uuid NOT NULL,
    old_marks      numeric(6,2),
    new_marks      numeric(6,2),
    reason         text NOT NULL,
    changed_by_user_id uuid NOT NULL,
    approved_by_user_id uuid,
    changed_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE assessment.internal_mark (
    internal_mark_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_offering_id uuid NOT NULL REFERENCES academics.course_offering,
    student_id     uuid NOT NULL REFERENCES people.student,
    components     jsonb NOT NULL,       -- {"MID1":18,"MID2":20,"ASSIGN":9}
    formula_version text NOT NULL,
    computed_marks numeric(6,2) NOT NULL,
    max_marks      numeric(6,2) NOT NULL,
    is_provisional boolean NOT NULL DEFAULT true,
    published_at   timestamptz,
    finalised_at   timestamptz,
    finalised_by   uuid REFERENCES identity.app_user,
    UNIQUE (course_offering_id, student_id)
);

CREATE TABLE assessment.mark_anomaly (
    mark_anomaly_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_offering_id uuid REFERENCES academics.course_offering,
    assessment_id  uuid REFERENCES assessment.assessment,
    anomaly_type   text NOT NULL CHECK (anomaly_type IN
                   ('SECTION_MEAN_OUTLIER','MISSING_ENTRY','OUT_OF_RANGE','DUPLICATE',
                    'INTERNAL_EXTERNAL_DIVERGENCE','CLUSTERED_MARKS')),
    detail         jsonb,
    severity       text CHECK (severity IN ('INFO','WARNING','CRITICAL')),
    detected_by_agent text,
    detected_at    timestamptz NOT NULL DEFAULT now(),
    status         text NOT NULL DEFAULT 'OPEN'
                   CHECK (status IN ('OPEN','EXPLAINED','CORRECTED','DISMISSED')),
    resolution_note text
);

-- ---------------------------------------------------------------------
-- Results
-- ---------------------------------------------------------------------
CREATE TABLE assessment.course_result (
    course_result_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id     uuid NOT NULL REFERENCES people.student,
    course_version_id uuid NOT NULL REFERENCES curriculum.course_version,
    term_id        uuid NOT NULL REFERENCES core.term,
    course_offering_id uuid REFERENCES academics.course_offering,
    attempt_no     smallint NOT NULL DEFAULT 1,
    exam_type      text NOT NULL DEFAULT 'REGULAR'
                   CHECK (exam_type IN ('REGULAR','SUPPLEMENTARY','IMPROVEMENT','REVALUATION')),
    internal_marks numeric(6,2),
    external_marks numeric(6,2),
    total_marks    numeric(6,2),
    max_marks      numeric(6,2),
    grade          text,
    grade_point    numeric(4,2),
    credits        numeric(4,1),
    result_status  text NOT NULL CHECK (result_status IN ('PASS','FAIL','ABSENT','WITHHELD','MALPRACTICE')),
    published_on   date,
    UNIQUE (student_id, course_version_id, term_id, attempt_no, exam_type)
);
CREATE INDEX idx_course_result_student ON assessment.course_result (student_id, result_status);
CREATE INDEX idx_course_result_cv_term ON assessment.course_result (course_version_id, term_id);

CREATE TABLE assessment.term_result (
    term_result_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id     uuid NOT NULL REFERENCES people.student,
    term_id        uuid NOT NULL REFERENCES core.term,
    credits_registered numeric(5,1),
    credits_earned numeric(5,1),
    sgpa           numeric(4,2),
    cgpa           numeric(4,2),
    backlog_count  smallint NOT NULL DEFAULT 0,
    promotion_status text CHECK (promotion_status IN ('PROMOTED','DETAINED','CONDITIONAL')),
    published_on   date,
    UNIQUE (student_id, term_id)
);

CREATE TABLE assessment.backlog (
    backlog_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id     uuid NOT NULL REFERENCES people.student,
    course_version_id uuid NOT NULL REFERENCES curriculum.course_version,
    origin_term_id uuid NOT NULL REFERENCES core.term,
    attempts_made  smallint NOT NULL DEFAULT 1,
    attempts_remaining smallint,
    status         text NOT NULL DEFAULT 'PENDING'
                   CHECK (status IN ('PENDING','CLEARED','EXHAUSTED','WAIVED')),
    cleared_in_term_id uuid REFERENCES core.term,
    cleared_on     date,
    UNIQUE (student_id, course_version_id, origin_term_id)
);
CREATE INDEX idx_backlog_open ON assessment.backlog (student_id) WHERE status = 'PENDING';

-- =====================================================================
-- EXAMS : operations
-- =====================================================================

CREATE TABLE exams.exam_event (
    exam_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    term_id     uuid NOT NULL REFERENCES core.term,
    name        text NOT NULL,
    exam_type   text NOT NULL CHECK (exam_type IN ('REGULAR','SUPPLEMENTARY','SPECIAL')),
    start_date  date,
    end_date    date,
    status      text NOT NULL DEFAULT 'PLANNED'
                CHECK (status IN ('PLANNED','SCHEDULED','IN_PROGRESS','EVALUATION','COMPLETED'))
);

CREATE TABLE exams.exam_schedule (
    exam_schedule_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_event_id  uuid NOT NULL REFERENCES exams.exam_event ON DELETE CASCADE,
    course_version_id uuid NOT NULL REFERENCES curriculum.course_version,
    exam_date      date NOT NULL,
    session        text NOT NULL CHECK (session IN ('FN','AN')),
    start_time     time,
    duration_minutes smallint,
    max_marks      numeric(6,2),
    UNIQUE (exam_event_id, course_version_id)
);
CREATE INDEX idx_exam_sched_date ON exams.exam_schedule (exam_date, session);

ALTER TABLE assessment.question_paper
  ADD CONSTRAINT fk_qp_exam_schedule FOREIGN KEY (exam_schedule_id)
  REFERENCES exams.exam_schedule;

CREATE TABLE exams.exam_registration (
    exam_registration_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_schedule_id uuid NOT NULL REFERENCES exams.exam_schedule ON DELETE CASCADE,
    student_id     uuid NOT NULL REFERENCES people.student,
    attempt_no     smallint NOT NULL DEFAULT 1,
    attendance_eligible boolean,
    fee_cleared    boolean,
    discipline_cleared boolean,
    eligibility_status text NOT NULL DEFAULT 'PENDING'
                   CHECK (eligibility_status IN ('PENDING','ELIGIBLE','CONDONATION_REQUIRED','DETAINED','DEBARRED')),
    hall_ticket_no text,
    UNIQUE (exam_schedule_id, student_id, attempt_no)
);

CREATE TABLE exams.exam_room_allocation (
    exam_room_allocation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_event_id uuid NOT NULL REFERENCES exams.exam_event,
    exam_date   date NOT NULL,
    session     text NOT NULL CHECK (session IN ('FN','AN')),
    room_id     uuid NOT NULL REFERENCES core.room,
    capacity_used smallint,
    UNIQUE (exam_date, session, room_id)
);

CREATE TABLE exams.seating_allocation (
    seating_allocation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_room_allocation_id uuid NOT NULL REFERENCES exams.exam_room_allocation ON DELETE CASCADE,
    student_id  uuid NOT NULL REFERENCES people.student,
    exam_schedule_id uuid NOT NULL REFERENCES exams.exam_schedule,
    seat_no     text NOT NULL,
    UNIQUE (exam_room_allocation_id, seat_no)
);

CREATE TABLE exams.invigilation_duty (
    invigilation_duty_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_room_allocation_id uuid NOT NULL REFERENCES exams.exam_room_allocation ON DELETE CASCADE,
    faculty_id  uuid NOT NULL REFERENCES people.faculty,
    duty_role   text NOT NULL DEFAULT 'INVIGILATOR'
                CHECK (duty_role IN ('INVIGILATOR','RELIEVER','SQUAD','CHIEF')),
    reported_at timestamptz,
    UNIQUE (exam_room_allocation_id, faculty_id)
);

CREATE TABLE exams.answer_script (
    answer_script_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_schedule_id uuid NOT NULL REFERENCES exams.exam_schedule,
    student_id   uuid REFERENCES people.student,     -- nulled during blind evaluation
    dummy_no     text NOT NULL,
    bundle_no    text,
    status       text NOT NULL DEFAULT 'COLLECTED'
                 CHECK (status IN ('COLLECTED','BUNDLED','ISSUED','EVALUATED','RETURNED','MISSING')),
    UNIQUE (exam_schedule_id, dummy_no)
);

CREATE TABLE exams.evaluation (
    evaluation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    answer_script_id uuid NOT NULL REFERENCES exams.answer_script ON DELETE CASCADE,
    evaluator_faculty_id uuid NOT NULL REFERENCES people.faculty,
    round_no    smallint NOT NULL DEFAULT 1,
    total_marks numeric(6,2),
    evaluated_on date,
    UNIQUE (answer_script_id, round_no)
);

CREATE TABLE exams.revaluation_request (
    revaluation_request_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_schedule_id uuid NOT NULL REFERENCES exams.exam_schedule,
    student_id  uuid NOT NULL REFERENCES people.student,
    request_type text NOT NULL CHECK (request_type IN ('RECOUNT','REVALUATION','PHOTOCOPY','CHALLENGE')),
    fee_paid    boolean NOT NULL DEFAULT false,
    original_marks numeric(6,2),
    revised_marks  numeric(6,2),
    status      text NOT NULL DEFAULT 'SUBMITTED'
                CHECK (status IN ('SUBMITTED','IN_PROCESS','COMPLETED','REJECTED')),
    requested_on date NOT NULL DEFAULT current_date,
    completed_on date
);

CREATE TABLE exams.malpractice_case (
    malpractice_case_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_schedule_id uuid NOT NULL REFERENCES exams.exam_schedule,
    student_id  uuid NOT NULL REFERENCES people.student,
    reported_by_faculty_id uuid REFERENCES people.faculty,
    incident_description text NOT NULL,
    evidence_ref uuid,
    committee_decision text,
    penalty     text,
    status      text NOT NULL DEFAULT 'REPORTED'
                CHECK (status IN ('REPORTED','UNDER_ENQUIRY','DECIDED','APPEALED','CLOSED')),
    decided_on  date
);

-- =====================================================================
-- OUTCOMES : CO / PO attainment (Agent 8)
-- =====================================================================

CREATE TABLE outcomes.attainment_rubric (
    attainment_rubric_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    programme_id   uuid REFERENCES curriculum.programme,   -- null = institution default
    name           text NOT NULL,
    version        text NOT NULL,
    threshold_pct  numeric(5,2) NOT NULL,      -- student is "attaining" above this
    level_bands    jsonb NOT NULL,             -- [{"min_pct":70,"level":3}, ...]
    direct_weight  numeric(4,3) NOT NULL DEFAULT 0.800,
    indirect_weight numeric(4,3) NOT NULL DEFAULT 0.200,
    effective_from date NOT NULL,
    effective_to   date,
    UNIQUE (institution_id, programme_id, version),
    CHECK (direct_weight + indirect_weight = 1.000)
);

COMMENT ON TABLE outcomes.attainment_rubric IS
  'The attainment formula is configuration, never code. Institutions revise thresholds '
  'between accreditation cycles and different programmes may use different rubrics.';

CREATE TABLE outcomes.attainment_run (
    attainment_run_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_offering_id uuid NOT NULL REFERENCES academics.course_offering,
    attainment_rubric_id uuid NOT NULL REFERENCES outcomes.attainment_rubric,
    run_at       timestamptz NOT NULL DEFAULT now(),
    run_by_agent text,
    input_assessment_ids uuid[],
    student_count smallint,
    status       text NOT NULL DEFAULT 'COMPUTED'
                 CHECK (status IN ('COMPUTED','REVIEWED','APPROVED','SUPERSEDED')),
    approved_by  uuid REFERENCES identity.app_user,
    approved_at  timestamptz
);

CREATE TABLE outcomes.co_attainment (
    co_attainment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    attainment_run_id uuid NOT NULL REFERENCES outcomes.attainment_run ON DELETE CASCADE,
    course_outcome_id uuid NOT NULL REFERENCES curriculum.course_outcome,
    students_evaluated smallint,
    students_attaining smallint,
    attaining_pct   numeric(5,2),
    direct_level    numeric(4,2),
    indirect_level  numeric(4,2),
    final_level     numeric(4,2),
    target_level    numeric(4,2),
    gap             numeric(4,2) GENERATED ALWAYS AS (final_level - target_level) STORED,
    contributing_questions jsonb,     -- traceability back to paper_question ids
    UNIQUE (attainment_run_id, course_outcome_id)
);

CREATE TABLE outcomes.po_attainment (
    po_attainment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    programme_outcome_id uuid NOT NULL REFERENCES curriculum.programme_outcome,
    batch_id     uuid NOT NULL REFERENCES curriculum.batch,
    term_id      uuid REFERENCES core.term,
    computed_at  timestamptz NOT NULL DEFAULT now(),
    contributing_co_count smallint,
    weighted_level numeric(4,2),
    target_level  numeric(4,2),
    contributing_runs uuid[],         -- attainment_run ids, for full audit trail
    status       text NOT NULL DEFAULT 'COMPUTED',
    approved_by  uuid REFERENCES identity.app_user,
    UNIQUE (programme_outcome_id, batch_id, term_id)
);

CREATE TABLE outcomes.indirect_feedback (
    indirect_feedback_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_offering_id uuid NOT NULL REFERENCES academics.course_offering,
    course_outcome_id uuid NOT NULL REFERENCES curriculum.course_outcome,
    student_id   uuid REFERENCES people.student,
    rating       smallint CHECK (rating BETWEEN 1 AND 5),
    submitted_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (course_offering_id, course_outcome_id, student_id)
);

CREATE TABLE outcomes.attainment_action (
    attainment_action_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    co_attainment_id uuid NOT NULL REFERENCES outcomes.co_attainment ON DELETE CASCADE,
    gap_analysis  text,
    probable_cause text,
    action_proposed text NOT NULL,
    owner_faculty_id uuid REFERENCES people.faculty,
    target_term_id uuid REFERENCES core.term,
    status        text NOT NULL DEFAULT 'PROPOSED'
                  CHECK (status IN ('PROPOSED','APPROVED','IN_PROGRESS','COMPLETED','DROPPED')),
    outcome_note  text
);

SELECT core.add_audit_columns('assessment.assessment');
SELECT core.add_audit_columns('assessment.question_bank_item');
SELECT core.add_audit_columns('assessment.question_paper');
SELECT core.add_audit_columns('assessment.student_assessment_mark');
SELECT core.add_audit_columns('assessment.internal_mark');
SELECT core.add_audit_columns('assessment.course_result');
SELECT core.add_audit_columns('outcomes.co_attainment');
SELECT core.add_audit_columns('outcomes.po_attainment');
