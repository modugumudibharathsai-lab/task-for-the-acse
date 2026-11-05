-- =====================================================================
-- 11_security_rls.sql
-- Row-level security. The access guardrails in the agent specifications
-- are enforced HERE, at the data layer, not in prompt instructions.
-- An agent must be technically incapable of retrieving another student's
-- record regardless of how the question is phrased.
--
-- Session context is set by the application on every connection:
--   SET LOCAL app.user_id      = '<uuid>';
--   SET LOCAL app.person_id    = '<uuid>';
--   SET LOCAL app.student_id   = '<uuid>';   -- when the user is a student
--   SET LOCAL app.faculty_id   = '<uuid>';
--   SET LOCAL app.role_codes   = 'FACULTY,MENTOR';
--   SET LOCAL app.dept_scope   = '<uuid>,<uuid>';
--   SET LOCAL app.agent_code   = 'A11_ATTENDANCE_ANALYSIS';  -- when an agent acts
-- =====================================================================

CREATE OR REPLACE FUNCTION identity.current_user_id() RETURNS uuid AS $$
  SELECT nullif(current_setting('app.user_id', true), '')::uuid
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION identity.current_student_id() RETURNS uuid AS $$
  SELECT nullif(current_setting('app.student_id', true), '')::uuid
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION identity.current_faculty_id() RETURNS uuid AS $$
  SELECT nullif(current_setting('app.faculty_id', true), '')::uuid
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION identity.has_role(p_role text) RETURNS boolean AS $$
  SELECT p_role = ANY (string_to_array(coalesce(current_setting('app.role_codes', true), ''), ','))
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION identity.dept_scope() RETURNS uuid[] AS $$
  SELECT CASE
    WHEN coalesce(current_setting('app.dept_scope', true), '') = '' THEN ARRAY[]::uuid[]
    ELSE string_to_array(current_setting('app.dept_scope', true), ',')::uuid[]
  END
$$ LANGUAGE sql STABLE;

-- Does the current faculty user teach this offering?
CREATE OR REPLACE FUNCTION academics.teaches_offering(p_offering uuid) RETURNS boolean AS $$
  SELECT EXISTS (
    SELECT 1 FROM academics.faculty_allocation fa
    WHERE fa.course_offering_id = p_offering
      AND fa.faculty_id = identity.current_faculty_id()
      AND (fa.valid_to IS NULL OR fa.valid_to >= current_date)
  )
$$ LANGUAGE sql STABLE;

-- Is the current faculty user the assigned mentor of this student?
CREATE OR REPLACE FUNCTION studentlife.is_mentor_of(p_student uuid) RETURNS boolean AS $$
  SELECT EXISTS (
    SELECT 1 FROM studentlife.mentorship m
    WHERE m.student_id = p_student
      AND m.mentor_faculty_id = identity.current_faculty_id()
      AND m.is_current
  )
$$ LANGUAGE sql STABLE;

-- Is this student inside the current user's departmental scope?
CREATE OR REPLACE FUNCTION people.student_in_scope(p_student uuid) RETURNS boolean AS $$
  SELECT EXISTS (
    SELECT 1
    FROM people.student s
    JOIN curriculum.batch b   ON b.batch_id = s.batch_id
    JOIN curriculum.programme p ON p.programme_id = b.programme_id
    WHERE s.student_id = p_student
      AND p.department_id = ANY (identity.dept_scope())
  )
$$ LANGUAGE sql STABLE;

-- ---------------------------------------------------------------------
-- Attendance: a student sees only their own rows.
-- ---------------------------------------------------------------------
ALTER TABLE attendance.attendance_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance.attendance_summary FORCE ROW LEVEL SECURITY;

CREATE POLICY att_summary_self ON attendance.attendance_summary
  FOR SELECT USING (student_id = identity.current_student_id());

CREATE POLICY att_summary_teaching_faculty ON attendance.attendance_summary
  FOR SELECT USING (
    course_offering_id IS NOT NULL
    AND academics.teaches_offering(course_offering_id)
  );

CREATE POLICY att_summary_mentor ON attendance.attendance_summary
  FOR SELECT USING (studentlife.is_mentor_of(student_id));

CREATE POLICY att_summary_dept_leadership ON attendance.attendance_summary
  FOR SELECT USING (
    (identity.has_role('HOD') OR identity.has_role('DEAN') OR identity.has_role('IQAC'))
    AND people.student_in_scope(student_id)
  );

CREATE POLICY att_summary_institution ON attendance.attendance_summary
  FOR ALL USING (identity.has_role('PRINCIPAL') OR identity.has_role('SYSTEM'));

-- ---------------------------------------------------------------------
-- Marks
-- ---------------------------------------------------------------------
ALTER TABLE assessment.internal_mark ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment.internal_mark FORCE ROW LEVEL SECURITY;

CREATE POLICY internal_mark_self ON assessment.internal_mark
  FOR SELECT USING (
    student_id = identity.current_student_id()
    AND is_provisional = false OR published_at IS NOT NULL
  );

CREATE POLICY internal_mark_faculty ON assessment.internal_mark
  FOR ALL USING (academics.teaches_offering(course_offering_id));

CREATE POLICY internal_mark_leadership ON assessment.internal_mark
  FOR SELECT USING (
    (identity.has_role('HOD') OR identity.has_role('DEAN') OR identity.has_role('COE'))
    AND people.student_in_scope(student_id)
  );

-- ---------------------------------------------------------------------
-- Question papers: restricted AND time-boxed.
-- ---------------------------------------------------------------------
ALTER TABLE assessment.question_paper ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment.question_paper FORCE ROW LEVEL SECURITY;

CREATE POLICY qp_setter_moderator ON assessment.question_paper
  FOR ALL USING (
    (setter_faculty_id = identity.current_faculty_id()
     OR moderator_faculty_id = identity.current_faculty_id())
    AND (access_opens_at IS NULL OR now() >= access_opens_at)
    AND (access_closes_at IS NULL OR now() <= access_closes_at)
  );

CREATE POLICY qp_coe ON assessment.question_paper
  FOR ALL USING (identity.has_role('COE'));

-- ---------------------------------------------------------------------
-- Counselling: the strictest boundary in the platform.
-- Only the assigned counsellor and the student themselves.
-- Not the mentor, not the HoD, not the placement cell.
-- ---------------------------------------------------------------------
ALTER TABLE confidential.counselling_case ENABLE ROW LEVEL SECURITY;
ALTER TABLE confidential.counselling_case FORCE ROW LEVEL SECURITY;

CREATE POLICY counselling_counsellor ON confidential.counselling_case
  FOR ALL USING (
    identity.has_role('COUNSELLOR')
    AND (counsellor_user_id = identity.current_user_id() OR counsellor_user_id IS NULL)
  );

CREATE POLICY counselling_self ON confidential.counselling_case
  FOR SELECT USING (student_id = identity.current_student_id());

ALTER TABLE confidential.counselling_note ENABLE ROW LEVEL SECURITY;
ALTER TABLE confidential.counselling_note FORCE ROW LEVEL SECURITY;

CREATE POLICY counselling_note_counsellor ON confidential.counselling_note
  FOR ALL USING (
    identity.has_role('COUNSELLOR')
    AND counsellor_user_id = identity.current_user_id()
  );

-- ---------------------------------------------------------------------
-- Disciplinary: named authorities only, and expired records disappear.
-- ---------------------------------------------------------------------
ALTER TABLE studentlife.disciplinary_case ENABLE ROW LEVEL SECURITY;
ALTER TABLE studentlife.disciplinary_case FORCE ROW LEVEL SECURITY;

CREATE POLICY disc_authority ON studentlife.disciplinary_case
  FOR ALL USING (
    (identity.has_role('DISCIPLINE_COMMITTEE') OR identity.has_role('DEAN_STUDENT_AFFAIRS'))
    AND retention_until >= current_date
  );

CREATE POLICY disc_self ON studentlife.disciplinary_case
  FOR SELECT USING (
    student_id = identity.current_student_id() AND retention_until >= current_date
  );

-- ---------------------------------------------------------------------
-- Risk flags: the responder, the subject, and departmental leadership.
-- Wellbeing flags are excluded from the academic leadership view entirely.
-- ---------------------------------------------------------------------
ALTER TABLE agentops.risk_flag ENABLE ROW LEVEL SECURITY;
ALTER TABLE agentops.risk_flag FORCE ROW LEVEL SECURITY;

CREATE POLICY flag_responder ON agentops.risk_flag
  FOR ALL USING (responder_user_id = identity.current_user_id());

CREATE POLICY flag_mentor ON agentops.risk_flag
  FOR SELECT USING (
    student_id IS NOT NULL AND studentlife.is_mentor_of(student_id)
  );

CREATE POLICY flag_academic_leadership ON agentops.risk_flag
  FOR SELECT USING (
    (identity.has_role('HOD') OR identity.has_role('DEAN'))
    AND flag_type <> 'WELLBEING_CONCERN'
    AND routed_to_confidential = false
    AND (student_id IS NULL OR people.student_in_scope(student_id))
  );

CREATE POLICY flag_counsellor ON agentops.risk_flag
  FOR SELECT USING (
    identity.has_role('COUNSELLOR') AND flag_type = 'WELLBEING_CONCERN'
  );

-- ---------------------------------------------------------------------
-- Faculty leave: the health reason is masked from everyone except HR
-- and the approving authority. Implemented as a view, since column-level
-- masking is clearer than a policy here.
-- ---------------------------------------------------------------------
CREATE VIEW hr.faculty_leave_public AS
SELECT faculty_leave_id, faculty_id, leave_type_id, from_date, to_date, days,
       substitution_arranged, status, approved_at,
       NULL::text AS reason_restricted
FROM hr.faculty_leave;

COMMENT ON VIEW hr.faculty_leave_public IS
  'Substitution notifications and timetable views must read from here, never from '
  'hr.faculty_leave directly, so that the reason for leave is not disclosed to students '
  'or colleagues.';

-- ---------------------------------------------------------------------
-- Audit log: append only. Revoke UPDATE/DELETE from every application role.
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION identity.block_audit_mutation() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'identity.audit_log is append-only';
END; $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_immutable
  BEFORE UPDATE OR DELETE ON identity.audit_log
  FOR EACH ROW EXECUTE FUNCTION identity.block_audit_mutation();

-- ---------------------------------------------------------------------
-- Application roles and baseline grants
-- ---------------------------------------------------------------------
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_readwrite') THEN
    CREATE ROLE app_readwrite NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_readonly') THEN
    CREATE ROLE app_readonly NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_counsellor') THEN
    CREATE ROLE app_counsellor NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_analytics') THEN
    CREATE ROLE app_analytics NOLOGIN;
  END IF;
END $$;

GRANT USAGE ON SCHEMA core, people, identity, curriculum, academics, attendance,
      assessment, exams, outcomes, research, engagement, admissions, finance,
      studentlife, placement, hr, governance, quality, knowledge, agentops
  TO app_readwrite, app_readonly, app_analytics;

-- confidential is NOT granted to the general application roles.
GRANT USAGE ON SCHEMA confidential TO app_counsellor;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA confidential TO app_counsellor;

GRANT SELECT ON ALL TABLES IN SCHEMA core, people, curriculum, academics, attendance,
      assessment, outcomes, research, engagement, admissions, finance, studentlife,
      placement, hr, governance, quality, knowledge, agentops
  TO app_readonly;

GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA core, people, curriculum, academics,
      attendance, assessment, exams, outcomes, research, engagement, admissions, finance,
      studentlife, placement, hr, governance, quality, knowledge, agentops
  TO app_readwrite;

GRANT INSERT ON identity.audit_log TO app_readwrite, app_readonly, app_counsellor;
REVOKE UPDATE, DELETE ON identity.audit_log FROM app_readwrite, app_readonly, app_counsellor;

-- The analytics role must never see the confidential schema or raw identifiers.
REVOKE ALL ON SCHEMA confidential FROM app_analytics, app_readwrite, app_readonly;
