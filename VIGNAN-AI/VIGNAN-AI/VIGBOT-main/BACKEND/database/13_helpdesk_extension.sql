-- =====================================================================
-- 13_helpdesk_extension.sql
-- Missing Helpdesk Extension Schema for VIGBOT
-- Target: PostgreSQL 14+
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS helpdesk;

-- ---------------------------------------------------------------------
-- 1. Multi-turn conversation sessions (Workflow Step 5)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS helpdesk.conversation (
    conversation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id uuid NOT NULL REFERENCES people.student,
    title text NOT NULL DEFAULT 'General Inquiry',
    status text NOT NULL DEFAULT 'ACTIVE'
           CHECK (status IN ('ACTIVE','RESOLVED','CLOSED','ESCALATED')),
    context_data jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_conv_student ON helpdesk.conversation (student_id, updated_at DESC);

-- ---------------------------------------------------------------------
-- 2. Durable message history with citations and classification
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS helpdesk.message (
    message_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id uuid NOT NULL REFERENCES helpdesk.conversation ON DELETE CASCADE,
    sender_role text NOT NULL CHECK (sender_role IN ('STUDENT','AGENT_65','VIGBOT','HUMAN_OFFICER','AGENT_66_COUNSELOR')),
    content text NOT NULL,
    category text CHECK (category IN
        ('PERSONAL_DATA','INSTITUTIONAL_INFO','PROCEDURAL_GUIDANCE','SERVICE_REQUEST','ESCALATION','DISTRESS_SUPPORT','GENERAL')),
    source_agent text DEFAULT 'VIGBOT',
    citations jsonb DEFAULT '[]'::jsonb,
    structured_card jsonb,
    is_distress boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_msg_conv ON helpdesk.message (conversation_id, created_at ASC);

-- ---------------------------------------------------------------------
-- 3. Service requests and ticketing (Workflow Step 7)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS helpdesk.service_request (
    service_request_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    request_no text NOT NULL UNIQUE,
    student_id uuid NOT NULL REFERENCES people.student,
    category text NOT NULL CHECK (category IN
        ('BONAFIDE_CERTIFICATE','FEE_ESTIMATE','GRADE_CARD_TRANSCRIPT','TRANSFER_CERTIFICATE',
         'HOSTEL_MAINTENANCE','ID_CARD_REPLACEMENT','BUS_PASS_ENDORSEMENT','MENTOR_MEETING','GRIEVANCE','OTHER')),
    title text NOT NULL,
    description text NOT NULL,
    priority text NOT NULL DEFAULT 'NORMAL'
             CHECK (priority IN ('LOW','NORMAL','HIGH','URGENT')),
    status text NOT NULL DEFAULT 'SUBMITTED'
           CHECK (status IN ('SUBMITTED','IN_REVIEW','PROCESSING','READY_FOR_COLLECTION','REJECTED','RESOLVED','CLOSED')),
    assigned_office text NOT NULL DEFAULT 'Registrar Student Affairs',
    sla_due_date date,
    conversation_id uuid REFERENCES helpdesk.conversation,
    resolution_notes text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_service_student ON helpdesk.service_request (student_id, status);

-- ---------------------------------------------------------------------
-- 4. Human handover / escalation record (Workflow Step 8)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS helpdesk.handover (
    handover_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    handover_no text NOT NULL UNIQUE,
    student_id uuid NOT NULL REFERENCES people.student,
    conversation_id uuid REFERENCES helpdesk.conversation,
    target_office text NOT NULL CHECK (target_office IN
        ('DEAN_ACADEMICS','EXAMINATION_CELL','BURSAR_FINANCE','HOD_OFFICE','STUDENT_WELFARE','REGISTRAR')),
    reason text NOT NULL,
    conversation_summary text NOT NULL,
    student_action_requested text,
    urgency text NOT NULL DEFAULT 'NORMAL' CHECK (urgency IN ('NORMAL','HIGH','CRITICAL')),
    status text NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','ACCEPTED','IN_PROGRESS','RESOLVED','CLOSED')),
    assigned_to_user_id uuid REFERENCES identity.app_user,
    created_at timestamptz NOT NULL DEFAULT now(),
    resolved_at timestamptz
);
CREATE INDEX IF NOT EXISTS idx_handover_office ON helpdesk.handover (target_office, status);

-- ---------------------------------------------------------------------
-- 5. Privacy-safe daily query analytics (Workflow Step 10)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS helpdesk.query_analytics_daily (
    analytics_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    stat_date date NOT NULL,
    intent_category text NOT NULL,
    topic text NOT NULL,
    language_code text NOT NULL DEFAULT 'en',
    query_count integer NOT NULL DEFAULT 1,
    successful_answers integer NOT NULL DEFAULT 1,
    escalated_count integer NOT NULL DEFAULT 0,
    distress_count integer NOT NULL DEFAULT 0,
    UNIQUE (stat_date, intent_category, topic, language_code)
);
CREATE INDEX IF NOT EXISTS idx_analytics_date ON helpdesk.query_analytics_daily (stat_date, intent_category);

-- ---------------------------------------------------------------------
-- 6. Row-Level Security (RLS) enforcement at the data layer
-- ---------------------------------------------------------------------
ALTER TABLE helpdesk.conversation ENABLE ROW LEVEL SECURITY;
ALTER TABLE helpdesk.conversation FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS conv_student_self ON helpdesk.conversation;
CREATE POLICY conv_student_self ON helpdesk.conversation
  FOR ALL USING (student_id = identity.current_student_id());

DROP POLICY IF EXISTS conv_institution_admin ON helpdesk.conversation;
CREATE POLICY conv_institution_admin ON helpdesk.conversation
  FOR ALL USING (identity.has_role('PRINCIPAL') OR identity.has_role('SYSTEM'));

ALTER TABLE helpdesk.message ENABLE ROW LEVEL SECURITY;
ALTER TABLE helpdesk.message FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS msg_student_self ON helpdesk.message;
CREATE POLICY msg_student_self ON helpdesk.message
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM helpdesk.conversation c
      WHERE c.conversation_id = helpdesk.message.conversation_id
        AND c.student_id = identity.current_student_id()
    )
  );

DROP POLICY IF EXISTS msg_institution_admin ON helpdesk.message;
CREATE POLICY msg_institution_admin ON helpdesk.message
  FOR ALL USING (identity.has_role('PRINCIPAL') OR identity.has_role('SYSTEM'));

ALTER TABLE helpdesk.service_request ENABLE ROW LEVEL SECURITY;
ALTER TABLE helpdesk.service_request FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS sr_student_self ON helpdesk.service_request;
CREATE POLICY sr_student_self ON helpdesk.service_request
  FOR ALL USING (student_id = identity.current_student_id());

DROP POLICY IF EXISTS sr_institution_admin ON helpdesk.service_request;
CREATE POLICY sr_institution_admin ON helpdesk.service_request
  FOR ALL USING (identity.has_role('REGISTRAR') OR identity.has_role('PRINCIPAL') OR identity.has_role('SYSTEM'));

ALTER TABLE helpdesk.handover ENABLE ROW LEVEL SECURITY;
ALTER TABLE helpdesk.handover FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS ho_student_self ON helpdesk.handover;
CREATE POLICY ho_student_self ON helpdesk.handover
  FOR ALL USING (student_id = identity.current_student_id());

-- Register VIGBOT in agentops catalogue if table exists
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'agentops' AND table_name = 'agent') THEN
    INSERT INTO agentops.agent (agent_id, code, agent_no, name, domain, agent_class, scope_statement, reasoning_policy, requires_human_approval, status)
    VALUES (
        'aaaaaaaa-6565-6565-6565-656565656565',
        'VIGBOT',
        65,
        'VIGBOT Campus Assistant',
        'STUDENT_SUPPORT',
        2,
        'Single conversational point of access for authenticated students to academic, attendance, marks, fees, timetable, institutional policies, and service requests.',
        'ACT_WITH_APPROVAL',
        false,
        'ACTIVE'
    ) ON CONFLICT (code) DO UPDATE SET status = 'ACTIVE';

    INSERT INTO agentops.agent_tool (agent_id, tool_name, resource_schema, resource_object, access_mode, row_scope_rule)
    VALUES 
      ('aaaaaaaa-6565-6565-6565-656565656565', 'get_my_profile', 'people', 'v_student_profile', 'READ', 'self'),
      ('aaaaaaaa-6565-6565-6565-656565656565', 'get_my_attendance', 'attendance', 'v_current_attendance', 'READ', 'self'),
      ('aaaaaaaa-6565-6565-6565-656565656565', 'get_my_timetable', 'academics', 'timetable_entry', 'READ', 'self'),
      ('aaaaaaaa-6565-6565-6565-656565656565', 'get_my_marks', 'assessment', 'internal_mark', 'READ', 'self'),
      ('aaaaaaaa-6565-6565-6565-656565656565', 'get_my_exam_schedule', 'exams', 'exam_schedule', 'READ', 'self'),
      ('aaaaaaaa-6565-6565-6565-656565656565', 'get_my_fee_status', 'finance', 'fee_demand', 'READ', 'self'),
      ('aaaaaaaa-6565-6565-6565-656565656565', 'get_my_curriculum_progress', 'curriculum', 'regulation_norm', 'READ', 'self'),
      ('aaaaaaaa-6565-6565-6565-656565656565', 'search_approved_policies', 'governance', 'policy_document', 'READ', 'public'),
      ('aaaaaaaa-6565-6565-6565-656565656565', 'search_approved_circulars', 'governance', 'circular', 'READ', 'public'),
      ('aaaaaaaa-6565-6565-6565-656565656565', 'create_service_request', 'helpdesk', 'service_request', 'WRITE', 'self'),
      ('aaaaaaaa-6565-6565-6565-656565656565', 'create_grievance', 'studentlife', 'grievance', 'WRITE', 'self'),
      ('aaaaaaaa-6565-6565-6565-656565656565', 'book_mentor_meeting', 'studentlife', 'mentor_meeting', 'WRITE', 'self'),
      ('aaaaaaaa-6565-6565-6565-656565656565', 'create_human_handover', 'helpdesk', 'handover', 'WRITE', 'self'),
      ('aaaaaaaa-6565-6565-6565-656565656565', 'escalate_to_agent_66', 'confidential', 'crisis_escalation', 'WRITE', 'emergency')
    ON CONFLICT (agent_id, tool_name, resource_schema, resource_object) DO NOTHING;
  END IF;
END $$;
