-- UX Research and Product Design Management
-- PostgreSQL 15+
--
-- The schema stores pseudonymous research evidence, synthesis themes,
-- design decisions, wireframe structure, design-system components,
-- prototype testing results, and design critique.
--
-- The final readiness function evaluates these records together.
-- This script recreates its isolated schema when executed.

DROP SCHEMA IF EXISTS ux_lab CASCADE;
CREATE SCHEMA ux_lab;

SET search_path TO ux_lab, public;

-- ---------------------------------------------------------------------
-- PROJECTS AND RESEARCH
-- ---------------------------------------------------------------------

CREATE TABLE projects (
    project_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_name     VARCHAR(160) NOT NULL UNIQUE,
    product_area     VARCHAR(120) NOT NULL,
    owner_reference  VARCHAR(100) NOT NULL,
    stage            VARCHAR(20) NOT NULL DEFAULT 'discovery'
                     CHECK (stage IN (
                         'discovery', 'synthesis', 'design',
                         'prototype', 'validated'
                     )),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE research_studies (
    study_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id     BIGINT NOT NULL REFERENCES projects(project_id)
                   ON DELETE CASCADE,
    study_name     VARCHAR(180) NOT NULL,
    method         VARCHAR(30) NOT NULL
                   CHECK (method IN (
                       'interview', 'survey', 'contextual_inquiry',
                       'diary_study', 'usability_test'
                   )),
    research_goal  TEXT NOT NULL,
    status         VARCHAR(20) NOT NULL DEFAULT 'planned'
                   CHECK (status IN ('planned', 'active', 'completed', 'archived')),
    started_on     DATE,
    completed_on   DATE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (study_id, project_id),
    CHECK (
        completed_on IS NULL
        OR started_on IS NULL
        OR completed_on >= started_on
    )
);

-- Participant names, contact information, and direct identifiers are
-- intentionally excluded. Pseudonymous references support traceability.
CREATE TABLE participants (
    participant_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    study_id             BIGINT NOT NULL,
    project_id           BIGINT NOT NULL,
    participant_reference VARCHAR(40) NOT NULL,
    user_segment         VARCHAR(100) NOT NULL,
    consent_obtained     BOOLEAN NOT NULL DEFAULT FALSE,
    participation_status VARCHAR(20) NOT NULL DEFAULT 'active'
                         CHECK (participation_status IN (
                             'active', 'withdrawn', 'completed'
                         )),
    UNIQUE (study_id, participant_reference),
    UNIQUE (participant_id, project_id),
    FOREIGN KEY (study_id, project_id)
        REFERENCES research_studies(study_id, project_id)
        ON DELETE CASCADE,
    CHECK (consent_obtained = TRUE)
);

CREATE TABLE research_sessions (
    session_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id      BIGINT NOT NULL,
    study_id        BIGINT NOT NULL,
    participant_id  BIGINT NOT NULL,
    session_date    TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes BETWEEN 1 AND 480),
    session_notes   TEXT,
    UNIQUE (session_id, project_id),
    FOREIGN KEY (study_id, project_id)
        REFERENCES research_studies(study_id, project_id)
        ON DELETE CASCADE,
    FOREIGN KEY (participant_id, project_id)
        REFERENCES participants(participant_id, project_id)
        ON DELETE CASCADE
);

CREATE TABLE research_observations (
    observation_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id      BIGINT NOT NULL,
    session_id      BIGINT NOT NULL,
    observation_text TEXT NOT NULL,
    evidence_excerpt TEXT,
    severity        SMALLINT NOT NULL CHECK (severity BETWEEN 1 AND 5),
    confidence      NUMERIC(4,3) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    observation_type VARCHAR(30) NOT NULL
                    CHECK (observation_type IN (
                        'pain_point', 'user_need', 'behavior',
                        'preference', 'positive_feedback'
                    )),
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (observation_id, project_id),
    FOREIGN KEY (session_id, project_id)
        REFERENCES research_sessions(session_id, project_id)
        ON DELETE CASCADE,
    CHECK (length(trim(observation_text)) > 0)
);

CREATE TABLE research_tags (
    tag_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id   BIGINT NOT NULL REFERENCES projects(project_id)
                 ON DELETE CASCADE,
    tag_name     VARCHAR(80) NOT NULL,
    UNIQUE (project_id, tag_name),
    UNIQUE (tag_id, project_id)
);

CREATE TABLE observation_tags (
    observation_id BIGINT NOT NULL,
    tag_id         BIGINT NOT NULL,
    project_id     BIGINT NOT NULL,
    PRIMARY KEY (observation_id, tag_id),
    FOREIGN KEY (observation_id, project_id)
        REFERENCES research_observations(observation_id, project_id)
        ON DELETE CASCADE,
    FOREIGN KEY (tag_id, project_id)
        REFERENCES research_tags(tag_id, project_id)
        ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- RESEARCH SYNTHESIS AND DESIGN DECISIONS
-- ---------------------------------------------------------------------

CREATE TABLE research_themes (
    theme_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id     BIGINT NOT NULL REFERENCES projects(project_id)
                   ON DELETE CASCADE,
    theme_name     VARCHAR(150) NOT NULL,
    description    TEXT NOT NULL,
    effort_hours   NUMERIC(7,2) NOT NULL CHECK (effort_hours > 0),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (project_id, theme_name),
    UNIQUE (theme_id, project_id)
);

-- A theme can reference multiple observations, and one observation can
-- support more than one theme. The rationale preserves the coding context.
CREATE TABLE theme_evidence (
    theme_id       BIGINT NOT NULL,
    observation_id BIGINT NOT NULL,
    project_id     BIGINT NOT NULL,
    rationale      TEXT NOT NULL,
    PRIMARY KEY (theme_id, observation_id),
    FOREIGN KEY (theme_id, project_id)
        REFERENCES research_themes(theme_id, project_id)
        ON DELETE CASCADE,
    FOREIGN KEY (observation_id, project_id)
        REFERENCES research_observations(observation_id, project_id)
        ON DELETE CASCADE
);

CREATE TABLE design_decisions (
    decision_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id     BIGINT NOT NULL REFERENCES projects(project_id)
                   ON DELETE CASCADE,
    theme_id       BIGINT,
    decision_title VARCHAR(180) NOT NULL,
    hypothesis     TEXT NOT NULL,
    rationale      TEXT NOT NULL,
    decision_status VARCHAR(20) NOT NULL DEFAULT 'proposed'
                    CHECK (decision_status IN (
                        'proposed', 'accepted', 'rejected',
                        'under_test', 'superseded'
                    )),
    owner_reference VARCHAR(100) NOT NULL,
    decided_at     TIMESTAMPTZ,
    FOREIGN KEY (theme_id, project_id)
        REFERENCES research_themes(theme_id, project_id)
        ON DELETE SET NULL (theme_id)
);

-- ---------------------------------------------------------------------
-- DESIGN SYSTEM AND WIREFRAMES
-- ---------------------------------------------------------------------

CREATE TABLE design_tokens (
    token_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id     BIGINT NOT NULL REFERENCES projects(project_id)
                   ON DELETE CASCADE,
    token_name     VARCHAR(120) NOT NULL,
    token_value    VARCHAR(160) NOT NULL,
    token_type     VARCHAR(30) NOT NULL
                   CHECK (token_type IN (
                       'color', 'spacing', 'typography',
                       'radius', 'shadow', 'duration'
                   )),
    description    TEXT NOT NULL DEFAULT '',
    UNIQUE (project_id, token_name),
    UNIQUE (token_id, project_id)
);

CREATE TABLE design_components (
    component_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id         BIGINT NOT NULL REFERENCES projects(project_id)
                       ON DELETE CASCADE,
    component_name     VARCHAR(120) NOT NULL,
    component_category VARCHAR(60) NOT NULL,
    specification      JSONB NOT NULL DEFAULT '{}'::jsonb,
    interactive        BOOLEAN NOT NULL DEFAULT FALSE,
    keyboard_accessible BOOLEAN NOT NULL DEFAULT TRUE,
    accessible_description TEXT NOT NULL,
    contrast_ratio     NUMERIC(5,2),
    version_number     INTEGER NOT NULL DEFAULT 1 CHECK (version_number > 0),
    UNIQUE (project_id, component_name),
    UNIQUE (component_id, project_id),
    CHECK (
        contrast_ratio IS NULL
        OR contrast_ratio BETWEEN 1 AND 21
    ),
    CHECK (length(trim(accessible_description)) > 0)
);

CREATE TABLE wireframe_screens (
    screen_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id      BIGINT NOT NULL REFERENCES projects(project_id)
                    ON DELETE CASCADE,
    screen_name     VARCHAR(140) NOT NULL,
    accessible_name VARCHAR(180) NOT NULL,
    layout_structure JSONB NOT NULL DEFAULT '{}'::jsonb,
    keyboard_order  TEXT[] NOT NULL DEFAULT '{}',
    screen_status   VARCHAR(20) NOT NULL DEFAULT 'draft'
                    CHECK (screen_status IN (
                        'draft', 'review', 'approved', 'retired'
                    )),
    UNIQUE (project_id, screen_name),
    UNIQUE (screen_id, project_id),
    CHECK (length(trim(accessible_name)) > 0)
);

CREATE TABLE screen_components (
    project_id    BIGINT NOT NULL,
    screen_id     BIGINT NOT NULL,
    component_id  BIGINT NOT NULL,
    display_order INTEGER NOT NULL CHECK (display_order >= 1),
    PRIMARY KEY (screen_id, component_id),
    UNIQUE (screen_id, display_order),
    FOREIGN KEY (screen_id, project_id)
        REFERENCES wireframe_screens(screen_id, project_id)
        ON DELETE CASCADE,
    FOREIGN KEY (component_id, project_id)
        REFERENCES design_components(component_id, project_id)
        ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- PROTOTYPES, USABILITY TESTS, AND CRITIQUE
-- ---------------------------------------------------------------------

CREATE TABLE prototypes (
    prototype_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id    BIGINT NOT NULL REFERENCES projects(project_id)
                  ON DELETE CASCADE,
    version_label VARCHAR(40) NOT NULL,
    prototype_status VARCHAR(20) NOT NULL DEFAULT 'draft'
                     CHECK (prototype_status IN (
                         'draft', 'internal_review', 'testing',
                         'approved', 'retired'
                     )),
    published_at  TIMESTAMPTZ,
    UNIQUE (project_id, version_label),
    UNIQUE (prototype_id, project_id)
);

CREATE TABLE prototype_screens (
    prototype_id BIGINT NOT NULL,
    screen_id    BIGINT NOT NULL,
    project_id   BIGINT NOT NULL,
    PRIMARY KEY (prototype_id, screen_id),
    FOREIGN KEY (prototype_id, project_id)
        REFERENCES prototypes(prototype_id, project_id)
        ON DELETE CASCADE,
    FOREIGN KEY (screen_id, project_id)
        REFERENCES wireframe_screens(screen_id, project_id)
        ON DELETE RESTRICT
);

CREATE TABLE usability_test_runs (
    test_run_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id      BIGINT NOT NULL,
    prototype_id    BIGINT NOT NULL,
    participant_id  BIGINT NOT NULL,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes BETWEEN 1 AND 480),
    moderator_notes TEXT,
    UNIQUE (test_run_id, project_id),
    FOREIGN KEY (prototype_id, project_id)
        REFERENCES prototypes(prototype_id, project_id)
        ON DELETE CASCADE,
    FOREIGN KEY (participant_id, project_id)
        REFERENCES participants(participant_id, project_id)
        ON DELETE RESTRICT
);

CREATE TABLE usability_task_results (
    task_result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id     BIGINT NOT NULL,
    test_run_id    BIGINT NOT NULL,
    task_name      VARCHAR(180) NOT NULL,
    succeeded      BOOLEAN NOT NULL,
    duration_seconds NUMERIC(8,2) NOT NULL CHECK (duration_seconds > 0),
    critical_errors INTEGER NOT NULL DEFAULT 0 CHECK (critical_errors >= 0),
    observed_issue TEXT,
    FOREIGN KEY (test_run_id, project_id)
        REFERENCES usability_test_runs(test_run_id, project_id)
        ON DELETE CASCADE,
    CHECK (length(trim(task_name)) > 0)
);

CREATE TABLE critique_issues (
    critique_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id    BIGINT NOT NULL,
    screen_id     BIGINT NOT NULL,
    heuristic     VARCHAR(120) NOT NULL,
    severity      VARCHAR(15) NOT NULL
                  CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description   TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    resolved      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at   TIMESTAMPTZ,
    FOREIGN KEY (screen_id, project_id)
        REFERENCES wireframe_screens(screen_id, project_id)
        ON DELETE CASCADE,
    CHECK (length(trim(description)) > 0),
    CHECK (length(trim(recommendation)) > 0),
    CHECK (
        (resolved = FALSE AND resolved_at IS NULL)
        OR
        (resolved = TRUE AND resolved_at IS NOT NULL)
    )
);

-- ---------------------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------------------

-- Supports project-level research reporting and evidence retrieval.
CREATE INDEX idx_observations_project_type
    ON research_observations(project_id, observation_type);

CREATE INDEX idx_sessions_project_date
    ON research_sessions(project_id, session_date DESC);

-- Supports reverse lookup from observations to synthesis themes.
CREATE INDEX idx_theme_evidence_observation
    ON theme_evidence(project_id, observation_id);

-- Supports usability reporting by project and prototype test.
CREATE INDEX idx_test_runs_project
    ON usability_test_runs(project_id, started_at DESC);

CREATE INDEX idx_task_results_run
    ON usability_task_results(test_run_id);

-- Open critical issues are frequently queried during readiness checks.
CREATE INDEX idx_critique_open_critical
    ON critique_issues(project_id, screen_id)
    WHERE resolved = FALSE AND severity = 'critical';

-- ---------------------------------------------------------------------
-- AGGREGATION VIEW
-- ---------------------------------------------------------------------

CREATE VIEW v_theme_strength AS
SELECT
    t.project_id,
    t.theme_id,
    t.theme_name,
    t.effort_hours,
    COUNT(o.observation_id) AS evidence_count,
    ROUND(AVG(o.severity)::NUMERIC, 2) AS average_severity,
    ROUND(AVG(o.confidence), 3) AS average_confidence,
    ROUND(
        (
            COUNT(o.observation_id)
            * AVG(o.severity)
            * AVG(o.confidence)
            / NULLIF(t.effort_hours, 0)
        )::NUMERIC,
        3
    ) AS priority_score
FROM research_themes t
LEFT JOIN theme_evidence te
    ON te.theme_id = t.theme_id
   AND te.project_id = t.project_id
LEFT JOIN research_observations o
    ON o.observation_id = te.observation_id
   AND o.project_id = te.project_id
GROUP BY
    t.project_id,
    t.theme_id,
    t.theme_name,
    t.effort_hours;

-- ---------------------------------------------------------------------
-- READINESS EVALUATION
-- ---------------------------------------------------------------------

CREATE FUNCTION fn_design_readiness(p_project_id BIGINT)
RETURNS TABLE (
    eligible BOOLEAN,
    blockers TEXT[],
    evidence_count BIGINT,
    theme_count BIGINT,
    screen_count BIGINT,
    test_run_count BIGINT,
    task_success_rate NUMERIC,
    critical_error_count BIGINT,
    unresolved_critical_count BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_evidence_count BIGINT := 0;
    v_theme_count BIGINT := 0;
    v_screen_count BIGINT := 0;
    v_test_run_count BIGINT := 0;
    v_task_count BIGINT := 0;
    v_success_count BIGINT := 0;
    v_success_rate NUMERIC := 0;
    v_critical_error_count BIGINT := 0;
    v_unresolved_critical_count BIGINT := 0;
    v_inaccessible_component_count BIGINT := 0;
    v_empty_screen_count BIGINT := 0;
    v_blockers TEXT[] := ARRAY[]::TEXT[];
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM projects p WHERE p.project_id = p_project_id
    ) THEN
        RAISE EXCEPTION 'Unknown project ID: %', p_project_id;
    END IF;

    SELECT COUNT(*)
    INTO v_evidence_count
    FROM research_observations o
    WHERE o.project_id = p_project_id;

    SELECT COUNT(*)
    INTO v_theme_count
    FROM research_themes t
    WHERE t.project_id = p_project_id;

    SELECT COUNT(*)
    INTO v_screen_count
    FROM wireframe_screens s
    WHERE s.project_id = p_project_id
      AND s.screen_status <> 'retired';

    SELECT COUNT(*)
    INTO v_test_run_count
    FROM usability_test_runs r
    WHERE r.project_id = p_project_id;

    SELECT
        COUNT(*),
        COUNT(*) FILTER (WHERE tr.succeeded = TRUE),
        COALESCE(SUM(tr.critical_errors), 0)
    INTO
        v_task_count,
        v_success_count,
        v_critical_error_count
    FROM usability_task_results tr
    WHERE tr.project_id = p_project_id;

    IF v_task_count > 0 THEN
        v_success_rate := ROUND(
            v_success_count::NUMERIC / v_task_count,
            3
        );
    END IF;

    SELECT COUNT(*)
    INTO v_unresolved_critical_count
    FROM critique_issues ci
    WHERE ci.project_id = p_project_id
      AND ci.severity = 'critical'
      AND ci.resolved = FALSE;

    SELECT COUNT(DISTINCT dc.component_id)
    INTO v_inaccessible_component_count
    FROM design_components dc
    JOIN screen_components sc
      ON sc.component_id = dc.component_id
     AND sc.project_id = dc.project_id
    WHERE dc.project_id = p_project_id
      AND (
          dc.keyboard_accessible = FALSE
          OR (dc.contrast_ratio IS NOT NULL AND dc.contrast_ratio < 4.5)
      );

    SELECT COUNT(*)
    INTO v_empty_screen_count
    FROM wireframe_screens s
    WHERE s.project_id = p_project_id
      AND s.screen_status <> 'retired'
      AND NOT EXISTS (
          SELECT 1
          FROM screen_components sc
          WHERE sc.screen_id = s.screen_id
            AND sc.project_id = s.project_id
      );

    IF v_evidence_count < 5 THEN
        v_blockers := array_append(
            v_blockers,
            'At least five research observations are required.'
        );
    END IF;

    IF v_theme_count < 2 THEN
        v_blockers := array_append(
            v_blockers,
            'At least two research themes are required.'
        );
    END IF;

    IF v_screen_count < 2 THEN
        v_blockers := array_append(
            v_blockers,
            'At least two non-retired wireframe screens are required.'
        );
    END IF;

    IF v_test_run_count < 3 THEN
        v_blockers := array_append(
            v_blockers,
            'At least three usability test runs are required.'
        );
    END IF;

    IF v_task_count < 5 THEN
        v_blockers := array_append(
            v_blockers,
            'At least five usability task results are required.'
        );
    END IF;

    IF v_success_rate < 0.800 THEN
        v_blockers := array_append(
            v_blockers,
            'Task success rate is below the 80 percent threshold.'
        );
    END IF;

    IF v_critical_error_count > 0 THEN
        v_blockers := array_append(
            v_blockers,
            'Prototype testing contains critical task errors.'
        );
    END IF;

    IF v_unresolved_critical_count > 0 THEN
        v_blockers := array_append(
            v_blockers,
            'Unresolved critical design critique issues exist.'
        );
    END IF;

    IF v_inaccessible_component_count > 0 THEN
        v_blockers := array_append(
            v_blockers,
            'Referenced components fail keyboard or contrast checks.'
        );
    END IF;

    IF v_empty_screen_count > 0 THEN
        v_blockers := array_append(
            v_blockers,
            'One or more wireframe screens have no registered components.'
        );
    END IF;

    RETURN QUERY
    SELECT
        cardinality(v_blockers) = 0,
        v_blockers,
        v_evidence_count,
        v_theme_count,
        v_screen_count,
        v_test_run_count,
        v_success_rate,
        v_critical_error_count,
        v_unresolved_critical_count;
END;
$$;

-- Validation of the final project stage is enforced by the database.
-- An application cannot set a project to validated while blockers remain.
CREATE FUNCTION trg_enforce_validated_stage()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_eligible BOOLEAN;
    v_blockers TEXT[];
BEGIN
    IF NEW.stage = 'validated'
       AND OLD.stage IS DISTINCT FROM NEW.stage THEN

        SELECT r.eligible, r.blockers
        INTO v_eligible, v_blockers
        FROM fn_design_readiness(NEW.project_id) r;

        IF v_eligible IS DISTINCT FROM TRUE THEN
            RAISE EXCEPTION
                'Project cannot enter validated stage. Blockers: %',
                array_to_string(v_blockers, '; ');
        END IF;
    END IF;

    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER projects_validated_stage_gate
BEFORE UPDATE OF stage ON projects
FOR EACH ROW
EXECUTE FUNCTION trg_enforce_validated_stage();

-- ---------------------------------------------------------------------
-- SAMPLE PROJECT AND RESEARCH RECORDS
-- ---------------------------------------------------------------------

BEGIN;

INSERT INTO projects (
    project_id, project_name, product_area, owner_reference, stage
) OVERRIDING SYSTEM VALUE
VALUES (
    1, 'City Transit Companion', 'Public Transport', 'DESIGN-OWNER-01', 'prototype'
);

INSERT INTO research_studies (
    study_id, project_id, study_name, method, research_goal, status,
    started_on, completed_on
) OVERRIDING SYSTEM VALUE
VALUES (
    1, 1, 'Journey Planning Discovery', 'interview',
    'Understand how passengers search, compare, and select transit journeys.',
    'completed', DATE '2026-09-01', DATE '2026-09-20'
);

INSERT INTO participants (
    participant_id, study_id, project_id, participant_reference,
    user_segment, consent_obtained, participation_status
) OVERRIDING SYSTEM VALUE
VALUES
    (1, 1, 1, 'P-001', 'Daily commuter', TRUE, 'completed'),
    (2, 1, 1, 'P-002', 'Occasional passenger', TRUE, 'completed'),
    (3, 1, 1, 'P-003', 'Daily commuter', TRUE, 'completed'),
    (4, 1, 1, 'P-004', 'Student passenger', TRUE, 'completed'),
    (5, 1, 1, 'P-005', 'Occasional passenger', TRUE, 'completed'),
    (6, 1, 1, 'P-006', 'Senior passenger', TRUE, 'completed'),
    (7, 1, 1, 'P-007', 'Daily commuter', TRUE, 'completed'),
    (8, 1, 1, 'P-008', 'Student passenger', TRUE, 'completed'),
    (9, 1, 1, 'P-009', 'Occasional passenger', TRUE, 'completed');

INSERT INTO research_sessions (
    session_id, project_id, study_id, participant_id, session_date,
    duration_minutes, session_notes
) OVERRIDING SYSTEM VALUE
VALUES
    (1, 1, 1, 1, TIMESTAMPTZ '2026-09-02 10:00:00+05:30', 45, 'Journey search interview.'),
    (2, 1, 1, 2, TIMESTAMPTZ '2026-09-05 11:00:00+05:30', 40, 'Route comparison observation.'),
    (3, 1, 1, 3, TIMESTAMPTZ '2026-09-08 14:00:00+05:30', 50, 'Fare information interview.');

INSERT INTO research_observations (
    observation_id, project_id, session_id, observation_text,
    evidence_excerpt, severity, confidence, observation_type
) OVERRIDING SYSTEM VALUE
VALUES
    (1, 1, 1, 'Transfer requirements are unclear.',
     'The participant could not determine whether a route required changing vehicles.',
     5, 0.950, 'pain_point'),
    (2, 1, 2, 'Transfer points are difficult to identify.',
     'The route presentation did not make interchange locations prominent.',
     4, 0.900, 'pain_point'),
    (3, 1, 2, 'Users compare journeys by total travel time.',
     'Total journey duration influenced route selection.',
     3, 0.850, 'behavior'),
    (4, 1, 3, 'The complete fare is difficult to locate.',
     'The participant opened multiple screens to compare journey cost.',
     5, 0.950, 'pain_point'),
    (5, 1, 3, 'Fare presentation is inconsistent.',
     'Similar route options displayed fare information in different positions.',
     4, 0.900, 'pain_point'),
    (6, 1, 3, 'Users need to compare fare categories.',
     'The participant asked whether the displayed fare was standard or discounted.',
     3, 0.850, 'user_need');

INSERT INTO research_tags (
    tag_id, project_id, tag_name
) OVERRIDING SYSTEM VALUE
VALUES
    (1, 1, 'transfers'),
    (2, 1, 'journey-time'),
    (3, 1, 'fares'),
    (4, 1, 'information-architecture');

INSERT INTO observation_tags (observation_id, tag_id, project_id)
VALUES
    (1, 1, 1),
    (2, 1, 1),
    (3, 2, 1),
    (4, 3, 1),
    (5, 3, 1),
    (6, 3, 1);

INSERT INTO research_themes (
    theme_id, project_id, theme_name, description, effort_hours
) OVERRIDING SYSTEM VALUE
VALUES
    (1, 1, 'Transfer uncertainty',
     'Passengers struggle to understand interchange requirements and journey structure.',
     8.00),
    (2, 1, 'Fare transparency',
     'Passengers need consistent and comparable fare information.',
     5.00);

INSERT INTO theme_evidence (
    theme_id, observation_id, project_id, rationale
)
VALUES
    (1, 1, 1, 'Direct evidence of unclear transfer requirements.'),
    (1, 2, 1, 'Supports the need for prominent interchange details.'),
    (1, 3, 1, 'Journey comparison behavior provides supporting context.'),
    (2, 4, 1, 'Direct evidence of difficulty locating complete fare information.'),
    (2, 5, 1, 'Supports consistent fare presentation.'),
    (2, 6, 1, 'Supports the need to distinguish fare categories.');

INSERT INTO design_decisions (
    decision_id, project_id, theme_id, decision_title,
    hypothesis, rationale, decision_status, owner_reference, decided_at
) OVERRIDING SYSTEM VALUE
VALUES
    (1, 1, 1, 'Show interchange information on route cards',
     'Prominent transfer details will help passengers compare route complexity.',
     'Three linked observations support transfer uncertainty as a design opportunity.',
     'accepted', 'DESIGN-OWNER-01', TIMESTAMPTZ '2026-09-22 10:00:00+05:30'),
    (2, 1, 2, 'Display total fare consistently',
     'A consistent fare location will reduce the effort needed to compare routes.',
     'Three linked observations identify fare discovery and comparison problems.',
     'under_test', 'DESIGN-OWNER-01', TIMESTAMPTZ '2026-09-23 10:00:00+05:30');

-- ---------------------------------------------------------------------
-- DESIGN SYSTEM AND WIREFRAMES
-- ---------------------------------------------------------------------

INSERT INTO design_tokens (
    token_id, project_id, token_name, token_value, token_type, description
) OVERRIDING SYSTEM VALUE
VALUES
    (1, 1, 'color.text', '#17212B', 'color', 'Primary text color.'),
    (2, 1, 'color.surface', '#FFFFFF', 'color', 'Primary content surface.'),
    (3, 1, 'color.action', '#1247A8', 'color', 'Primary interactive color.'),
    (4, 1, 'space.medium', '16px', 'spacing', 'Standard component spacing.');

INSERT INTO design_components (
    component_id, project_id, component_name, component_category,
    specification, interactive, keyboard_accessible,
    accessible_description, contrast_ratio, version_number
) OVERRIDING SYSTEM VALUE
VALUES
    (1, 1, 'SearchField', 'form',
     '{"label":"Origin and destination","input_type":"text"}'::jsonb,
     TRUE, TRUE, 'Origin and destination input field.', 12.5, 1),
    (2, 1, 'PrimaryButton', 'action',
     '{"role":"button","state":"enabled"}'::jsonb,
     TRUE, TRUE, 'Submit route search.', 8.9, 1),
    (3, 1, 'RouteCard', 'navigation',
     '{"selection":"single","content":"journey option"}'::jsonb,
     TRUE, TRUE, 'Selectable public transport journey option.', 7.2, 1);

INSERT INTO wireframe_screens (
    screen_id, project_id, screen_name, accessible_name,
    layout_structure, keyboard_order, screen_status
) OVERRIDING SYSTEM VALUE
VALUES
    (1, 1, 'Route Search',
     'Search for a public transport journey',
     '{"regions":["header","search-form","recent-searches"]}'::jsonb,
     ARRAY['SearchField', 'PrimaryButton'],
     'review'),
    (2, 1, 'Route Results',
     'Available journey options',
     '{"regions":["header","journey-summary","route-list","filters"]}'::jsonb,
     ARRAY['RouteCard', 'PrimaryButton'],
     'review');

INSERT INTO screen_components (
    project_id, screen_id, component_id, display_order
)
VALUES
    (1, 1, 1, 1),
    (1, 1, 2, 2),
    (1, 2, 3, 1),
    (1, 2, 2, 2);

INSERT INTO prototypes (
    prototype_id, project_id, version_label, prototype_status, published_at
) OVERRIDING SYSTEM VALUE
VALUES (
    1, 1, 'v1.0', 'testing', TIMESTAMPTZ '2026-10-01 09:00:00+05:30'
);

INSERT INTO prototype_screens (prototype_id, screen_id, project_id)
VALUES (1, 1, 1), (1, 2, 1);

-- Three independent participant test runs provide a minimal test sample.
INSERT INTO usability_test_runs (
    test_run_id, project_id, prototype_id, participant_id,
    started_at, duration_minutes, moderator_notes
) OVERRIDING SYSTEM VALUE
VALUES
    (1, 1, 1, 7, TIMESTAMPTZ '2026-10-02 10:00:00+05:30', 20, 'Search and route selection.'),
    (2, 1, 1, 8, TIMESTAMPTZ '2026-10-03 11:00:00+05:30', 25, 'Route comparison and transfers.'),
    (3, 1, 1, 9, TIMESTAMPTZ '2026-10-04 12:00:00+05:30', 22, 'Fare discovery and return journey.');

INSERT INTO usability_task_results (
    project_id, test_run_id, task_name, succeeded,
    duration_seconds, critical_errors, observed_issue
)
VALUES
    (1, 1, 'Find the fastest route', TRUE, 62, 0, NULL),
    (1, 1, 'Compare journey options', TRUE, 75, 0, NULL),
    (1, 1, 'Identify transfer points', TRUE, 81, 0, NULL),
    (1, 2, 'Find the complete fare', FALSE, 110, 0,
     'Participant did not find the fare breakdown.'),
    (1, 2, 'Select an alternative route', TRUE, 74, 0, NULL),
    (1, 2, 'Review the journey duration', TRUE, 58, 0, NULL),
    (1, 3, 'Compare fare categories', TRUE, 68, 0, NULL),
    (1, 3, 'Search for a return journey', TRUE, 69, 0, NULL),
    (1, 3, 'Identify interchange locations', TRUE, 71, 0, NULL);

INSERT INTO critique_issues (
    critique_id, project_id, screen_id, heuristic, severity,
    description, recommendation, resolved, resolved_at
) OVERRIDING SYSTEM VALUE
VALUES
    (1, 1, 2, 'Visibility of system status', 'medium',
     'The selected route does not have a persistent visual indicator.',
     'Add a selected state and accessible state announcement.',
     FALSE, NULL),
    (2, 1, 1, 'Error prevention', 'critical',
     'The early prototype accepted an empty origin.',
     'Require a valid origin before route calculation.',
     TRUE, TIMESTAMPTZ '2026-10-05 15:00:00+05:30');

COMMIT;

-- Identity values were inserted explicitly for a reproducible example.
-- Reset the sequences so subsequent generated rows do not collide.
SELECT setval(
    pg_get_serial_sequence('projects', 'project_id'),
    (SELECT MAX(project_id) FROM projects)
);
SELECT setval(
    pg_get_serial_sequence('research_studies', 'study_id'),
    (SELECT MAX(study_id) FROM research_studies)
);
SELECT setval(
    pg_get_serial_sequence('participants', 'participant_id'),
    (SELECT MAX(participant_id) FROM participants)
);
SELECT setval(
    pg_get_serial_sequence('research_sessions', 'session_id'),
    (SELECT MAX(session_id) FROM research_sessions)
);
SELECT setval(
    pg_get_serial_sequence('research_observations', 'observation_id'),
    (SELECT MAX(observation_id) FROM research_observations)
);
SELECT setval(
    pg_get_serial_sequence('research_tags', 'tag_id'),
    (SELECT MAX(tag_id) FROM research_tags)
);
SELECT setval(
    pg_get_serial_sequence('research_themes', 'theme_id'),
    (SELECT MAX(theme_id) FROM research_themes)
);
SELECT setval(
    pg_get_serial_sequence('design_decisions', 'decision_id'),
    (SELECT MAX(decision_id) FROM design_decisions)
);
SELECT setval(
    pg_get_serial_sequence('design_tokens', 'token_id'),
    (SELECT MAX(token_id) FROM design_tokens)
);
SELECT setval(
    pg_get_serial_sequence('design_components', 'component_id'),
    (SELECT MAX(component_id) FROM design_components)
);
SELECT setval(
    pg_get_serial_sequence('wireframe_screens', 'screen_id'),
    (SELECT MAX(screen_id) FROM wireframe_screens)
);
SELECT setval(
    pg_get_serial_sequence('prototypes', 'prototype_id'),
    (SELECT MAX(prototype_id) FROM prototypes)
);
SELECT setval(
    pg_get_serial_sequence('usability_test_runs', 'test_run_id'),
    (SELECT MAX(test_run_id) FROM usability_test_runs)
);
SELECT setval(
    pg_get_serial_sequence('critique_issues', 'critique_id'),
    (SELECT MAX(critique_id) FROM critique_issues)
);

-- ---------------------------------------------------------------------
-- REPORTING AND VALIDATION QUERIES
-- ---------------------------------------------------------------------

-- 1. Prioritize research themes using their evidence and effort.
SELECT
    theme_name,
    evidence_count,
    average_severity,
    average_confidence,
    effort_hours,
    priority_score
FROM v_theme_strength
WHERE project_id = 1
ORDER BY priority_score DESC;

-- 2. Retrieve the evidence trail behind each theme.
SELECT
    t.theme_name,
    o.observation_id,
    o.observation_text,
    o.severity,
    o.confidence,
    te.rationale
FROM theme_evidence te
JOIN research_themes t
    ON t.theme_id = te.theme_id
   AND t.project_id = te.project_id
JOIN research_observations o
    ON o.observation_id = te.observation_id
   AND o.project_id = te.project_id
WHERE te.project_id = 1
ORDER BY t.theme_name, o.observation_id;

-- 3. Report usability performance by prototype.
SELECT
    p.version_label,
    COUNT(DISTINCT r.test_run_id) AS test_runs,
    COUNT(tr.task_result_id) AS total_tasks,
    COUNT(*) FILTER (WHERE tr.succeeded) AS successful_tasks,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE tr.succeeded)
        / NULLIF(COUNT(tr.task_result_id), 0),
        2
    ) AS task_success_percentage,
    ROUND(AVG(tr.duration_seconds), 1) AS average_task_seconds,
    COALESCE(SUM(tr.critical_errors), 0) AS critical_errors
FROM prototypes p
LEFT JOIN usability_test_runs r
    ON r.prototype_id = p.prototype_id
   AND r.project_id = p.project_id
LEFT JOIN usability_task_results tr
    ON tr.test_run_id = r.test_run_id
   AND tr.project_id = r.project_id
WHERE p.project_id = 1
GROUP BY p.prototype_id, p.version_label;

-- 4. Find unresolved critique issues by severity.
SELECT
    s.screen_name,
    ci.heuristic,
    ci.severity,
    ci.description,
    ci.recommendation
FROM critique_issues ci
JOIN wireframe_screens s
    ON s.screen_id = ci.screen_id
   AND s.project_id = ci.project_id
WHERE ci.project_id = 1
  AND ci.resolved = FALSE
ORDER BY
    CASE ci.severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        ELSE 4
    END;

-- 5. Compare screen composition with the design-system component catalogue.
SELECT
    s.screen_name,
    sc.display_order,
    dc.component_name,
    dc.interactive,
    dc.keyboard_accessible,
    dc.contrast_ratio,
    dc.accessible_description
FROM wireframe_screens s
JOIN screen_components sc
    ON sc.screen_id = s.screen_id
   AND sc.project_id = s.project_id
JOIN design_components dc
    ON dc.component_id = sc.component_id
   AND dc.project_id = sc.project_id
WHERE s.project_id = 1
ORDER BY s.screen_id, sc.display_order;

-- 6. Evaluate the design gate before changing the project stage.
SELECT *
FROM fn_design_readiness(1);

-- 7. CTE-based decision report joining research priorities and task outcomes.
WITH theme_priorities AS (
    SELECT
        project_id,
        SUM(priority_score) AS total_theme_priority,
        COUNT(*) AS theme_count
    FROM v_theme_strength
    WHERE project_id = 1
    GROUP BY project_id
),
prototype_performance AS (
    SELECT
        project_id,
        COUNT(*) AS task_count,
        ROUND(AVG(succeeded::INTEGER)::NUMERIC, 3) AS success_rate
    FROM usability_task_results
    WHERE project_id = 1
    GROUP BY project_id
)
SELECT
    p.project_name,
    p.stage,
    tp.theme_count,
    tp.total_theme_priority,
    pp.task_count,
    pp.success_rate
FROM projects p
JOIN theme_priorities tp ON tp.project_id = p.project_id
JOIN prototype_performance pp ON pp.project_id = p.project_id
WHERE p.project_id = 1;

-- 8. The trigger rejects this transition if the quality gate fails.
UPDATE projects
SET stage = 'validated'
WHERE project_id = 1;

SELECT project_name, stage, updated_at
FROM projects
WHERE project_id = 1;
