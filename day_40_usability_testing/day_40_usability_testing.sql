-- PostgreSQL 15+
-- Usability research database for moderated studies, task evidence,
-- problem triage, and design-iteration comparisons.
--
-- Run in a dedicated learning database:
--   psql -v ON_ERROR_STOP=1 -d usability_lab -f usability_testing.sql
--
-- The schema separates plans, participants, sessions, observations, findings,
-- and iteration metrics so that a design decision can be traced to evidence.
-- Participant identifiers are pseudonymous. Avoid storing unnecessary personal
-- data or recording consent-sensitive content in free-text observations.

BEGIN;

CREATE SCHEMA IF NOT EXISTS usability_lab;
SET search_path TO usability_lab, public;

CREATE TYPE session_mode AS ENUM ('moderated', 'unmoderated');
CREATE TYPE task_outcome AS ENUM ('success', 'partial', 'failure', 'abandoned');
CREATE TYPE evidence_kind AS ENUM ('observed', 'participant_reported', 'inferred');
CREATE TYPE problem_severity AS ENUM ('cosmetic', 'minor', 'major', 'critical');
CREATE TYPE finding_status AS ENUM (
    'open',
    'in_progress',
    'fixed',
    'verified',
    'accepted_risk'
);

CREATE TABLE studies (
    study_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    study_code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    objective TEXT NOT NULL,
    environment TEXT NOT NULL,
    target_participants INTEGER NOT NULL CHECK (target_participants > 0),
    recruitment_criteria JSONB NOT NULL DEFAULT '[]'::jsonb,
    moderator_script JSONB NOT NULL DEFAULT '[]'::jsonb,
    analysis_plan TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (jsonb_typeof(recruitment_criteria) = 'array'),
    CHECK (jsonb_typeof(moderator_script) = 'array')
);

CREATE TABLE research_questions (
    question_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    study_id BIGINT NOT NULL REFERENCES studies(study_id) ON DELETE CASCADE,
    question_code TEXT NOT NULL,
    question_text TEXT NOT NULL,
    supported_decision TEXT NOT NULL,
    UNIQUE (study_id, question_code)
);

CREATE TABLE study_tasks (
    task_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    study_id BIGINT NOT NULL REFERENCES studies(study_id) ON DELETE CASCADE,
    task_code TEXT NOT NULL,
    scenario TEXT NOT NULL,
    expected_outcome TEXT NOT NULL,
    success_criteria JSONB NOT NULL,
    time_limit_seconds INTEGER NOT NULL CHECK (time_limit_seconds > 0),
    task_order INTEGER NOT NULL CHECK (task_order > 0),
    UNIQUE (study_id, task_code),
    UNIQUE (study_id, task_order),
    CHECK (
        jsonb_typeof(success_criteria) = 'array'
        AND jsonb_array_length(success_criteria) > 0
    )
);

CREATE TABLE participants (
    participant_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    study_id BIGINT NOT NULL REFERENCES studies(study_id) ON DELETE CASCADE,
    pseudonym TEXT NOT NULL,
    role_name TEXT NOT NULL,
    experience_level TEXT NOT NULL
        CHECK (experience_level IN ('frequent', 'occasional', 'novice')),
    consent_recorded BOOLEAN NOT NULL DEFAULT FALSE,
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (study_id, pseudonym),
    CHECK (consent_recorded = TRUE)
);

CREATE TABLE sessions (
    session_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    study_id BIGINT NOT NULL REFERENCES studies(study_id) ON DELETE CASCADE,
    participant_id BIGINT NOT NULL REFERENCES participants(participant_id),
    task_id BIGINT NOT NULL REFERENCES study_tasks(task_id),
    mode session_mode NOT NULL,
    outcome task_outcome NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    duration_seconds NUMERIC(10, 2),
    error_count INTEGER NOT NULL DEFAULT 0 CHECK (error_count >= 0),
    assistance_requests INTEGER NOT NULL DEFAULT 0 CHECK (assistance_requests >= 0),
    confidence_rating SMALLINT CHECK (confidence_rating BETWEEN 1 AND 5),
    moderator_notes TEXT NOT NULL DEFAULT '',
    UNIQUE (participant_id, task_id),
    CHECK (ended_at IS NULL OR ended_at >= started_at),
    CHECK (duration_seconds IS NULL OR duration_seconds >= 0),
    CHECK (
        (outcome IN ('success', 'partial') AND duration_seconds > 0)
        OR outcome IN ('failure', 'abandoned')
        OR duration_seconds IS NULL
    )
);

CREATE TABLE observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    elapsed_seconds NUMERIC(10, 2) NOT NULL CHECK (elapsed_seconds >= 0),
    event_type TEXT NOT NULL,
    target_element TEXT NOT NULL,
    description TEXT NOT NULL,
    evidence_type evidence_kind NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (session_id, elapsed_seconds, event_type, target_element)
);

CREATE TABLE usability_problems (
    problem_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    study_id BIGINT NOT NULL REFERENCES studies(study_id) ON DELETE CASCADE,
    problem_code TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity problem_severity NOT NULL,
    impact NUMERIC(4, 3) NOT NULL CHECK (impact BETWEEN 0 AND 1),
    proposed_change TEXT NOT NULL,
    status finding_status NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (study_id, problem_code)
);

CREATE TABLE problem_tasks (
    problem_id BIGINT NOT NULL REFERENCES usability_problems(problem_id) ON DELETE CASCADE,
    task_id BIGINT NOT NULL REFERENCES study_tasks(task_id),
    PRIMARY KEY (problem_id, task_id)
);

CREATE TABLE problem_evidence (
    evidence_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    problem_id BIGINT NOT NULL REFERENCES usability_problems(problem_id) ON DELETE CASCADE,
    observation_id BIGINT REFERENCES observations(observation_id) ON DELETE SET NULL,
    evidence_type evidence_kind NOT NULL,
    evidence_statement TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE design_iterations (
    iteration_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    study_id BIGINT NOT NULL REFERENCES studies(study_id) ON DELETE CASCADE,
    version_label TEXT NOT NULL,
    description TEXT NOT NULL,
    prototype_reference TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (study_id, version_label)
);

CREATE TABLE iteration_task_metrics (
    iteration_id BIGINT NOT NULL REFERENCES design_iterations(iteration_id) ON DELETE CASCADE,
    task_id BIGINT NOT NULL REFERENCES study_tasks(task_id),
    participant_count INTEGER NOT NULL CHECK (participant_count >= 0),
    success_count INTEGER NOT NULL CHECK (success_count >= 0),
    partial_count INTEGER NOT NULL CHECK (partial_count >= 0),
    failure_count INTEGER NOT NULL CHECK (failure_count >= 0),
    abandoned_count INTEGER NOT NULL CHECK (abandoned_count >= 0),
    median_success_seconds NUMERIC(10, 2) CHECK (median_success_seconds >= 0),
    mean_errors NUMERIC(10, 3) NOT NULL CHECK (mean_errors >= 0),
    assistance_rate NUMERIC(5, 4) NOT NULL CHECK (assistance_rate BETWEEN 0 AND 1),
    UNIQUE (iteration_id, task_id),
    CHECK (
        success_count + partial_count + failure_count + abandoned_count
        = participant_count
    ),
    CHECK (success_count <= participant_count)
);

CREATE TABLE design_decisions (
    decision_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    study_id BIGINT NOT NULL REFERENCES studies(study_id) ON DELETE CASCADE,
    problem_id BIGINT REFERENCES usability_problems(problem_id),
    decision_text TEXT NOT NULL,
    rationale TEXT NOT NULL,
    owner_role TEXT NOT NULL,
    due_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- These indexes support the most common analysis access paths.
CREATE INDEX sessions_study_task_outcome_idx
    ON sessions (study_id, task_id, outcome);

CREATE INDEX sessions_participant_started_idx
    ON sessions (participant_id, started_at);

CREATE INDEX observations_session_elapsed_idx
    ON observations (session_id, elapsed_seconds);

CREATE INDEX problem_severity_status_idx
    ON usability_problems (study_id, severity, status);

CREATE INDEX problem_evidence_problem_idx
    ON problem_evidence (problem_id, evidence_type);

CREATE INDEX iteration_metrics_task_idx
    ON iteration_task_metrics (task_id, iteration_id);

-- Prevent a session from linking a participant or task from another study.
CREATE FUNCTION validate_session_study_membership()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    participant_study BIGINT;
    task_study BIGINT;
BEGIN
    SELECT study_id INTO participant_study
    FROM participants
    WHERE participant_id = NEW.participant_id;

    SELECT study_id INTO task_study
    FROM study_tasks
    WHERE task_id = NEW.task_id;

    IF participant_study IS DISTINCT FROM NEW.study_id THEN
        RAISE EXCEPTION
            'Participant % does not belong to study %',
            NEW.participant_id, NEW.study_id;
    END IF;

    IF task_study IS DISTINCT FROM NEW.study_id THEN
        RAISE EXCEPTION
            'Task % does not belong to study %',
            NEW.task_id, NEW.study_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER sessions_study_membership_guard
BEFORE INSERT OR UPDATE OF study_id, participant_id, task_id
ON sessions
FOR EACH ROW
EXECUTE FUNCTION validate_session_study_membership();

-- Enforce a legal problem lifecycle. A fixed problem is not verified until
-- subsequent evidence supports the changed design.
CREATE FUNCTION enforce_finding_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = OLD.status THEN
        RETURN NEW;
    END IF;

    IF NOT (
        (OLD.status = 'open'
            AND NEW.status IN ('in_progress', 'accepted_risk'))
        OR
        (OLD.status = 'in_progress'
            AND NEW.status IN ('open', 'fixed'))
        OR
        (OLD.status = 'fixed'
            AND NEW.status IN ('verified', 'in_progress'))
        OR
        (OLD.status = 'verified'
            AND NEW.status = 'in_progress')
        OR
        (OLD.status = 'accepted_risk'
            AND NEW.status = 'open')
    ) THEN
        RAISE EXCEPTION 'Invalid finding transition: % -> %',
            OLD.status, NEW.status;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER usability_problem_transition_guard
BEFORE UPDATE OF status ON usability_problems
FOR EACH ROW
EXECUTE FUNCTION enforce_finding_transition();

-- A problem-task relationship must stay within one study.
CREATE FUNCTION validate_problem_task_study()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    problem_study BIGINT;
    task_study BIGINT;
BEGIN
    SELECT study_id INTO problem_study
    FROM usability_problems
    WHERE problem_id = NEW.problem_id;

    SELECT study_id INTO task_study
    FROM study_tasks
    WHERE task_id = NEW.task_id;

    IF problem_study IS DISTINCT FROM task_study THEN
        RAISE EXCEPTION 'Problem and task must belong to the same study';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER problem_task_study_guard
BEFORE INSERT OR UPDATE ON problem_tasks
FOR EACH ROW
EXECUTE FUNCTION validate_problem_task_study();

-- Strict success and partial-or-success are distinct measures.
CREATE VIEW task_performance AS
SELECT
    st.study_id,
    st.task_id,
    st.task_code,
    st.scenario,
    COUNT(s.session_id) AS participant_count,
    COUNT(*) FILTER (WHERE s.outcome = 'success') AS success_count,
    COUNT(*) FILTER (WHERE s.outcome = 'partial') AS partial_count,
    COUNT(*) FILTER (WHERE s.outcome = 'failure') AS failure_count,
    COUNT(*) FILTER (WHERE s.outcome = 'abandoned') AS abandoned_count,
    ROUND(
        COUNT(*) FILTER (WHERE s.outcome = 'success')::NUMERIC
        / NULLIF(COUNT(s.session_id), 0),
        4
    ) AS success_rate,
    ROUND(
        COUNT(*) FILTER (WHERE s.outcome IN ('success', 'partial'))::NUMERIC
        / NULLIF(COUNT(s.session_id), 0),
        4
    ) AS partial_or_success_rate,
    ROUND(AVG(s.duration_seconds) FILTER (
        WHERE s.outcome = 'success'
    ), 2) AS mean_success_seconds,
    ROUND(AVG(s.error_count)::NUMERIC, 3) AS mean_errors,
    ROUND(AVG(s.assistance_requests)::NUMERIC, 3) AS mean_assistance_requests,
    ROUND(AVG(s.confidence_rating)::NUMERIC, 2) AS mean_confidence
FROM study_tasks st
LEFT JOIN sessions s ON s.task_id = st.task_id
GROUP BY st.study_id, st.task_id, st.task_code, st.scenario;

-- The frequency measure counts distinct participants with linked evidence.
-- The score is a transparent triage aid, not a statistically validated scale.
CREATE VIEW prioritized_problems AS
SELECT
    p.problem_id,
    p.study_id,
    p.problem_code,
    p.title,
    p.severity,
    p.impact,
    p.status,
    COUNT(DISTINCT s.participant_id) AS observed_participant_frequency,
    CASE p.severity
        WHEN 'cosmetic' THEN 1
        WHEN 'minor' THEN 2
        WHEN 'major' THEN 3
        WHEN 'critical' THEN 4
    END
    * LN(
        1 + GREATEST(
            COUNT(DISTINCT s.participant_id),
            COUNT(DISTINCT pe.evidence_id)
        )
    )
    * p.impact AS priority_score,
    p.proposed_change
FROM usability_problems p
LEFT JOIN problem_evidence pe ON pe.problem_id = p.problem_id
LEFT JOIN observations o ON o.observation_id = pe.observation_id
LEFT JOIN sessions s ON s.session_id = o.session_id
GROUP BY
    p.problem_id,
    p.study_id,
    p.problem_code,
    p.title,
    p.severity,
    p.impact,
    p.status,
    p.proposed_change;

INSERT INTO studies (
    study_code,
    title,
    objective,
    environment,
    target_participants,
    recruitment_criteria,
    moderator_script,
    analysis_plan
) VALUES (
    'PROC-UX-2026-03',
    'Procurement Portal Usability Evaluation',
    'Assess supplier discovery, quotation comparison, and purchase-request submission.',
    'Moderated sessions in a staging procurement portal.',
    6,
    '[
        "Recruit procurement or purchasing staff",
        "Include frequent and occasional system users",
        "Record consent before session participation"
    ]'::jsonb,
    '[
        "Explain that the interface is being evaluated, not the participant",
        "Ask the participant to think aloud",
        "Avoid teaching the interface during task execution",
        "Ask neutral follow-up questions after each task"
    ]'::jsonb,
    'Compare task success, time, errors, assistance, confidence, and qualitative evidence.'
);

INSERT INTO research_questions (study_id, question_code, question_text, supported_decision)
SELECT study_id, 'RQ-SUPPLIER',
       'Can users distinguish active supplier approval from pending approval?',
       'Clarify supplier approval labels and filters.'
FROM studies WHERE study_code = 'PROC-UX-2026-03';

INSERT INTO research_questions (study_id, question_code, question_text, supported_decision)
SELECT study_id, 'RQ-QUOTE',
       'Can users identify the lowest-priced compliant quotation?',
       'Show compliance beside total cost.'
FROM studies WHERE study_code = 'PROC-UX-2026-03';

INSERT INTO research_questions (study_id, question_code, question_text, supported_decision)
SELECT study_id, 'RQ-SUBMIT',
       'Can users submit a request and verify its final state?',
       'Improve submission feedback.'
FROM studies WHERE study_code = 'PROC-UX-2026-03';

INSERT INTO study_tasks (
    study_id, task_code, scenario, expected_outcome,
    success_criteria, time_limit_seconds, task_order
)
SELECT study_id, 'T-SUPPLIER',
       'Find an electrical supplier whose approval is active.',
       'Identify a suitable approved supplier.',
       '["Supplier selected", "Approval verified", "Category verified"]'::jsonb,
       240, 1
FROM studies WHERE study_code = 'PROC-UX-2026-03';

INSERT INTO study_tasks (
    study_id, task_code, scenario, expected_outcome,
    success_criteria, time_limit_seconds, task_order
)
SELECT study_id, 'T-QUOTE',
       'Compare quotations and select the lowest-priced compliant offer.',
       'Select an offer that satisfies the specification.',
       '["Offers compared", "Compliance verified", "Offer selected"]'::jsonb,
       300, 2
FROM studies WHERE study_code = 'PROC-UX-2026-03';

INSERT INTO study_tasks (
    study_id, task_code, scenario, expected_outcome,
    success_criteria, time_limit_seconds, task_order
)
SELECT study_id, 'T-SUBMIT',
       'Submit a purchase request and verify its reference and submitted state.',
       'Submit a valid request.',
       '["Quantity correct", "Request submitted", "Reference verified"]'::jsonb,
       360, 3
FROM studies WHERE study_code = 'PROC-UX-2026-03';

INSERT INTO participants (
    study_id, pseudonym, role_name, experience_level, consent_recorded
)
SELECT study_id, sample.pseudonym, sample.role_name,
       sample.experience_level, TRUE
FROM studies
CROSS JOIN (
    VALUES
        ('P401', 'Procurement officer', 'frequent'),
        ('P402', 'Purchase analyst', 'occasional'),
        ('P403', 'Vendor manager', 'frequent'),
        ('P404', 'Department coordinator', 'occasional')
) AS sample(pseudonym, role_name, experience_level)
WHERE studies.study_code = 'PROC-UX-2026-03';

-- Representative sessions deliberately include success, partial completion,
-- failure, assistance, and different confidence levels.
INSERT INTO sessions (
    study_id, participant_id, task_id, mode, outcome,
    started_at, ended_at, duration_seconds, error_count,
    assistance_requests, confidence_rating, moderator_notes
)
SELECT
    st.study_id,
    p.participant_id,
    st.task_id,
    'moderated'::session_mode,
    sample.outcome::task_outcome,
    TIMESTAMPTZ '2026-10-01 09:00:00+05:30'
        + sample.session_offset * INTERVAL '1 hour',
    TIMESTAMPTZ '2026-10-01 09:00:00+05:30'
        + sample.session_offset * INTERVAL '1 hour'
        + sample.duration_seconds * INTERVAL '1 second',
    sample.duration_seconds,
    sample.error_count,
    sample.assistance_requests,
    sample.confidence_rating,
    sample.notes
FROM (
    VALUES
        ('P401', 'T-SUPPLIER', 'success', 72, 0, 0, 5, 0,
         'Applied approval filter and verified status.'),
        ('P402', 'T-SUPPLIER', 'failure', 240, 3, 1, 2, 1,
         'Selected a supplier with pending approval.'),
        ('P403', 'T-SUPPLIER', 'success', 88, 1, 0, 4, 2,
         'Searched by category and checked approval.'),
        ('P404', 'T-SUPPLIER', 'partial', 180, 2, 1, 3, 3,
         'Changed filters repeatedly before selection.'),
        ('P401', 'T-QUOTE', 'partial', 160, 2, 0, 3, 4,
         'Selected a low-priced offer before verifying compliance.'),
        ('P402', 'T-QUOTE', 'failure', 300, 4, 2, 2, 5,
         'Could not distinguish compliant offers.'),
        ('P403', 'T-QUOTE', 'success', 125, 1, 0, 5, 6,
         'Compared specification and total price.'),
        ('P404', 'T-QUOTE', 'success', 142, 1, 0, 4, 7,
         'Checked compliance before selecting the quotation.'),
        ('P401', 'T-SUBMIT', 'success', 165, 1, 0, 5, 8,
         'Verified the submission confirmation.'),
        ('P402', 'T-SUBMIT', 'failure', 360, 4, 2, 2, 9,
         'Repeated submission after ambiguous feedback.'),
        ('P403', 'T-SUBMIT', 'success', 190, 1, 0, 4, 10,
         'Opened request history to confirm status.'),
        ('P404', 'T-SUBMIT', 'success', 175, 1, 0, 4, 11,
         'Corrected quantity and submitted request.')
) AS sample(
    pseudonym, task_code, outcome, duration_seconds, error_count,
    assistance_requests, confidence_rating, session_offset, notes
)
JOIN studies st ON st.study_code = 'PROC-UX-2026-03'
JOIN participants p
    ON p.study_id = st.study_id
   AND p.pseudonym = sample.pseudonym
JOIN study_tasks t
    ON t.study_id = st.study_id
   AND t.task_code = sample.task_code
JOIN study_tasks st_task ON st_task.task_id = t.task_id
CROSS JOIN LATERAL (
    SELECT st_task.task_id
) AS resolved_task(task_id)
WHERE st_task.study_id = st.study_id;

INSERT INTO observations (
    session_id, elapsed_seconds, event_type, target_element,
    description, evidence_type
)
SELECT s.session_id, sample.elapsed_seconds, sample.event_type,
       sample.target_element, sample.description, 'observed'::evidence_kind
FROM (
    VALUES
        ('P402', 'T-SUPPLIER', 30, 'wrong_selection', 'supplier-row',
         'Selected a supplier with pending approval.'),
        ('P404', 'T-SUPPLIER', 40, 'filter_confusion', 'approval-filter',
         'Changed the approval filter repeatedly.'),
        ('P401', 'T-QUOTE', 25, 'wrong_selection', 'quotation-row',
         'Selected a low-priced offer before checking compliance.'),
        ('P402', 'T-QUOTE', 75, 'comparison_confusion', 'compliance-column',
         'Could not determine which offers met specifications.'),
        ('P402', 'T-SUBMIT', 180, 'repeated_submission', 'submit-button',
         'Repeated submission after ambiguous feedback.')
) AS sample(
    pseudonym, task_code, elapsed_seconds, event_type,
    target_element, description
)
JOIN participants p ON p.pseudonym = sample.pseudonym
JOIN study_tasks t ON t.task_code = sample.task_code
JOIN sessions s
    ON s.participant_id = p.participant_id
   AND s.task_id = t.task_id;

INSERT INTO usability_problems (
    study_id, problem_code, title, description, severity,
    impact, proposed_change
)
SELECT study_id, 'UX-501',
       'Supplier approval labels are ambiguous',
       'Users can confuse pending approval with active approval.',
       'critical', 0.95,
       'Use explicit status labels, approval dates, and an approved-only filter.'
FROM studies WHERE study_code = 'PROC-UX-2026-03';

INSERT INTO usability_problems (
    study_id, problem_code, title, description, severity,
    impact, proposed_change
)
SELECT study_id, 'UX-502',
       'Quotation compliance is separated from price',
       'Users can select a low-priced quotation without checking compliance.',
       'critical', 0.90,
       'Display compliance beside total price and highlight the lowest compliant offer.'
FROM studies WHERE study_code = 'PROC-UX-2026-03';

INSERT INTO usability_problems (
    study_id, problem_code, title, description, severity,
    impact, proposed_change
)
SELECT study_id, 'UX-503',
       'Request submission feedback is unclear',
       'Users may repeat an action because its resulting state is uncertain.',
       'major', 0.80,
       'Show a persistent confirmation, request reference, and request-history link.'
FROM studies WHERE study_code = 'PROC-UX-2026-03';

INSERT INTO problem_tasks (problem_id, task_id)
SELECT p.problem_id, t.task_id
FROM usability_problems p
JOIN study_tasks t ON t.study_id = p.study_id
WHERE (p.problem_code = 'UX-501' AND t.task_code = 'T-SUPPLIER')
   OR (p.problem_code = 'UX-502' AND t.task_code = 'T-QUOTE')
   OR (p.problem_code = 'UX-503' AND t.task_code = 'T-SUBMIT');

INSERT INTO problem_evidence (
    problem_id, observation_id, evidence_type, evidence_statement
)
SELECT p.problem_id, o.observation_id, 'observed'::evidence_kind, o.description
FROM usability_problems p
JOIN study_tasks t ON t.study_id = p.study_id
JOIN sessions s ON s.task_id = t.task_id
JOIN observations o ON o.session_id = s.session_id
WHERE (p.problem_code = 'UX-501' AND t.task_code = 'T-SUPPLIER'
       AND o.event_type IN ('wrong_selection', 'filter_confusion'))
   OR (p.problem_code = 'UX-502' AND t.task_code = 'T-QUOTE'
       AND o.event_type IN ('wrong_selection', 'comparison_confusion'))
   OR (p.problem_code = 'UX-503' AND t.task_code = 'T-SUBMIT'
       AND o.event_type = 'repeated_submission');

INSERT INTO design_iterations (
    study_id, version_label, description, prototype_reference
)
SELECT study_id, 'v1',
       'Baseline procurement interface before usability-driven changes.',
       'staging/procurement/v1'
FROM studies WHERE study_code = 'PROC-UX-2026-03';

INSERT INTO design_iterations (
    study_id, version_label, description, prototype_reference
)
SELECT study_id, 'v2',
       'Candidate interface with clearer approval, compliance, and submission feedback.',
       'staging/procurement/v2'
FROM studies WHERE study_code = 'PROC-UX-2026-03';

-- Aggregate task outcomes for the baseline iteration.
INSERT INTO iteration_task_metrics (
    iteration_id, task_id, participant_count, success_count,
    partial_count, failure_count, abandoned_count,
    median_success_seconds, mean_errors, assistance_rate
)
SELECT
    i.iteration_id,
    t.task_id,
    COUNT(s.session_id)::INTEGER,
    COUNT(*) FILTER (WHERE s.outcome = 'success')::INTEGER,
    COUNT(*) FILTER (WHERE s.outcome = 'partial')::INTEGER,
    COUNT(*) FILTER (WHERE s.outcome = 'failure')::INTEGER,
    COUNT(*) FILTER (WHERE s.outcome = 'abandoned')::INTEGER,
    percentile_cont(0.5) WITHIN GROUP (
        ORDER BY s.duration_seconds
    ) FILTER (WHERE s.outcome = 'success'),
    COALESCE(AVG(s.error_count), 0),
    COALESCE(AVG((s.assistance_requests > 0)::INTEGER), 0)
FROM design_iterations i
JOIN study_tasks t ON t.study_id = i.study_id
LEFT JOIN sessions s ON s.task_id = t.task_id
WHERE i.version_label = 'v1'
GROUP BY i.iteration_id, t.task_id;

-- A separate candidate-version dataset allows iteration comparison even when
-- its participant sessions have not yet been inserted. These are illustrative
-- evaluation measurements, not claimed improvements from the baseline sample.
INSERT INTO iteration_task_metrics (
    iteration_id, task_id, participant_count, success_count,
    partial_count, failure_count, abandoned_count,
    median_success_seconds, mean_errors, assistance_rate
)
SELECT
    i.iteration_id,
    t.task_id,
    6,
    sample.success_count,
    sample.partial_count,
    sample.failure_count,
    sample.abandoned_count,
    sample.median_success_seconds,
    sample.mean_errors,
    sample.assistance_rate
FROM design_iterations i
JOIN study_tasks t ON t.study_id = i.study_id
JOIN (
    VALUES
        ('T-SUPPLIER', 5, 1, 0, 0, 62.0, 0.8, 0.10),
        ('T-QUOTE', 5, 1, 0, 0, 110.0, 0.7, 0.10),
        ('T-SUBMIT', 5, 1, 0, 0, 145.0, 0.5, 0.05)
) AS sample(
    task_code, success_count, partial_count, failure_count,
    abandoned_count, median_success_seconds, mean_errors, assistance_rate
) ON sample.task_code = t.task_code
WHERE i.version_label = 'v2';

-- Task-level analysis with explicit denominators.
SELECT
    task_code,
    participant_count,
    success_count,
    partial_count,
    failure_count,
    abandoned_count,
    success_rate,
    partial_or_success_rate,
    mean_success_seconds,
    mean_errors,
    mean_assistance_requests,
    mean_confidence
FROM task_performance
WHERE study_id = (
    SELECT study_id FROM studies
    WHERE study_code = 'PROC-UX-2026-03'
)
ORDER BY task_id;

-- Evidence-based problem prioritization.
SELECT
    problem_code,
    title,
    severity,
    status,
    observed_participant_frequency,
    ROUND(priority_score::NUMERIC, 3) AS priority_score,
    proposed_change
FROM prioritized_problems
WHERE study_id = (
    SELECT study_id FROM studies
    WHERE study_code = 'PROC-UX-2026-03'
)
ORDER BY priority_score DESC, problem_code;

-- Compare versions. Rates are derived from each version's own participant count.
SELECT
    task.task_code,
    old_version.version_label AS baseline_version,
    new_version.version_label AS candidate_version,
    ROUND(
        old_metrics.success_count::NUMERIC
        / NULLIF(old_metrics.participant_count, 0), 4
    ) AS baseline_success_rate,
    ROUND(
        new_metrics.success_count::NUMERIC
        / NULLIF(new_metrics.participant_count, 0), 4
    ) AS candidate_success_rate,
    ROUND(
        (
            new_metrics.success_count::NUMERIC
            / NULLIF(new_metrics.participant_count, 0)
        )
        -
        (
            old_metrics.success_count::NUMERIC
            / NULLIF(old_metrics.participant_count, 0)
        ),
        4
    ) AS success_rate_change,
    old_metrics.median_success_seconds AS baseline_median_seconds,
    new_metrics.median_success_seconds AS candidate_median_seconds,
    new_metrics.median_success_seconds
        - old_metrics.median_success_seconds AS median_seconds_change,
    new_metrics.mean_errors - old_metrics.mean_errors AS mean_error_change
FROM iteration_task_metrics old_metrics
JOIN design_iterations old_version
    ON old_version.iteration_id = old_metrics.iteration_id
JOIN iteration_task_metrics new_metrics
    ON new_metrics.task_id = old_metrics.task_id
JOIN design_iterations new_version
    ON new_version.iteration_id = new_metrics.iteration_id
JOIN study_tasks task ON task.task_id = old_metrics.task_id
WHERE old_version.version_label = 'v1'
  AND new_version.version_label = 'v2'
  AND old_version.study_id = new_version.study_id
ORDER BY task.task_order;

-- Demonstrate finding lifecycle rules with a valid transition.
UPDATE usability_problems
SET status = 'in_progress'
WHERE problem_code = 'UX-501'
  AND study_id = (
      SELECT study_id FROM studies
      WHERE study_code = 'PROC-UX-2026-03'
  );

-- The following deliberately invalid transition is documented but not executed:
-- UPDATE usability_problems SET status = 'verified' WHERE problem_code = 'UX-501';
-- The trigger rejects open -> verified because a fix and its verification must
-- be represented as separate states.

COMMIT;
