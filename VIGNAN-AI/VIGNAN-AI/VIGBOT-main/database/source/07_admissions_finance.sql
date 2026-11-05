-- =====================================================================
-- 07_admissions_finance.sql  : Agents 36-43
-- =====================================================================

CREATE TABLE admissions.enquiry (
    enquiry_id   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    enquirer_name text,
    phone text, email text,
    programme_interest_id uuid REFERENCES curriculum.programme,
    source       text CHECK (source IN ('WEBSITE','WHATSAPP','PHONE','WALK_IN','EMAIL','CAMPAIGN','REFERRAL')),
    campaign_code text,
    channel_detail text,
    language     text,
    intent_score numeric(5,2),
    status       text NOT NULL DEFAULT 'NEW'
                 CHECK (status IN ('NEW','CONTACTED','QUALIFIED','APPLIED','ENROLLED','LOST','DUPLICATE')),
    lost_reason  text,
    consent_to_contact boolean NOT NULL DEFAULT false,
    handled_by_agent text,
    escalated_to_user_id uuid REFERENCES identity.app_user,
    received_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_enquiry_status ON admissions.enquiry (status, received_at);

CREATE TABLE admissions.enquiry_interaction (
    enquiry_interaction_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    enquiry_id  uuid NOT NULL REFERENCES admissions.enquiry ON DELETE CASCADE,
    occurred_at timestamptz NOT NULL DEFAULT now(),
    direction   text CHECK (direction IN ('INBOUND','OUTBOUND')),
    channel     text,
    handled_by  text,                     -- agent code or user id
    summary     text,
    knowledge_citations jsonb             -- which KB clauses backed the answer
);

CREATE TABLE admissions.cutoff_history (
    cutoff_history_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    programme_id uuid NOT NULL REFERENCES curriculum.programme,
    admission_year smallint NOT NULL,
    exam_code   text NOT NULL,            -- EAPCET, JEE, GATE
    category    text NOT NULL,
    round_no    smallint,
    opening_rank integer, closing_rank integer,
    seats_offered smallint, seats_filled smallint,
    UNIQUE (programme_id, admission_year, exam_code, category, round_no)
);

CREATE TABLE admissions.application (
    application_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    application_no text NOT NULL UNIQUE,
    enquiry_id   uuid REFERENCES admissions.enquiry,
    person_id    uuid REFERENCES people.person,
    applicant_name text NOT NULL,
    date_of_birth date, gender text,
    phone text, email text,
    social_category text, is_differently_abled boolean,
    admission_year smallint NOT NULL,
    admission_route text CHECK (admission_route IN ('CONVENER','MANAGEMENT','LATERAL','NRI','SPOT','SPONSORED')),
    exam_code text, exam_rank integer, exam_score numeric(8,2),
    qualifying_exam jsonb,               -- board, year, subject marks
    programme_preferences uuid[],
    status       text NOT NULL DEFAULT 'DRAFT'
                 CHECK (status IN ('DRAFT','SUBMITTED','DOCUMENT_PENDING','VERIFIED',
                                   'COUNSELLED','ALLOTTED','ENROLLED','REJECTED','WITHDRAWN')),
    submitted_at timestamptz
);
CREATE INDEX idx_application_year_status ON admissions.application (admission_year, status);

CREATE TABLE admissions.application_document (
    application_document_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id uuid NOT NULL REFERENCES admissions.application ON DELETE CASCADE,
    document_type text NOT NULL,          -- SSC, HSC, TC, CASTE, INCOME, AADHAAR, RANK_CARD
    is_required   boolean NOT NULL DEFAULT true,
    file_ref      text,
    uploaded_at   timestamptz,
    extraction_job_id uuid,               -- knowledge.extraction_job
    extracted_fields jsonb,
    extraction_confidence numeric(4,3),
    discrepancies jsonb,                  -- e.g. name mismatch across documents
    verification_status text NOT NULL DEFAULT 'PENDING'
                 CHECK (verification_status IN ('PENDING','AUTO_FLAGGED','HUMAN_REVIEW','VERIFIED','REJECTED','RESUBMIT')),
    verified_by_user_id uuid REFERENCES identity.app_user,
    verified_at   timestamptz,
    UNIQUE (application_id, document_type)
);
COMMENT ON COLUMN admissions.application_document.verification_status IS
  'AUTO_FLAGGED never means rejected. Only a human sets REJECTED. OCR error rates on '
  'scanned certificates are material and a wrong rejection costs an academic year.';

CREATE TABLE admissions.counselling_session (
    counselling_session_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id uuid NOT NULL REFERENCES admissions.application,
    counsellor_user_id uuid REFERENCES identity.app_user,
    session_at   timestamptz NOT NULL DEFAULT now(),
    mode         text,
    candidate_goals text,
    agent_recommendations jsonb,          -- ranked programmes + probability + reasoning
    counsellor_notes text,
    outcome      text
);

CREATE TABLE admissions.seat_allotment (
    seat_allotment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id uuid NOT NULL REFERENCES admissions.application,
    programme_id uuid NOT NULL REFERENCES curriculum.programme,
    round_no    smallint NOT NULL DEFAULT 1,
    allotted_on date,
    status      text NOT NULL DEFAULT 'ALLOTTED'
                CHECK (status IN ('ALLOTTED','ACCEPTED','DECLINED','CANCELLED','UPGRADED')),
    UNIQUE (application_id, round_no)
);

CREATE TABLE admissions.enrolment (
    enrolment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id uuid NOT NULL UNIQUE REFERENCES admissions.application,
    student_id   uuid NOT NULL UNIQUE REFERENCES people.student,
    enrolled_on  date NOT NULL,
    reported_on  date
);

-- =====================================================================
-- FINANCE : Agents 40-43
-- =====================================================================

CREATE TABLE finance.fee_head (
    fee_head_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    code text NOT NULL, name text NOT NULL,
    head_type text CHECK (head_type IN ('TUITION','HOSTEL','TRANSPORT','EXAM','LAB','LIBRARY','CAUTION','ONE_TIME','OTHER')),
    is_refundable boolean NOT NULL DEFAULT false,
    allocation_priority smallint NOT NULL DEFAULT 100,  -- partial payment waterfall
    UNIQUE (institution_id, code)
);

CREATE TABLE finance.fee_structure (
    fee_structure_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    programme_id uuid NOT NULL REFERENCES curriculum.programme,
    regulation_id uuid REFERENCES curriculum.regulation,
    admission_year smallint NOT NULL,
    admission_route text,
    year_of_study smallint NOT NULL,
    version      smallint NOT NULL DEFAULT 1,
    effective_from date NOT NULL,
    effective_to date,
    approved_by  uuid REFERENCES identity.app_user,
    UNIQUE (programme_id, admission_year, admission_route, year_of_study, version)
);

CREATE TABLE finance.fee_structure_line (
    fee_structure_id uuid NOT NULL REFERENCES finance.fee_structure ON DELETE CASCADE,
    fee_head_id  uuid NOT NULL REFERENCES finance.fee_head,
    amount       numeric(12,2) NOT NULL CHECK (amount >= 0),
    PRIMARY KEY (fee_structure_id, fee_head_id)
);

CREATE TABLE finance.fee_demand (
    fee_demand_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id   uuid NOT NULL REFERENCES people.student,
    academic_year_id uuid NOT NULL REFERENCES core.academic_year,
    fee_structure_id uuid REFERENCES finance.fee_structure,
    gross_amount numeric(12,2) NOT NULL,
    concession_amount numeric(12,2) NOT NULL DEFAULT 0,
    scholarship_expected numeric(12,2) NOT NULL DEFAULT 0,
    net_payable  numeric(12,2) NOT NULL,
    paid_amount  numeric(12,2) NOT NULL DEFAULT 0,
    outstanding  numeric(12,2) GENERATED ALWAYS AS (net_payable - paid_amount) STORED,
    due_date     date,
    status       text NOT NULL DEFAULT 'OPEN'
                 CHECK (status IN ('OPEN','PARTIAL','SETTLED','WAIVED','WRITTEN_OFF')),
    UNIQUE (student_id, academic_year_id)
);
CREATE INDEX idx_demand_outstanding ON finance.fee_demand (status, due_date);

CREATE TABLE finance.fee_demand_line (
    fee_demand_line_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fee_demand_id uuid NOT NULL REFERENCES finance.fee_demand ON DELETE CASCADE,
    fee_head_id  uuid NOT NULL REFERENCES finance.fee_head,
    amount       numeric(12,2) NOT NULL,
    concession   numeric(12,2) NOT NULL DEFAULT 0,
    net_amount   numeric(12,2) NOT NULL,
    paid_amount  numeric(12,2) NOT NULL DEFAULT 0,
    UNIQUE (fee_demand_id, fee_head_id)
);

CREATE TABLE finance.installment_plan (
    installment_plan_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fee_demand_id uuid NOT NULL REFERENCES finance.fee_demand ON DELETE CASCADE,
    installment_no smallint NOT NULL,
    amount      numeric(12,2) NOT NULL,
    due_date    date NOT NULL,
    status      text NOT NULL DEFAULT 'PENDING'
                CHECK (status IN ('PENDING','PAID','OVERDUE','WAIVED')),
    approved_by uuid REFERENCES identity.app_user,
    UNIQUE (fee_demand_id, installment_no)
);

CREATE TABLE finance.payment (
    payment_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  uuid NOT NULL REFERENCES people.student,
    amount      numeric(12,2) NOT NULL CHECK (amount > 0),
    payment_mode text NOT NULL CHECK (payment_mode IN ('ONLINE','NEFT','CHEQUE','DD','CASH','SCHOLARSHIP','LOAN')),
    channel     text,
    transaction_ref text,
    paid_on     date NOT NULL,
    received_on date,
    receipt_no  text UNIQUE,
    status      text NOT NULL DEFAULT 'RECEIVED'
                CHECK (status IN ('INITIATED','RECEIVED','RECONCILED','FAILED','REVERSED')),
    reconciled_at timestamptz,
    UNIQUE (payment_mode, transaction_ref)
);
CREATE INDEX idx_payment_student ON finance.payment (student_id, paid_on);

CREATE TABLE finance.payment_allocation (
    payment_id  uuid NOT NULL REFERENCES finance.payment ON DELETE CASCADE,
    fee_demand_line_id uuid NOT NULL REFERENCES finance.fee_demand_line,
    amount      numeric(12,2) NOT NULL CHECK (amount > 0),
    PRIMARY KEY (payment_id, fee_demand_line_id)
);

CREATE TABLE finance.refund (
    refund_id   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  uuid NOT NULL REFERENCES people.student,
    reason      text NOT NULL CHECK (reason IN ('WITHDRAWAL','CANCELLATION','EXCESS','CAUTION_DEPOSIT','OTHER')),
    withdrawal_date date,
    eligible_amount numeric(12,2),
    approved_amount numeric(12,2),
    policy_applied text,
    status      text NOT NULL DEFAULT 'REQUESTED'
                CHECK (status IN ('REQUESTED','APPROVED','PAID','REJECTED')),
    approved_by uuid REFERENCES identity.app_user,
    paid_on     date
);

CREATE TABLE finance.reminder_dispatch (
    reminder_dispatch_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  uuid NOT NULL REFERENCES people.student,
    fee_demand_id uuid REFERENCES finance.fee_demand,
    segment     text NOT NULL CHECK (segment IN
                ('FORGOTTEN','AWAITING_SCHOLARSHIP','ON_PLAN','HARDSHIP','PERSISTENT')),
    escalation_level smallint NOT NULL DEFAULT 1,
    channel     text NOT NULL,
    message_ref text,
    suppressed  boolean NOT NULL DEFAULT false,
    suppression_reason text,
    sent_at     timestamptz,
    delivered_at timestamptz,
    responded   boolean
);
COMMENT ON COLUMN finance.reminder_dispatch.suppressed IS
  'Reminders MUST be suppressed where a sanctioned scholarship or approved installment '
  'plan covers the dues. This is the most common cause of avoidable distress in fee follow-up.';

CREATE TABLE finance.scholarship_scheme (
    scholarship_scheme_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code text NOT NULL UNIQUE, name text NOT NULL,
    provider_type text CHECK (provider_type IN ('CENTRAL','STATE','INSTITUTIONAL','PRIVATE','CORPORATE','ALUMNI')),
    provider_name text,
    benefit_type text CHECK (benefit_type IN ('FULL_TUITION','PARTIAL','FIXED_AMOUNT','MAINTENANCE')),
    benefit_amount numeric(12,2),
    eligibility_criteria jsonb NOT NULL,   -- machine-evaluable rules
    required_documents text[],
    application_opens date, application_closes date,
    renewal_required boolean NOT NULL DEFAULT false,
    renewal_criteria jsonb,
    academic_year_id uuid REFERENCES core.academic_year,
    is_active boolean NOT NULL DEFAULT true
);

CREATE TABLE finance.scholarship_eligibility (
    scholarship_eligibility_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scholarship_scheme_id uuid NOT NULL REFERENCES finance.scholarship_scheme ON DELETE CASCADE,
    student_id  uuid NOT NULL REFERENCES people.student,
    evaluated_at timestamptz NOT NULL DEFAULT now(),
    is_eligible boolean NOT NULL,
    criteria_result jsonb,
    notified_at timestamptz,
    UNIQUE (scholarship_scheme_id, student_id, evaluated_at)
);

CREATE TABLE finance.scholarship_application (
    scholarship_application_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scholarship_scheme_id uuid NOT NULL REFERENCES finance.scholarship_scheme,
    student_id  uuid NOT NULL REFERENCES people.student,
    academic_year_id uuid NOT NULL REFERENCES core.academic_year,
    external_application_no text,
    applied_on  date,
    status      text NOT NULL DEFAULT 'DRAFT'
                CHECK (status IN ('DRAFT','SUBMITTED','INSTITUTION_VERIFIED','SANCTIONED',
                                  'DISBURSED','REJECTED','LAPSED')),
    rejection_reason text,
    sanctioned_amount numeric(12,2),
    disbursed_amount numeric(12,2),
    disbursed_on date,
    payment_id  uuid REFERENCES finance.payment,
    UNIQUE (scholarship_scheme_id, student_id, academic_year_id)
);

CREATE TABLE finance.scholarship_renewal_risk (
    scholarship_renewal_risk_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scholarship_application_id uuid NOT NULL REFERENCES finance.scholarship_application ON DELETE CASCADE,
    assessed_on date NOT NULL,
    attendance_pct numeric(5,2),
    cgpa numeric(4,2),
    criteria_at_risk jsonb,
    risk_level text CHECK (risk_level IN ('NONE','WATCH','AT_RISK','LIKELY_LOSS')),
    alerted_at timestamptz
);

CREATE TABLE finance.loan_document_request (
    loan_document_request_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  uuid NOT NULL REFERENCES people.student,
    bank_name   text,
    document_type text NOT NULL CHECK (document_type IN
                ('BONAFIDE','FEE_STRUCTURE','ADMISSION_CONFIRMATION','FEE_PAID_STATEMENT','ACADEMIC_STATUS')),
    requested_on date NOT NULL DEFAULT current_date,
    status      text NOT NULL DEFAULT 'REQUESTED'
                CHECK (status IN ('REQUESTED','IN_PROGRESS','ISSUED','REJECTED')),
    issued_on   date,
    issued_by   uuid REFERENCES identity.app_user,
    verification_code text UNIQUE,
    document_ref uuid,
    turnaround_hours numeric(8,2)
);

SELECT core.add_audit_columns('admissions.application');
SELECT core.add_audit_columns('admissions.application_document');
SELECT core.add_audit_columns('finance.fee_structure');
SELECT core.add_audit_columns('finance.fee_demand');
SELECT core.add_audit_columns('finance.payment');
SELECT core.add_audit_columns('finance.scholarship_application');
