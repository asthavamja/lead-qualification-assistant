CREATE TABLE IF NOT EXISTS service_catalog (
    slug TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'INR',
    price_min NUMERIC(12, 2),
    price_max NUMERIC(12, 2),
    billing_period TEXT,
    timeline_min INTEGER,
    timeline_max INTEGER,
    timeline_unit TEXT,
    price_note TEXT NOT NULL,
    details TEXT NOT NULL DEFAULT '{}',
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT service_catalog_valid_price_range
        CHECK (price_min IS NULL OR price_max IS NULL OR price_min <= price_max),
    CONSTRAINT service_catalog_valid_timeline_range
        CHECK (
            timeline_min IS NULL
            OR timeline_max IS NULL
            OR timeline_min <= timeline_max
        )
);

CREATE TABLE IF NOT EXISTS project_process_steps (
    step_number SMALLINT PRIMARY KEY CHECK (step_number > 0),
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    timing_note TEXT
);

CREATE TABLE IF NOT EXISTS company_policies (
    policy_key TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    policy_text TEXT NOT NULL,
    requires_human_review INTEGER NOT NULL DEFAULT 0
        CHECK (requires_human_review IN (0, 1))
);

CREATE INDEX IF NOT EXISTS company_policies_category_idx
    ON company_policies (category);
