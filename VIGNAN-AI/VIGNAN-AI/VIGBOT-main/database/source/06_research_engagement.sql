-- =====================================================================
-- 06_research_engagement.sql
-- Serves Agents 17-29
-- =====================================================================

CREATE TABLE research.venue (
    venue_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    venue_type   text NOT NULL CHECK (venue_type IN ('JOURNAL','CONFERENCE','BOOK','BOOK_SERIES')),
    name         text NOT NULL,
    short_name   text,
    print_issn   text,
    online_issn  text,
    publisher    text,
    country      text,
    subject_areas text[],
    is_flagged   boolean NOT NULL DEFAULT false,
    flag_reason  text,                    -- delisted / predatory indicators
    UNIQUE (print_issn, online_issn, name)
);
CREATE INDEX idx_venue_name_trgm ON research.venue USING gin (name gin_trgm_ops);

-- Metrics are time-stamped per source. Indexing status changes; a cached
-- value presented as current has cost faculty a year of work.
CREATE TABLE research.venue_metric (
    venue_metric_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    venue_id     uuid NOT NULL REFERENCES research.venue ON DELETE CASCADE,
    source       text NOT NULL CHECK (source IN ('SCOPUS','WOS','JCR','SJR','UGC_CARE','OTHER')),
    metric_year  smallint NOT NULL,
    subject_category text,
    is_indexed   boolean,
    quartile     text CHECK (quartile IN ('Q1','Q2','Q3','Q4','NA')),
    impact_factor numeric(7,3),
    citescore    numeric(7,3),
    sjr          numeric(7,3),
    checked_at   timestamptz NOT NULL DEFAULT now(),
    valid_until  date,
    evidence_url text,
    UNIQUE (venue_id, source, metric_year, subject_category)
);

CREATE TABLE research.publication (
    publication_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    title        text NOT NULL,
    venue_id     uuid REFERENCES research.venue,
    publication_type text NOT NULL CHECK (publication_type IN
                 ('JOURNAL_ARTICLE','CONFERENCE_PAPER','BOOK','BOOK_CHAPTER','REVIEW','PREPRINT')),
    doi          text,
    published_year smallint,
    published_month smallint,
    volume       text, issue text, pages text,
    abstract     text,
    keywords     text[],
    affiliation_verified boolean NOT NULL DEFAULT false,
    review_status text NOT NULL DEFAULT 'PENDING'
                 CHECK (review_status IN ('PENDING','CONFIRMED','DISPUTED','REJECTED','FLAGGED')),
    flag_reason  text,
    UNIQUE (doi)
);
CREATE INDEX idx_pub_year ON research.publication (published_year);
CREATE INDEX idx_pub_title_trgm ON research.publication USING gin (title gin_trgm_ops);

-- Provenance: the same paper arrives from Scopus, WoS and Scholar in
-- different forms. Dedup decisions must be inspectable.
CREATE TABLE research.publication_source (
    publication_source_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    publication_id uuid NOT NULL REFERENCES research.publication ON DELETE CASCADE,
    source       text NOT NULL CHECK (source IN ('SCOPUS','WOS','SCHOLAR','ORCID','CROSSREF','MANUAL','REPOSITORY')),
    external_id  text,
    raw_record   jsonb,
    match_method text CHECK (match_method IN ('DOI','TITLE_AUTHOR','MANUAL')),
    match_confidence numeric(4,3),
    retrieved_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source, external_id)
);

CREATE TABLE research.publication_author (
    publication_author_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    publication_id uuid NOT NULL REFERENCES research.publication ON DELETE CASCADE,
    faculty_id   uuid REFERENCES people.faculty,
    student_id   uuid REFERENCES people.student,
    external_name text,
    external_affiliation text,
    author_order smallint NOT NULL,
    is_corresponding boolean NOT NULL DEFAULT false,
    attribution_status text NOT NULL DEFAULT 'AUTO'
                 CHECK (attribution_status IN ('AUTO','CONFIRMED','AMBIGUOUS','REJECTED')),
    UNIQUE (publication_id, author_order),
    CHECK (faculty_id IS NOT NULL OR student_id IS NOT NULL OR external_name IS NOT NULL)
);
CREATE INDEX idx_pubauthor_faculty ON research.publication_author (faculty_id);

CREATE TABLE research.citation_snapshot (
    citation_snapshot_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_type text NOT NULL CHECK (subject_type IN ('PUBLICATION','FACULTY')),
    publication_id uuid REFERENCES research.publication,
    faculty_id   uuid REFERENCES people.faculty,
    source       text NOT NULL,
    as_of_date   date NOT NULL,
    citation_count integer,
    h_index      smallint,
    i10_index    smallint,
    UNIQUE (subject_type, publication_id, faculty_id, source, as_of_date)
);

CREATE TABLE research.researcher_profile (
    researcher_profile_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id   uuid NOT NULL REFERENCES people.faculty ON DELETE CASCADE,
    platform     text NOT NULL CHECK (platform IN
                 ('GOOGLE_SCHOLAR','ORCID','SCOPUS','WOS','RESEARCHGATE','VIDWAN','LINKEDIN')),
    identifier   text NOT NULL,
    profile_url  text,
    completeness_score numeric(5,2),
    missing_items jsonb,
    last_audited_at timestamptz,
    UNIQUE (faculty_id, platform)
);

CREATE TABLE research.affiliation_variant (
    affiliation_variant_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    variant_text text NOT NULL,
    is_active    boolean NOT NULL DEFAULT true,
    UNIQUE (institution_id, variant_text)
);
COMMENT ON TABLE research.affiliation_variant IS
  'A single institution appears in the literature under many spellings. This table is '
  'the practical determinant of publication sweep recall. Revisit annually.';

-- Patents
CREATE TABLE research.patent (
    patent_id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    title        text NOT NULL,
    application_no text,
    publication_no text,
    grant_no     text,
    jurisdiction text NOT NULL DEFAULT 'IN',
    filing_type  text CHECK (filing_type IN ('PROVISIONAL','COMPLETE','PCT','DESIGN','UTILITY')),
    technology_area text,
    filed_on     date,
    published_on date,
    granted_on   date,
    status       text NOT NULL DEFAULT 'DISCLOSED'
                 CHECK (status IN ('DISCLOSED','FILED','PUBLISHED','EXAMINATION_REQUESTED',
                                   'UNDER_EXAMINATION','GRANTED','REFUSED','ABANDONED','LAPSED')),
    commercialisation_status text,
    UNIQUE (jurisdiction, application_no)
);

CREATE TABLE research.patent_inventor (
    patent_id  uuid NOT NULL REFERENCES research.patent ON DELETE CASCADE,
    faculty_id uuid REFERENCES people.faculty,
    student_id uuid REFERENCES people.student,
    external_name text,
    ownership_share numeric(5,4),
    inventor_order smallint NOT NULL,
    PRIMARY KEY (patent_id, inventor_order)
);

CREATE TABLE research.patent_deadline (
    patent_deadline_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    patent_id  uuid NOT NULL REFERENCES research.patent ON DELETE CASCADE,
    deadline_type text NOT NULL,     -- COMPLETE_SPEC, RFE, FER_RESPONSE, RENEWAL
    due_date   date NOT NULL,
    completed_on date,
    status     text NOT NULL DEFAULT 'PENDING'
               CHECK (status IN ('PENDING','COMPLETED','MISSED','NOT_APPLICABLE')),
    alert_days_before smallint DEFAULT 60
);
CREATE INDEX idx_patent_due ON research.patent_deadline (due_date) WHERE status = 'PENDING';

-- Funding
CREATE TABLE research.funding_agency (
    funding_agency_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code text NOT NULL UNIQUE,           -- DST, ANRF, SERB, MEITY, DRDO, AICTE, UGC
    name text NOT NULL,
    agency_type text CHECK (agency_type IN ('CENTRAL','STATE','INDUSTRY','INTERNATIONAL','NGO')),
    portal_url text
);

CREATE TABLE research.funding_call (
    funding_call_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    funding_agency_id uuid NOT NULL REFERENCES research.funding_agency,
    scheme_name  text NOT NULL,
    title        text NOT NULL,
    research_areas text[],
    eligibility  jsonb,
    funding_ceiling numeric(14,2),
    duration_months smallint,
    published_on date,
    deadline     date,
    call_url     text,
    status       text NOT NULL DEFAULT 'OPEN'
                 CHECK (status IN ('OPEN','EXTENDED','CLOSED','WITHDRAWN')),
    source_checked_at timestamptz
);
CREATE INDEX idx_call_deadline ON research.funding_call (deadline) WHERE status IN ('OPEN','EXTENDED');

CREATE TABLE research.call_faculty_match (
    call_faculty_match_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    funding_call_id uuid NOT NULL REFERENCES research.funding_call ON DELETE CASCADE,
    faculty_id   uuid NOT NULL REFERENCES people.faculty,
    match_score  numeric(5,2),
    match_reason text,
    notified_at  timestamptz,
    outcome      text CHECK (outcome IN ('IGNORED','VIEWED','APPLIED','NOT_ELIGIBLE')),
    UNIQUE (funding_call_id, faculty_id)
);

CREATE TABLE research.proposal (
    proposal_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    funding_call_id uuid REFERENCES research.funding_call,
    pi_faculty_id uuid NOT NULL REFERENCES people.faculty,
    title        text NOT NULL,
    amount_requested numeric(14,2),
    duration_months smallint,
    submitted_on date,
    status       text NOT NULL DEFAULT 'DRAFT'
                 CHECK (status IN ('DRAFT','INTERNAL_REVIEW','SUBMITTED','UNDER_REVIEW',
                                   'SANCTIONED','REJECTED','WITHDRAWN')),
    outcome_date date,
    reviewer_comments text
);

CREATE TABLE research.project (
    project_id   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id  uuid REFERENCES research.proposal,
    funding_agency_id uuid REFERENCES research.funding_agency,
    title        text NOT NULL,
    sanction_no  text,
    pi_faculty_id uuid NOT NULL REFERENCES people.faculty,
    sanctioned_amount numeric(14,2),
    received_amount numeric(14,2),
    start_date   date, end_date date,
    project_type text CHECK (project_type IN ('RESEARCH','CONSULTANCY','SEED','INDUSTRY','INTERNATIONAL')),
    status       text NOT NULL DEFAULT 'ACTIVE'
                 CHECK (status IN ('SANCTIONED','ACTIVE','EXTENDED','COMPLETED','TERMINATED'))
);

CREATE TABLE research.project_member (
    project_id uuid NOT NULL REFERENCES research.project ON DELETE CASCADE,
    faculty_id uuid REFERENCES people.faculty,
    student_id uuid REFERENCES people.student,
    role       text NOT NULL CHECK (role IN ('CO_PI','MENTOR','JRF','SRF','RA','PROJECT_STAFF')),
    from_date  date, to_date date,
    PRIMARY KEY (project_id, faculty_id, student_id, role)
);

-- Doctoral programme
CREATE TABLE research.phd_scholar (
    phd_scholar_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id    uuid NOT NULL REFERENCES people.person,
    registration_no text NOT NULL UNIQUE,
    department_id uuid NOT NULL REFERENCES core.department,
    supervisor_faculty_id uuid NOT NULL REFERENCES people.faculty,
    co_supervisor_faculty_id uuid REFERENCES people.faculty,
    mode         text NOT NULL CHECK (mode IN ('FULL_TIME','PART_TIME','EXTERNAL')),
    research_area text,
    registered_on date NOT NULL,
    min_duration_months smallint,
    max_duration_months smallint,
    thesis_title text,
    status       text NOT NULL DEFAULT 'REGISTERED'
                 CHECK (status IN ('REGISTERED','COURSEWORK','RESEARCH','SUBMITTED',
                                   'AWARDED','WITHDRAWN','TERMINATED','LAPSED')),
    awarded_on   date
);
CREATE INDEX idx_phd_supervisor ON research.phd_scholar (supervisor_faculty_id, status);

CREATE TABLE research.phd_milestone (
    phd_milestone_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    phd_scholar_id uuid NOT NULL REFERENCES research.phd_scholar ON DELETE CASCADE,
    milestone_type text NOT NULL CHECK (milestone_type IN
                 ('COURSEWORK','COMPREHENSIVE_EXAM','PROPOSAL_DEFENCE','DC_REVIEW',
                  'PUBLICATION_REQUIREMENT','PRE_SUBMISSION_SEMINAR','SYNOPSIS','THESIS_SUBMISSION','VIVA')),
    sequence_no  smallint,
    due_date     date,
    completed_on date,
    status       text NOT NULL DEFAULT 'PENDING'
                 CHECK (status IN ('PENDING','IN_PROGRESS','COMPLETED','OVERDUE','WAIVED')),
    outcome      text,
    remarks      text
);
CREATE INDEX idx_phd_milestone_due ON research.phd_milestone (due_date) WHERE status = 'PENDING';

CREATE TABLE research.collaboration (
    collaboration_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id   uuid NOT NULL REFERENCES people.faculty,
    partner_type text NOT NULL CHECK (partner_type IN
                 ('INTERNAL_FACULTY','UNIVERSITY','LAB','INDUSTRY','INTERNATIONAL')),
    partner_name text NOT NULL,
    partner_faculty_id uuid REFERENCES people.faculty,
    area         text,
    origin       text CHECK (origin IN ('SUGGESTED','ORGANIC','MOU')),
    suggested_by_agent text,
    status       text NOT NULL DEFAULT 'SUGGESTED'
                 CHECK (status IN ('SUGGESTED','INITIATED','ACTIVE','DORMANT','CONCLUDED')),
    outcome_publication_ids uuid[],
    started_on   date
);

-- =====================================================================
-- ENGAGEMENT : events, industry, outreach (Agents 26-29)
-- =====================================================================

CREATE TABLE engagement.event (
    event_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    department_id uuid REFERENCES core.department,
    event_type   text NOT NULL CHECK (event_type IN
                 ('CONFERENCE','FDP','WORKSHOP','SEMINAR','WEBINAR','STTP','BOOTCAMP','HACKATHON')),
    title        text NOT NULL,
    from_date    date NOT NULL, to_date date NOT NULL,
    mode         text CHECK (mode IN ('OFFLINE','ONLINE','HYBRID')),
    coordinator_faculty_id uuid REFERENCES people.faculty,
    funding_source text,
    budget_sanctioned numeric(12,2),
    expenditure  numeric(12,2),
    participant_target smallint,
    status       text NOT NULL DEFAULT 'PROPOSED'
                 CHECK (status IN ('PROPOSED','APPROVED','OPEN','ONGOING','COMPLETED','CANCELLED')),
    report_ref   uuid,
    CHECK (to_date >= from_date)
);

CREATE TABLE engagement.event_participant (
    event_participant_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id     uuid NOT NULL REFERENCES engagement.event ON DELETE CASCADE,
    person_id    uuid REFERENCES people.person,
    external_name text, external_org text, external_email text,
    participant_role text NOT NULL DEFAULT 'PARTICIPANT'
                 CHECK (participant_role IN ('PARTICIPANT','RESOURCE_PERSON','ORGANISER','CHAIR','REVIEWER','VOLUNTEER')),
    registered_at timestamptz,
    attendance_days smallint,
    attendance_pct numeric(5,2),
    pre_score numeric(5,2), post_score numeric(5,2),
    certificate_no text UNIQUE,
    certificate_issued_on date,
    feedback     jsonb
);
CREATE INDEX idx_event_participant ON engagement.event_participant (person_id, event_id);

CREATE TABLE engagement.event_submission (
    event_submission_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id   uuid NOT NULL REFERENCES engagement.event ON DELETE CASCADE,
    track      text,
    title      text NOT NULL,
    abstract   text,
    file_ref   text,
    similarity_pct numeric(5,2),
    status     text NOT NULL DEFAULT 'SUBMITTED'
               CHECK (status IN ('SUBMITTED','UNDER_REVIEW','ACCEPTED','REVISION','REJECTED','WITHDRAWN','CAMERA_READY')),
    decision_on date
);

CREATE TABLE engagement.review_assignment (
    review_assignment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_submission_id uuid NOT NULL REFERENCES engagement.event_submission ON DELETE CASCADE,
    reviewer_person_id uuid REFERENCES people.person,
    reviewer_external  text,
    assigned_on date, due_on date, submitted_on date,
    score numeric(5,2),
    recommendation text CHECK (recommendation IN ('ACCEPT','WEAK_ACCEPT','BORDERLINE','WEAK_REJECT','REJECT')),
    comments text,
    conflict_declared boolean NOT NULL DEFAULT false
);

CREATE TABLE engagement.industry_partner (
    industry_partner_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    name       text NOT NULL,
    sector     text,
    website    text,
    contact_person text, contact_email text, contact_phone text,
    relationship_owner_faculty_id uuid REFERENCES people.faculty,
    engagement_score numeric(5,2),
    last_activity_on date,
    status     text NOT NULL DEFAULT 'ACTIVE'
               CHECK (status IN ('PROSPECT','ACTIVE','DORMANT','CONCLUDED')),
    UNIQUE (institution_id, name)
);

CREATE TABLE engagement.mou (
    mou_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_partner_id uuid REFERENCES engagement.industry_partner,
    partner_name text NOT NULL,
    partner_type text CHECK (partner_type IN ('INDUSTRY','UNIVERSITY','RESEARCH_LAB','NGO','GOVERNMENT','INTERNATIONAL')),
    title      text NOT NULL,
    scope      text,
    signed_on  date NOT NULL,
    valid_from date, valid_until date,
    owner_faculty_id uuid REFERENCES people.faculty,
    document_ref uuid,
    status     text NOT NULL DEFAULT 'ACTIVE'
               CHECK (status IN ('DRAFT','ACTIVE','EXPIRED','RENEWED','TERMINATED')),
    renewal_alert_days smallint DEFAULT 90
);

CREATE TABLE engagement.mou_deliverable (
    mou_deliverable_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    mou_id     uuid NOT NULL REFERENCES engagement.mou ON DELETE CASCADE,
    description text NOT NULL,
    deliverable_type text,
    target_count smallint,
    achieved_count smallint NOT NULL DEFAULT 0,
    due_date   date,
    status     text NOT NULL DEFAULT 'PENDING'
               CHECK (status IN ('PENDING','IN_PROGRESS','ACHIEVED','NOT_ACHIEVED'))
);

CREATE TABLE engagement.industry_activity (
    industry_activity_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_partner_id uuid REFERENCES engagement.industry_partner,
    mou_id     uuid REFERENCES engagement.mou,
    department_id uuid REFERENCES core.department,
    activity_type text NOT NULL CHECK (activity_type IN
               ('INDUSTRY_VISIT','GUEST_LECTURE','EXPERT_TALK','SPONSORED_PROJECT',
                'INTERNSHIP_DRIVE','FACULTY_EXCHANGE','LAB_SUPPORT','CONSULTANCY')),
    title      text NOT NULL,
    activity_date date NOT NULL,
    course_version_id uuid REFERENCES curriculum.course_version,  -- topical alignment
    participant_count smallint,
    feedback_summary text,
    evidence_ref uuid
);

CREATE TABLE engagement.outreach_activity (
    outreach_activity_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id uuid NOT NULL REFERENCES core.institution,
    department_id uuid REFERENCES core.department,
    activity_type text NOT NULL CHECK (activity_type IN
               ('SCHOOL_OUTREACH','AWARENESS','COMMUNITY_SERVICE','ENVIRONMENT',
                'HEALTH_CAMP','SKILL_TRAINING','DISASTER_RELIEF','NSS','NCC')),
    title      text NOT NULL,
    activity_date date NOT NULL, end_date date,
    location   text,
    partner_organisation text,
    beneficiary_count integer,
    volunteer_hours numeric(8,2),
    sdg_codes  smallint[],
    accreditation_criteria text[],
    media_refs uuid[],
    consent_obtained boolean NOT NULL DEFAULT false,
    coordinator_faculty_id uuid REFERENCES people.faculty
);

CREATE TABLE engagement.outreach_participant (
    outreach_activity_id uuid NOT NULL REFERENCES engagement.outreach_activity ON DELETE CASCADE,
    person_id  uuid NOT NULL REFERENCES people.person,
    role       text CHECK (role IN ('VOLUNTEER','ORGANISER','FACULTY_LEAD')),
    hours      numeric(6,2),
    PRIMARY KEY (outreach_activity_id, person_id)
);

SELECT core.add_audit_columns('research.publication');
SELECT core.add_audit_columns('research.patent');
SELECT core.add_audit_columns('research.project');
SELECT core.add_audit_columns('research.phd_scholar');
SELECT core.add_audit_columns('engagement.event');
SELECT core.add_audit_columns('engagement.mou');
SELECT core.add_audit_columns('engagement.outreach_activity');
