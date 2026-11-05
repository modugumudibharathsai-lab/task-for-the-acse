-- =====================================================================
-- 12_views.sql : the read layer agents and dashboards should use.
-- Agents query views, not base tables, so that metric definitions live
-- in one place and cannot drift between agents.
-- =====================================================================

-- Who is registered in what, this term
CREATE VIEW academics.v_offering_roster AS
SELECT co.course_offering_id, co.term_id, t.label AS term_label,
       cv.course_code, c.title AS course_title, cv.credits, cv.course_type,
       sec.code AS section_code, b.label AS batch_label, p.code AS programme_code,
       d.code AS department_code,
       sr.student_id, s.roll_no, per.full_name AS student_name,
       sr.registration_type, sr.attempt_no
FROM academics.course_offering co
JOIN academics.student_registration sr ON sr.course_offering_id = co.course_offering_id
                                      AND sr.status = 'REGISTERED'
JOIN people.student s   ON s.student_id = sr.student_id
JOIN people.person per  ON per.person_id = s.person_id
JOIN curriculum.course_version cv ON cv.course_version_id = co.course_version_id
JOIN curriculum.course c ON c.course_id = cv.course_id
JOIN curriculum.section sec ON sec.section_id = co.section_id
JOIN curriculum.batch b ON b.batch_id = sec.batch_id
JOIN curriculum.programme p ON p.programme_id = b.programme_id
JOIN core.department d ON d.department_id = co.department_id
JOIN core.term t ON t.term_id = co.term_id;

-- Latest attendance position per student per offering
CREATE VIEW attendance.v_current_attendance AS
SELECT DISTINCT ON (student_id, course_offering_id, term_id)
       student_id, course_offering_id, term_id, as_of_date,
       classes_held, classes_attended, raw_pct, adjusted_pct,
       trend_slope, projected_end_pct, band, risk_level
FROM attendance.attendance_summary
ORDER BY student_id, course_offering_id, term_id, as_of_date DESC;

-- Course-level result analysis (Agent 34)
CREATE VIEW assessment.v_course_performance AS
SELECT cr.course_version_id, cv.course_code, c.title AS course_title,
       cr.term_id, co.course_offering_id, co.section_id, co.department_id,
       count(*) AS students_appeared,
       count(*) FILTER (WHERE cr.result_status = 'PASS') AS passed,
       round(100.0 * count(*) FILTER (WHERE cr.result_status = 'PASS')
             / nullif(count(*) FILTER (WHERE cr.result_status <> 'ABSENT'), 0), 2) AS pass_pct,
       round(avg(cr.total_marks), 2) AS avg_total,
       round(avg(cr.internal_marks), 2) AS avg_internal,
       round(avg(cr.external_marks), 2) AS avg_external,
       round(stddev_pop(cr.external_marks), 2) AS sd_external,
       round(corr(cr.internal_marks, cr.external_marks)::numeric, 3) AS internal_external_corr
FROM assessment.course_result cr
JOIN curriculum.course_version cv ON cv.course_version_id = cr.course_version_id
JOIN curriculum.course c ON c.course_id = cv.course_id
LEFT JOIN academics.course_offering co ON co.course_offering_id = cr.course_offering_id
WHERE cr.exam_type = 'REGULAR'
GROUP BY cr.course_version_id, cv.course_code, c.title, cr.term_id,
         co.course_offering_id, co.section_id, co.department_id;

COMMENT ON COLUMN assessment.v_course_performance.internal_external_corr IS
  'A weak or negative correlation is the signal that internal evaluation in this offering '
  'is not discriminating. It is one of the few metrics that detects lenient internal marking.';

-- The evidence chain: PO attainment traceable back to individual questions.
-- This is what a peer team asks for, and what must resolve in seconds.
CREATE VIEW outcomes.v_attainment_trace AS
SELECT po.outcome_type, po.outcome_no, po.statement AS outcome_statement,
       poa.weighted_level AS po_level, poa.target_level AS po_target,
       cvo.co_no, cvo.statement AS co_statement,
       cpm.strength AS mapping_strength,
       coa.direct_level, coa.indirect_level, coa.final_level AS co_level,
       coa.students_evaluated, coa.attaining_pct,
       ar.attainment_run_id, ar.run_at, ar.status AS run_status,
       cofr.course_offering_id, cv.course_code, t.label AS term_label,
       coa.contributing_questions
FROM outcomes.po_attainment poa
JOIN curriculum.programme_outcome po ON po.programme_outcome_id = poa.programme_outcome_id
JOIN curriculum.co_po_map cpm ON cpm.programme_outcome_id = po.programme_outcome_id
JOIN curriculum.course_outcome cvo ON cvo.course_outcome_id = cpm.course_outcome_id
JOIN outcomes.co_attainment coa ON coa.course_outcome_id = cvo.course_outcome_id
JOIN outcomes.attainment_run ar ON ar.attainment_run_id = coa.attainment_run_id
JOIN academics.course_offering cofr ON cofr.course_offering_id = ar.course_offering_id
JOIN curriculum.course_version cv ON cv.course_version_id = cofr.course_version_id
JOIN core.term t ON t.term_id = cofr.term_id;

-- Faculty workload, current term
CREATE VIEW hr.v_current_workload AS
SELECT DISTINCT ON (fw.faculty_id, fw.term_id)
       fw.faculty_id, per.full_name, f.designation, d.code AS department_code,
       fw.term_id, fw.total_weighted_load, fw.norm_expected, fw.variance_pct, fw.status
FROM hr.faculty_workload fw
JOIN people.faculty f ON f.faculty_id = fw.faculty_id
JOIN people.person per ON per.person_id = f.person_id
JOIN core.department d ON d.department_id = f.department_id
ORDER BY fw.faculty_id, fw.term_id, fw.computed_at DESC;

-- Open risk flags awaiting a human, with age
CREATE VIEW agentops.v_open_flags AS
SELECT rf.risk_flag_id, a.code AS agent_code, a.agent_no,
       rf.flag_type, rf.severity, rf.subject_type,
       rf.student_id, rf.faculty_id, rf.course_offering_id,
       rf.deviation_summary, rf.suggested_first_action,
       rf.raised_at, rf.respond_by,
       rf.responder_user_id, rf.status,
       EXTRACT(EPOCH FROM (now() - rf.raised_at))/3600 AS age_hours,
       (rf.respond_by IS NOT NULL AND now() > rf.respond_by) AS is_overdue
FROM agentops.risk_flag rf
JOIN agentops.agent a ON a.agent_id = rf.agent_id
WHERE rf.status IN ('OPEN','ACKNOWLEDGED','IN_PROGRESS');

-- Agent health: is anyone acting on what the agents produce, and are they right?
CREATE VIEW agentops.v_agent_health AS
SELECT a.agent_id, a.code, a.agent_no, a.name, a.agent_class, a.status,
       count(DISTINCT r.agent_run_id)                                   AS runs_30d,
       count(DISTINCT o.agent_output_id)                                AS outputs_30d,
       count(DISTINCT hr2.human_review_id) FILTER (WHERE hr2.decision = 'APPROVE') AS approved,
       count(DISTINCT hr2.human_review_id) FILTER (WHERE hr2.decision = 'REJECT')  AS rejected,
       round(100.0 * count(DISTINCT hr2.human_review_id) FILTER (WHERE hr2.decision = 'REJECT')
             / nullif(count(DISTINCT hr2.human_review_id), 0), 1)       AS reject_rate_pct,
       count(DISTINCT fl.risk_flag_id) FILTER (WHERE fl.confirmed_by_human = false) AS false_positives,
       round(100.0 * count(DISTINCT fl.risk_flag_id) FILTER (WHERE fl.confirmed_by_human = false)
             / nullif(count(DISTINCT fl.risk_flag_id) FILTER (WHERE fl.confirmed_by_human IS NOT NULL), 0), 1)
                                                                        AS false_positive_rate_pct,
       round(avg(fb.rating)::numeric, 2)                                AS avg_feedback
FROM agentops.agent a
LEFT JOIN agentops.agent_run r  ON r.agent_id = a.agent_id AND r.started_at > now() - interval '30 days'
LEFT JOIN agentops.agent_output o ON o.agent_run_id = r.agent_run_id
LEFT JOIN agentops.human_review hr2 ON hr2.agent_output_id = o.agent_output_id
LEFT JOIN agentops.risk_flag fl ON fl.agent_id = a.agent_id AND fl.raised_at > now() - interval '30 days'
LEFT JOIN agentops.agent_feedback fb ON fb.agent_output_id = o.agent_output_id
GROUP BY a.agent_id, a.code, a.agent_no, a.name, a.agent_class, a.status;

COMMENT ON VIEW agentops.v_agent_health IS
  'A reject_rate above roughly 50 percent means the agent is wrong or its inputs are, and '
  'a false_positive_rate trending upward predicts that responders will start ignoring it.';

-- Did interventions work?
CREATE VIEW agentops.v_intervention_effectiveness AS
SELECT i.intervention_type,
       count(DISTINCT i.intervention_id)      AS interventions,
       count(DISTINCT ip.student_id)          AS students_reached,
       round(avg(io.post_value - io.pre_value)::numeric, 2)   AS avg_raw_improvement,
       round(avg(io.comparison_group_delta)::numeric, 2)      AS avg_comparison_delta,
       round(avg(io.net_effect)::numeric, 2)                  AS avg_net_effect,
       sum(io.sample_size)                    AS total_sample
FROM agentops.intervention i
LEFT JOIN agentops.intervention_participant ip ON ip.intervention_id = i.intervention_id
LEFT JOIN agentops.intervention_outcome io ON io.intervention_id = i.intervention_id
WHERE i.status = 'DELIVERED'
GROUP BY i.intervention_type;

-- Latest validated KPI value per scope
CREATE VIEW quality.v_kpi_latest AS
SELECT DISTINCT ON (kd.code, kv.scope_type, kv.scope_id)
       kd.code, kd.name, kd.domain, kd.unit, kd.direction,
       kv.scope_type, kv.scope_id, kv.period_start, kv.period_end,
       kv.value, kv.target_value, kv.variance_pct, kv.trend, kv.status,
       kv.validated_at IS NOT NULL AS is_validated,
       kd.framework_mapping
FROM quality.kpi_value kv
JOIN quality.kpi_definition kd ON kd.kpi_definition_id = kv.kpi_definition_id
WHERE kd.is_active
ORDER BY kd.code, kv.scope_type, kv.scope_id, kv.period_end DESC;

-- Student 360 (Agent 44). Deliberately EXCLUDES confidential and
-- disciplinary data; those require separate authorisation.
CREATE VIEW people.v_student_profile AS
SELECT s.student_id, s.roll_no, per.full_name, s.status,
       p.code AS programme_code, d.code AS department_code,
       b.label AS batch_label, sec.code AS section_code, s.current_year_of_study,
       tr.cgpa, tr.backlog_count,
       (SELECT round(avg(adjusted_pct), 2) FROM attendance.v_current_attendance a
         WHERE a.student_id = s.student_id AND a.course_offering_id IS NULL) AS attendance_pct,
       (SELECT count(*) FROM studentlife.achievement ach
         WHERE ach.student_id = s.student_id AND ach.verification_status = 'VERIFIED') AS verified_achievements,
       (SELECT count(*) FROM studentlife.student_certification sc
         WHERE sc.student_id = s.student_id AND sc.verification_status = 'VERIFIED') AS certifications,
       (SELECT count(*) FROM placement.internship i
         WHERE i.student_id = s.student_id AND i.status = 'COMPLETED') AS internships,
       (SELECT count(*) FROM placement.offer o
         WHERE o.student_id = s.student_id AND o.status IN ('ACCEPTED','JOINED')) AS offers_accepted,
       (SELECT fd.outstanding FROM finance.fee_demand fd
         WHERE fd.student_id = s.student_id ORDER BY fd.created_at DESC LIMIT 1) AS fee_outstanding
FROM people.student s
JOIN people.person per ON per.person_id = s.person_id
JOIN curriculum.batch b ON b.batch_id = s.batch_id
JOIN curriculum.programme p ON p.programme_id = b.programme_id
JOIN core.department d ON d.department_id = p.department_id
LEFT JOIN curriculum.section sec ON sec.section_id = s.current_section_id
LEFT JOIN LATERAL (
    SELECT cgpa, backlog_count FROM assessment.term_result tr2
    WHERE tr2.student_id = s.student_id ORDER BY tr2.published_on DESC NULLS LAST LIMIT 1
) tr ON true;

COMMENT ON VIEW people.v_student_profile IS
  'Aggregation itself creates risk that the individual source systems did not carry. '
  'Counselling, medical and disciplinary data are deliberately absent and must be reached '
  'through their own authorisation path, never through this view.';
