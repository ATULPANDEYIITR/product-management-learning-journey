DROP SCHEMA IF EXISTS ux_fundamentals CASCADE;
CREATE SCHEMA ux_fundamentals;

SET search_path TO ux_fundamentals, public;

CREATE TYPE severity AS ENUM (
    'info',
    'minor',
    'major',
    'critical'
);

CREATE TYPE issue_type AS ENUM (
    'ui',
    'usability',
    'accessibility',
    'interaction',
    'information_architecture'
);

CREATE TYPE control_type AS ENUM (
    'button',
    'link',
    'input',
    'checkbox',
    'select'
);

CREATE TYPE task_status AS ENUM (
    'completed',
    'failed',
    'abandoned'
);

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    display_name TEXT NOT NULL,
    keyboard_only BOOLEAN NOT NULL DEFAULT FALSE,
    screen_reader_user BOOLEAN NOT NULL DEFAULT FALSE,
    reduced_motion BOOLEAN NOT NULL DEFAULT FALSE,
    low_vision BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE screens (
    screen_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    screen_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    primary_action TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (btrim(screen_key) <> ''),
    CHECK (btrim(title) <> ''),
    CHECK (btrim(primary_action) <> '')
);

CREATE TABLE navigation_items (
    navigation_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    screen_id BIGINT NOT NULL REFERENCES screens(screen_id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    UNIQUE (screen_id, position),
    UNIQUE (screen_id, label)
);

CREATE TABLE content_sections (
    section_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    screen_id BIGINT NOT NULL REFERENCES screens(screen_id) ON DELETE CASCADE,
    heading TEXT NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    UNIQUE (screen_id, position),
    CHECK (btrim(heading) <> '')
);

CREATE TABLE controls (
    control_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    screen_id BIGINT NOT NULL REFERENCES screens(screen_id) ON DELETE CASCADE,
    control_key TEXT NOT NULL,
    control_type control_type NOT NULL,
    accessible_name TEXT,
    keyboard_reachable BOOLEAN NOT NULL DEFAULT FALSE,
    visible BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (screen_id, control_key)
);

CREATE TABLE focus_order (
    focus_order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    screen_id BIGINT NOT NULL REFERENCES screens(screen_id) ON DELETE CASCADE,
    control_id BIGINT NOT NULL REFERENCES controls(control_id) ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position > 0),
    UNIQUE (screen_id, position),
    UNIQUE (screen_id, control_id)
);

CREATE TABLE contrast_tokens (
    contrast_token_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    screen_id BIGINT NOT NULL REFERENCES screens(screen_id) ON DELETE CASCADE,
    token_name TEXT NOT NULL,
    ratio NUMERIC(5,2) NOT NULL CHECK (ratio > 0),
    UNIQUE (screen_id, token_name)
);

CREATE TABLE ux_issues (
    issue_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    screen_id BIGINT REFERENCES screens(screen_id) ON DELETE CASCADE,
    issue_type issue_type NOT NULL,
    severity severity NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    detected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (status IN ('open', 'accepted', 'resolved')),
    CHECK (btrim(description) <> ''),
    CHECK (btrim(recommendation) <> '')
);

CREATE TABLE usability_sessions (
    session_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMPTZ
);

CREATE TABLE usability_tasks (
    task_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES usability_sessions(session_id) ON DELETE CASCADE,
    task_name TEXT NOT NULL,
    status task_status NOT NULL,
    duration_seconds NUMERIC(10,2) NOT NULL CHECK (duration_seconds >= 0),
    steps INTEGER NOT NULL CHECK (steps > 0),
    errors INTEGER NOT NULL CHECK (errors >= 0 AND errors <= steps),
    notes TEXT
);

CREATE TABLE issue_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    issue_id BIGINT NOT NULL REFERENCES ux_issues(issue_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK (
        event_type IN ('created', 'accepted', 'resolved', 'reopened')
    ),
    event_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION validate_primary_action()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM controls c
        WHERE c.screen_id = NEW.screen_id
          AND c.control_key = NEW.primary_action
    ) THEN
        RAISE EXCEPTION
            'Primary action "%" does not exist as a control on screen %',
            NEW.primary_action,
            NEW.screen_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE CONSTRAINT TRIGGER screens_primary_action_trigger
AFTER INSERT OR UPDATE OF primary_action
ON screens
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION validate_primary_action();

CREATE OR REPLACE FUNCTION prevent_duplicate_focus_positions()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM focus_order
        WHERE screen_id = NEW.screen_id
          AND position = NEW.position
          AND focus_order_id <> NEW.focus_order_id
    ) THEN
        RAISE EXCEPTION
            'Duplicate focus position % on screen %',
            NEW.position,
            NEW.screen_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER focus_order_validation
BEFORE INSERT OR UPDATE
ON focus_order
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_focus_positions();

CREATE OR REPLACE FUNCTION record_issue_event()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO issue_events(issue_id, event_type)
    VALUES (NEW.issue_id, 'created');

    RETURN NEW;
END;
$$;

CREATE TRIGGER issue_creation_event
AFTER INSERT ON ux_issues
FOR EACH ROW
EXECUTE FUNCTION record_issue_event();

CREATE INDEX idx_navigation_screen_position
    ON navigation_items(screen_id, position);

CREATE INDEX idx_controls_screen_keyboard
    ON controls(screen_id, keyboard_reachable);

CREATE INDEX idx_issues_severity_status
    ON ux_issues(severity, status);

CREATE INDEX idx_tasks_session
    ON usability_tasks(session_id);

INSERT INTO users (
    display_name,
    keyboard_only,
    screen_reader_user,
    reduced_motion,
    low_vision
)
VALUES
    ('Keyboard participant', TRUE, FALSE, TRUE, FALSE),
    ('Screen reader participant', FALSE, TRUE, TRUE, FALSE),
    ('General participant', FALSE, FALSE, FALSE, FALSE);

INSERT INTO screens (
    screen_key,
    title,
    primary_action
)
VALUES
    ('dashboard', 'Project Dashboard', 'create_project'),
    ('settings', 'Account Settings', 'save_settings');

INSERT INTO navigation_items(screen_id, label, position)
SELECT screen_id, item.label, item.position
FROM screens s
CROSS JOIN LATERAL (
    VALUES
        ('Projects', 1),
        ('Reports', 2),
        ('Teams', 3),
        ('Activity', 4),
        ('Integrations', 5),
        ('Billing', 6),
        ('Settings', 7),
        ('Help', 8)
) AS item(label, position)
WHERE s.screen_key = 'dashboard';

INSERT INTO navigation_items(screen_id, label, position)
SELECT screen_id, item.label, item.position
FROM screens s
CROSS JOIN LATERAL (
    VALUES
        ('Projects', 1),
        ('Settings', 2)
) AS item(label, position)
WHERE s.screen_key = 'settings';

INSERT INTO content_sections(screen_id, heading, position)
SELECT screen_id, 'Projects', 1
FROM screens
WHERE screen_key = 'dashboard';

INSERT INTO content_sections(screen_id, heading, position)
SELECT screen_id, 'Recent Activity', 2
FROM screens
WHERE screen_key = 'dashboard';

INSERT INTO content_sections(screen_id, heading, position)
SELECT screen_id, item.heading, item.position
FROM screens s
CROSS JOIN LATERAL (
    VALUES
        ('Profile', 1),
        ('Security', 2),
        ('Account', 3)
) AS item(heading, position)
WHERE s.screen_key = 'settings';

INSERT INTO controls (
    screen_id,
    control_key,
    control_type,
    accessible_name,
    keyboard_reachable
)
SELECT
    s.screen_id,
    item.control_key,
    item.control_type,
    item.accessible_name,
    item.keyboard_reachable
FROM screens s
CROSS JOIN LATERAL (
    VALUES
        (
            'search',
            'input'::control_type,
            'Search projects',
            TRUE
        ),
        (
            'create_project',
            'button'::control_type,
            'Create project',
            TRUE
        ),
        (
            'open_project',
            'link'::control_type,
            'Open project',
            TRUE
        ),
        (
            'account_menu',
            'button'::control_type,
            'Account menu',
            TRUE
        )
) AS item(
    control_key,
    control_type,
    accessible_name,
    keyboard_reachable
)
WHERE s.screen_key = 'dashboard';

INSERT INTO controls (
    screen_id,
    control_key,
    control_type,
    accessible_name,
    keyboard_reachable
)
SELECT
    s.screen_id,
    item.control_key,
    item.control_type,
    item.accessible_name,
    item.keyboard_reachable
FROM screens s
CROSS JOIN LATERAL (
    VALUES
        (
            'account_name',
            'input'::control_type,
            'Account name',
            TRUE
        ),
        (
            'save_settings',
            'button'::control_type,
            'Save settings',
            TRUE
        ),
        (
            'delete_account',
            'button'::control_type,
            NULL::TEXT,
            FALSE
        )
) AS item(
    control_key,
    control_type,
    accessible_name,
    keyboard_reachable
)
WHERE s.screen_key = 'settings';

INSERT INTO focus_order(screen_id, control_id, position)
SELECT
    c.screen_id,
    c.control_id,
    CASE c.control_key
        WHEN 'search' THEN 1
        WHEN 'create_project' THEN 2
        WHEN 'open_project' THEN 3
        WHEN 'account_menu' THEN 4
        WHEN 'account_name' THEN 1
        WHEN 'save_settings' THEN 2
        WHEN 'delete_account' THEN 3
    END
FROM controls c;

INSERT INTO contrast_tokens(screen_id, token_name, ratio)
SELECT
    s.screen_id,
    item.token_name,
    item.ratio
FROM screens s
CROSS JOIN LATERAL (
    VALUES
        ('body_text', 7.2::NUMERIC),
        ('muted_text', 3.3::NUMERIC),
        ('primary_button', 4.9::NUMERIC)
) AS item(token_name, ratio)
WHERE s.screen_key = 'dashboard';

INSERT INTO contrast_tokens(screen_id, token_name, ratio)
SELECT
    s.screen_id,
    item.token_name,
    item.ratio
FROM screens s
CROSS JOIN LATERAL (
    VALUES
        ('body_text', 8.1::NUMERIC),
        ('primary_button', 5.2::NUMERIC)
) AS item(token_name, ratio)
WHERE s.screen_key = 'settings';

INSERT INTO ux_issues (
    screen_id,
    issue_type,
    severity,
    description,
    recommendation
)
SELECT
    s.screen_id,
    'information_architecture',
    'minor',
    'Primary navigation contains more than seven top-level destinations.',
    'Group related destinations and reduce navigation breadth.'
FROM screens s
WHERE s.screen_key = 'dashboard'
  AND (
      SELECT COUNT(*)
      FROM navigation_items n
      WHERE n.screen_id = s.screen_id
  ) > 7;

INSERT INTO ux_issues (
    screen_id,
    issue_type,
    severity,
    description,
    recommendation
)
SELECT
    c.screen_id,
    'accessibility',
    'major',
    'Interactive control has no accessible name.',
    'Provide a visible or programmatic accessible name.'
FROM controls c
WHERE c.accessible_name IS NULL
   OR btrim(c.accessible_name) = '';

INSERT INTO ux_issues (
    screen_id,
    issue_type,
    severity,
    description,
    recommendation
)
SELECT
    c.screen_id,
    'accessibility',
    'critical',
    'Interactive control is not keyboard reachable.',
    'Make the control available through keyboard interaction.'
FROM controls c
WHERE NOT c.keyboard_reachable;

INSERT INTO ux_issues (
    screen_id,
    issue_type,
    severity,
    description,
    recommendation
)
SELECT
    contrast_token_id,
    'accessibility',
    'major',
    'Contrast ratio is below the normal-text AA threshold.',
    'Use a compliant foreground and background combination.'
FROM contrast_tokens ct
WHERE ct.ratio < 4.5;

INSERT INTO usability_sessions(user_id, ended_at)
SELECT user_id, CURRENT_TIMESTAMP
FROM users
WHERE display_name = 'Keyboard participant';

INSERT INTO usability_tasks (
    session_id,
    task_name,
    status,
    duration_seconds,
    steps,
    errors,
    notes
)
SELECT
    us.session_id,
    task.task_name,
    task.status,
    task.duration_seconds,
    task.steps,
    task.errors,
    task.notes
FROM usability_sessions us
CROSS JOIN LATERAL (
    VALUES
        (
            'Find project',
            'completed'::task_status,
            18.4::NUMERIC,
            5,
            0,
            'Search was easy to discover.'
        ),
        (
            'Create project',
            'completed'::task_status,
            31.7::NUMERIC,
            7,
            1,
            'Primary action was clearly visible.'
        ),
        (
            'Change account settings',
            'failed'::task_status,
            44.2::NUMERIC,
            8,
            3,
            'Account action produced repeated errors.'
        )
) AS task(
    task_name,
    status,
    duration_seconds,
    steps,
    errors,
    notes
)
WHERE us.session_id = (
    SELECT MIN(session_id)
    FROM usability_sessions
);

CREATE OR REPLACE VIEW accessibility_findings AS
SELECT
    s.screen_key,
    c.control_key,
    CASE
        WHEN c.accessible_name IS NULL OR btrim(c.accessible_name) = ''
            THEN 'missing_accessible_name'
        WHEN NOT c.keyboard_reachable
            THEN 'keyboard_inaccessible'
        ELSE 'pass'
    END AS finding
FROM screens s
JOIN controls c
    ON c.screen_id = s.screen_id;

CREATE OR REPLACE VIEW contrast_findings AS
SELECT
    s.screen_key,
    ct.token_name,
    ct.ratio,
    CASE
        WHEN ct.ratio >= 4.5 THEN 'pass'
        ELSE 'below_aa_normal_text_threshold'
    END AS finding
FROM screens s
JOIN contrast_tokens ct
    ON ct.screen_id = s.screen_id;

CREATE OR REPLACE VIEW navigation_findings AS
SELECT
    s.screen_key,
    COUNT(n.navigation_item_id) AS top_level_items,
    CASE
        WHEN COUNT(n.navigation_item_id) <= 7 THEN 'manageable'
        ELSE 'broad_navigation'
    END AS finding
FROM screens s
LEFT JOIN navigation_items n
    ON n.screen_id = s.screen_id
GROUP BY s.screen_id, s.screen_key;

CREATE OR REPLACE VIEW usability_metrics AS
SELECT
    us.session_id,
    u.display_name,
    ROUND(
        100.0 * AVG(
            CASE WHEN ut.status = 'completed' THEN 1.0 ELSE 0.0 END
        ),
        2
    ) AS completion_rate_percent,
    ROUND(AVG(ut.duration_seconds), 2) AS average_duration_seconds,
    ROUND(
        100.0 * SUM(ut.errors)::NUMERIC / NULLIF(SUM(ut.steps), 0),
        2
    ) AS error_rate_percent
FROM usability_sessions us
JOIN users u
    ON u.user_id = us.user_id
JOIN usability_tasks ut
    ON ut.session_id = us.session_id
GROUP BY us.session_id, u.display_name;

-- Retrieval: all open critical and major UX findings.
SELECT
    s.screen_key,
    ui.issue_type,
    ui.severity,
    ui.description,
    ui.recommendation
FROM ux_issues ui
LEFT JOIN screens s
    ON s.screen_id = ui.screen_id
WHERE ui.status = 'open'
  AND ui.severity IN ('critical', 'major')
ORDER BY
    CASE ui.severity
        WHEN 'critical' THEN 1
        WHEN 'major' THEN 2
        ELSE 3
    END,
    s.screen_key;

-- Accessibility validation.
SELECT *
FROM accessibility_findings
WHERE finding <> 'pass'
ORDER BY screen_key, control_key;

-- Contrast validation.
SELECT *
FROM contrast_findings
WHERE finding <> 'pass'
ORDER BY screen_key, token_name;

-- Information-architecture reporting.
SELECT *
FROM navigation_findings
ORDER BY top_level_items DESC;

-- Usability evaluation.
SELECT *
FROM usability_metrics
ORDER BY session_id;

-- Workflow state: unresolved issues by type and severity.
SELECT
    issue_type,
    severity,
    COUNT(*) AS issue_count
FROM ux_issues
WHERE status <> 'resolved'
GROUP BY issue_type, severity
ORDER BY issue_type, severity;

-- Eligibility query: a screen is release-ready only when it has
-- no open critical accessibility findings and no open major findings.
WITH blocking_issues AS (
    SELECT
        s.screen_id,
        COUNT(*) AS blocking_count
    FROM screens s
    JOIN ux_issues ui
        ON ui.screen_id = s.screen_id
    WHERE ui.status = 'open'
      AND ui.severity IN ('critical', 'major')
    GROUP BY s.screen_id
)
SELECT
    s.screen_key,
    COALESCE(b.blocking_count, 0) AS blocking_issues,
    CASE
        WHEN COALESCE(b.blocking_count, 0) = 0 THEN 'eligible'
        ELSE 'blocked'
    END AS release_eligibility
FROM screens s
LEFT JOIN blocking_issues b
    ON b.screen_id = s.screen_id
ORDER BY s.screen_key;

-- Transactional example: resolve one issue and record the state change.
BEGIN;

WITH selected_issue AS (
    SELECT issue_id
    FROM ux_issues
    WHERE status = 'open'
      AND severity = 'minor'
    ORDER BY issue_id
    LIMIT 1
)
UPDATE ux_issues ui
SET status = 'resolved'
FROM selected_issue si
WHERE ui.issue_id = si.issue_id;

INSERT INTO issue_events(issue_id, event_type)
SELECT issue_id, 'resolved'
FROM ux_issues
WHERE status = 'resolved'
  AND issue_id = (
      SELECT MAX(issue_id)
      FROM ux_issues
      WHERE status = 'resolved'
  );

COMMIT;

-- Final governance report.
SELECT
    s.screen_key,
    COUNT(ui.issue_id) FILTER (
        WHERE ui.status = 'open'
    ) AS open_issues,
    COUNT(ui.issue_id) FILTER (
        WHERE ui.status = 'open'
          AND ui.severity = 'critical'
    ) AS critical_open,
    COUNT(ui.issue_id) FILTER (
        WHERE ui.status = 'open'
          AND ui.severity = 'major'
    ) AS major_open,
    CASE
        WHEN COUNT(ui.issue_id) FILTER (
            WHERE ui.status = 'open'
              AND ui.severity IN ('critical', 'major')
        ) = 0
        THEN 'eligible'
        ELSE 'blocked'
    END AS release_status
FROM screens s
LEFT JOIN ux_issues ui
    ON ui.screen_id = s.screen_id
GROUP BY s.screen_id, s.screen_key
ORDER BY s.screen_key;
