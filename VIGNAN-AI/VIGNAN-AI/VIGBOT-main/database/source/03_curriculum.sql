-- =====================================================================
-- 03_curriculum.sql : programmes, regulations, courses, units, outcomes
-- Serves Agents 1, 2, 8, 31, 54, 67
--
-- KEY DESIGN DECISION: a course is not a single thing. There is a stable
-- course identity (title, department) and a regulation-specific VERSION of
-- it (credits, syllabus, outcomes). Three or four regulations run
-- simultaneously across live batches, so version is a first-class entity.
-- =====================================================================

CREATE TABLE curriculum.programme (
    programme_id   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    department_id  uuid NOT NULL REFERENCES core.department,
    code           text NOT NULL,
    name           text NOT NULL,
    level          text NOT NULL CHECK (level IN ('UG','PG','PHD','DIPLOMA','INTEGRATED')),
    degree         text NOT NULL,                 -- 'B.Tech','M.Tech','MBA'
    specialisation text,
    duration_years numeric(3,1) NOT NULL,
    total_terms    smallint NOT NULL,
    sanctioned_intake smallint,
    is_active      boolean NOT NULL DEFAULT true,
    UNIQUE (institution_id, code)
);

CREATE TABLE curriculum.regulation (
    regulation_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    code           text NOT NULL,                 -- 'R23'
    name           text NOT NULL,
    effective_from_admission_year smallint NOT NULL,
    effective_to_admission_year   smallint,
    approved_on    date,
    approving_body text,
    status         text NOT NULL DEFAULT 'DRAFT'
                   CHECK (status IN ('DRAFT','APPROVED','ACTIVE','SUPERSEDED','WITHDRAWN')),
    superseded_by  uuid REFERENCES curriculum.regulation,
    document_ref   uuid,                          -- knowledge.document
    UNIQUE (institution_id, code)
);

-- Credit and category norms the regulation imposes; checked by Agent 54.
CREATE TABLE curriculum.regulation_norm (
    regulation_norm_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    regulation_id  uuid NOT NULL REFERENCES curriculum.regulation ON DELETE CASCADE,
    programme_id   uuid REFERENCES curriculum.programme,
    course_category text NOT NULL,                -- BSC, ESC, PCC, PEC, OEC, HSMC, PROJ
    min_credits    numeric(5,1),
    max_credits    numeric(5,1),
    UNIQUE (regulation_id, programme_id, course_category)
);

CREATE TABLE curriculum.batch (
    batch_id       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    programme_id   uuid NOT NULL REFERENCES curriculum.programme,
    regulation_id  uuid NOT NULL REFERENCES curriculum.regulation,
    admission_year smallint NOT NULL,
    label          text NOT NULL,                 -- '2023-27 CSE'
    expected_graduation_year smallint,
    status         text NOT NULL DEFAULT 'ACTIVE'
                   CHECK (status IN ('ACTIVE','GRADUATED','CLOSED')),
    UNIQUE (programme_id, admission_year)
);

CREATE TABLE curriculum.section (
    section_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id       uuid NOT NULL REFERENCES curriculum.batch,
    code           text NOT NULL,                 -- 'A','B','CSE-1'
    year_of_study  smallint NOT NULL CHECK (year_of_study BETWEEN 1 AND 6),
    strength       smallint,
    class_advisor_faculty_id uuid REFERENCES people.faculty,
    is_active      boolean NOT NULL DEFAULT true,
    UNIQUE (batch_id, code, year_of_study)
);

-- Lab batches: a section splits into sub-batches for laboratory sessions.
CREATE TABLE curriculum.lab_batch (
    lab_batch_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    section_id   uuid NOT NULL REFERENCES curriculum.section ON DELETE CASCADE,
    code         text NOT NULL,                   -- 'B1','B2'
    strength     smallint,
    UNIQUE (section_id, code)
);

ALTER TABLE people.student
  ADD CONSTRAINT fk_student_batch FOREIGN KEY (batch_id) REFERENCES curriculum.batch,
  ADD CONSTRAINT fk_student_section FOREIGN KEY (current_section_id) REFERENCES curriculum.section;

CREATE TABLE people.student_lab_batch (
    student_id   uuid NOT NULL REFERENCES people.student ON DELETE CASCADE,
    lab_batch_id uuid NOT NULL REFERENCES curriculum.lab_batch ON DELETE CASCADE,
    PRIMARY KEY (student_id, lab_batch_id)
);

-- ---------------------------------------------------------------------
-- Course identity vs course version
-- ---------------------------------------------------------------------
CREATE TABLE curriculum.course (
    course_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    owning_department_id uuid NOT NULL REFERENCES core.department,
    title         text NOT NULL,
    short_title   text,
    is_active     boolean NOT NULL DEFAULT true
);

-- The regulation-specific, semester-placed instance of a course.
-- This is what a syllabus, a set of COs, and a credit value belong to.
CREATE TABLE curriculum.course_version (
    course_version_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id      uuid NOT NULL REFERENCES curriculum.course,
    regulation_id  uuid NOT NULL REFERENCES curriculum.regulation,
    programme_id   uuid NOT NULL REFERENCES curriculum.programme,
    course_code    text NOT NULL,                 -- 'CS301'
    term_no        smallint NOT NULL CHECK (term_no BETWEEN 1 AND 12),
    year_of_study  smallint NOT NULL,
    course_category text NOT NULL,                -- must match regulation_norm categories
    course_type    text NOT NULL CHECK (course_type IN
                   ('THEORY','LAB','THEORY_WITH_LAB','PROJECT','INTERNSHIP','SEMINAR',
                    'MOOC','AUDIT','MANDATORY_NON_CREDIT')),
    is_elective    boolean NOT NULL DEFAULT false,
    elective_group text,
    credits        numeric(4,1) NOT NULL,
    lecture_hours  smallint NOT NULL DEFAULT 0,
    tutorial_hours smallint NOT NULL DEFAULT 0,
    practical_hours smallint NOT NULL DEFAULT 0,
    total_contact_hours smallint GENERATED ALWAYS AS
                   (lecture_hours + tutorial_hours + practical_hours) STORED,
    internal_max_marks smallint NOT NULL DEFAULT 40,
    external_max_marks smallint NOT NULL DEFAULT 60,
    pass_min_internal  smallint,
    pass_min_external  smallint,
    pass_min_total     smallint,
    syllabus_document_ref uuid,                   -- knowledge.document
    status         text NOT NULL DEFAULT 'ACTIVE'
                   CHECK (status IN ('DRAFT','ACTIVE','SUPERSEDED','WITHDRAWN')),
    UNIQUE (regulation_id, programme_id, course_code)
);
CREATE INDEX idx_cv_lookup ON curriculum.course_version (regulation_id, programme_id, term_no);

CREATE TABLE curriculum.course_prerequisite (
    course_version_id  uuid NOT NULL REFERENCES curriculum.course_version ON DELETE CASCADE,
    prerequisite_course_version_id uuid NOT NULL REFERENCES curriculum.course_version,
    prerequisite_type  text NOT NULL DEFAULT 'MANDATORY'
                       CHECK (prerequisite_type IN ('MANDATORY','RECOMMENDED','COREQUISITE')),
    PRIMARY KEY (course_version_id, prerequisite_course_version_id),
    CHECK (course_version_id <> prerequisite_course_version_id)
);

CREATE TABLE curriculum.course_unit (
    course_unit_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_version_id uuid NOT NULL REFERENCES curriculum.course_version ON DELETE CASCADE,
    unit_no       smallint NOT NULL,
    title         text NOT NULL,
    description   text,
    notional_hours smallint,
    UNIQUE (course_version_id, unit_no)
);

CREATE TABLE curriculum.course_topic (
    course_topic_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_unit_id  uuid NOT NULL REFERENCES curriculum.course_unit ON DELETE CASCADE,
    seq_no          smallint NOT NULL,
    title           text NOT NULL,
    parent_topic_id uuid REFERENCES curriculum.course_topic,   -- sub-topics
    notional_hours  numeric(3,1),
    UNIQUE (course_unit_id, seq_no)
);

CREATE TABLE curriculum.course_outcome (
    course_outcome_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_version_id uuid NOT NULL REFERENCES curriculum.course_version ON DELETE CASCADE,
    co_no          smallint NOT NULL,
    statement      text NOT NULL,
    bloom_level    smallint CHECK (bloom_level BETWEEN 1 AND 6),
    target_level   numeric(3,2),                  -- institutional attainment target
    UNIQUE (course_version_id, co_no)
);

-- Optional: which units primarily serve which CO (used by Agents 5, 31, 67)
CREATE TABLE curriculum.unit_outcome_map (
    course_unit_id    uuid NOT NULL REFERENCES curriculum.course_unit ON DELETE CASCADE,
    course_outcome_id uuid NOT NULL REFERENCES curriculum.course_outcome ON DELETE CASCADE,
    PRIMARY KEY (course_unit_id, course_outcome_id)
);

-- Programme Outcomes and Programme Specific Outcomes
CREATE TABLE curriculum.programme_outcome (
    programme_outcome_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    programme_id   uuid NOT NULL REFERENCES curriculum.programme,
    regulation_id  uuid NOT NULL REFERENCES curriculum.regulation,
    outcome_type   text NOT NULL CHECK (outcome_type IN ('PO','PSO')),
    outcome_no     smallint NOT NULL,
    statement      text NOT NULL,
    target_level   numeric(3,2),
    UNIQUE (programme_id, regulation_id, outcome_type, outcome_no)
);

CREATE TABLE curriculum.co_po_map (
    course_outcome_id    uuid NOT NULL REFERENCES curriculum.course_outcome ON DELETE CASCADE,
    programme_outcome_id uuid NOT NULL REFERENCES curriculum.programme_outcome ON DELETE CASCADE,
    strength             smallint NOT NULL CHECK (strength BETWEEN 1 AND 3),
    justification        text,
    PRIMARY KEY (course_outcome_id, programme_outcome_id)
);

CREATE TABLE curriculum.course_book (
    course_book_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    course_version_id uuid NOT NULL REFERENCES curriculum.course_version ON DELETE CASCADE,
    book_type   text NOT NULL CHECK (book_type IN ('TEXTBOOK','REFERENCE','WEB','MOOC')),
    title       text NOT NULL,
    authors     text,
    publisher   text,
    edition     text,
    isbn        text,
    year        smallint,
    url         text,
    seq_no      smallint
);

SELECT core.add_audit_columns('curriculum.programme');
SELECT core.add_audit_columns('curriculum.regulation');
SELECT core.add_audit_columns('curriculum.course_version');
SELECT core.add_audit_columns('curriculum.course_outcome');
SELECT core.add_audit_columns('curriculum.co_po_map');
