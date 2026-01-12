-- OpenPulse Database Schema
-- PostgreSQL 13+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Repositories table
CREATE TABLE IF NOT EXISTS repositories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(50) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    repo VARCHAR(255) NOT NULL,
    full_name VARCHAR(512) GENERATED ALWAYS AS (owner || '/' || repo) STORED,
    description TEXT,
    stars INTEGER DEFAULT 0,
    forks INTEGER DEFAULT 0,
    watchers INTEGER DEFAULT 0,
    open_issues INTEGER DEFAULT 0,
    language VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_analyzed_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(platform, owner, repo)
);

CREATE INDEX idx_repositories_platform_owner_repo ON repositories(platform, owner, repo);
CREATE INDEX idx_repositories_is_active ON repositories(is_active);
CREATE INDEX idx_repositories_last_analyzed ON repositories(last_analyzed_at);

-- Contributors table
CREATE TABLE IF NOT EXISTS contributors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    username VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    email VARCHAR(255),
    name VARCHAR(255),
    openrank DECIMAL(10, 2),
    total_commits INTEGER DEFAULT 0,
    total_prs INTEGER DEFAULT 0,
    total_issues INTEGER DEFAULT 0,
    total_reviews INTEGER DEFAULT 0,
    first_contribution_at TIMESTAMP WITH TIME ZONE,
    last_contribution_at TIMESTAMP WITH TIME ZONE,
    contribution_frequency VARCHAR(20), -- high, medium, low
    role VARCHAR(20), -- core, regular, occasional
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(repository_id, username, platform)
);

CREATE INDEX idx_contributors_repository ON contributors(repository_id);
CREATE INDEX idx_contributors_username ON contributors(username);
CREATE INDEX idx_contributors_role ON contributors(role);
CREATE INDEX idx_contributors_last_contribution ON contributors(last_contribution_at);

-- Health scores table
CREATE TABLE IF NOT EXISTS health_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    overall_score DECIMAL(5, 2) NOT NULL,
    health_level VARCHAR(20), -- critical, warning, healthy, excellent
    lifecycle_stage VARCHAR(20), -- embryonic, growth, mature, decline

    -- Dimension scores
    activity_score DECIMAL(5, 2),
    diversity_score DECIMAL(5, 2),
    response_time_score DECIMAL(5, 2),
    code_quality_score DECIMAL(5, 2),
    documentation_score DECIMAL(5, 2),
    community_atmosphere_score DECIMAL(5, 2),

    -- Metadata
    analysis_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(repository_id, analysis_date)
);

CREATE INDEX idx_health_scores_repository ON health_scores(repository_id);
CREATE INDEX idx_health_scores_date ON health_scores(analysis_date);
CREATE INDEX idx_health_scores_overall ON health_scores(overall_score);
CREATE INDEX idx_health_scores_health_level ON health_scores(health_level);

-- Churn predictions table
CREATE TABLE IF NOT EXISTS churn_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    contributor_id UUID REFERENCES contributors(id) ON DELETE CASCADE,

    -- Prediction scores
    overall_risk_score DECIMAL(5, 2) NOT NULL,
    risk_level VARCHAR(20), -- green, yellow, orange, red
    confidence DECIMAL(5, 4),
    prediction_horizon_months INTEGER,

    -- Risk factor scores
    behavioral_decay_score DECIMAL(5, 2),
    network_marginalization_score DECIMAL(5, 2),
    temporal_anomaly_score DECIMAL(5, 2),
    community_engagement_score DECIMAL(5, 2),

    -- Metadata
    prediction_date DATE NOT NULL,
    alert_message TEXT,
    recommendations JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(repository_id, contributor_id, prediction_date)
);

CREATE INDEX idx_churn_predictions_repository ON churn_predictions(repository_id);
CREATE INDEX idx_churn_predictions_contributor ON churn_predictions(contributor_id);
CREATE INDEX idx_churn_predictions_risk_level ON churn_predictions(risk_level);
CREATE INDEX idx_churn_predictions_date ON churn_predictions(prediction_date);

-- Analysis tasks table
CREATE TABLE IF NOT EXISTS analysis_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    task_type VARCHAR(50) NOT NULL, -- health_assessment, churn_prediction, network_analysis
    status VARCHAR(20) NOT NULL, -- pending, running, completed, failed
    celery_task_id VARCHAR(255),

    -- Task parameters
    parameters JSONB,

    -- Results
    result JSONB,
    error_message TEXT,

    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analysis_tasks_repository ON analysis_tasks(repository_id);
CREATE INDEX idx_analysis_tasks_status ON analysis_tasks(status);
CREATE INDEX idx_analysis_tasks_type ON analysis_tasks(task_type);
CREATE INDEX idx_analysis_tasks_celery_id ON analysis_tasks(celery_task_id);

-- Network analysis results table
CREATE TABLE IF NOT EXISTS network_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,

    -- Network metrics
    total_nodes INTEGER,
    total_edges INTEGER,
    density DECIMAL(5, 4),
    average_degree DECIMAL(8, 2),
    average_clustering DECIMAL(5, 4),
    number_of_communities INTEGER,
    modularity DECIMAL(5, 4),
    diameter INTEGER,
    average_path_length DECIMAL(8, 2),

    -- Bus factor
    bus_factor INTEGER,
    bus_factor_risk_level VARCHAR(20),

    -- Full network data (stored as JSON)
    network_data JSONB,

    -- Metadata
    analysis_date DATE NOT NULL,
    time_window VARCHAR(50), -- last_month, last_3_months, last_6_months, last_year
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(repository_id, analysis_date, time_window)
);

CREATE INDEX idx_network_analysis_repository ON network_analysis(repository_id);
CREATE INDEX idx_network_analysis_date ON network_analysis(analysis_date);
CREATE INDEX idx_network_analysis_bus_factor ON network_analysis(bus_factor);

-- Structural holes table
CREATE TABLE IF NOT EXISTS structural_holes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    network_analysis_id UUID REFERENCES network_analysis(id) ON DELETE CASCADE,
    contributor_id UUID REFERENCES contributors(id) ON DELETE CASCADE,

    -- Structural hole metrics
    constraint_score DECIMAL(5, 4),
    effective_size DECIMAL(8, 2),
    efficiency DECIMAL(5, 4),
    hierarchy DECIMAL(5, 4),
    bridge_score DECIMAL(5, 4),

    -- Risk assessment
    is_critical_bridge BOOLEAN DEFAULT FALSE,
    risk_level VARCHAR(20),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(network_analysis_id, contributor_id)
);

CREATE INDEX idx_structural_holes_network ON structural_holes(network_analysis_id);
CREATE INDEX idx_structural_holes_contributor ON structural_holes(contributor_id);
CREATE INDEX idx_structural_holes_critical ON structural_holes(is_critical_bridge);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_repositories_updated_at BEFORE UPDATE ON repositories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contributors_updated_at BEFORE UPDATE ON contributors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_tasks_updated_at BEFORE UPDATE ON analysis_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries

-- Active repositories with latest health scores
CREATE OR REPLACE VIEW v_active_repositories_health AS
SELECT
    r.id,
    r.platform,
    r.owner,
    r.repo,
    r.full_name,
    r.stars,
    r.forks,
    r.language,
    r.last_analyzed_at,
    hs.overall_score,
    hs.health_level,
    hs.lifecycle_stage,
    hs.analysis_date
FROM repositories r
LEFT JOIN LATERAL (
    SELECT * FROM health_scores
    WHERE repository_id = r.id
    ORDER BY analysis_date DESC
    LIMIT 1
) hs ON TRUE
WHERE r.is_active = TRUE;

-- High-risk contributors
CREATE OR REPLACE VIEW v_high_risk_contributors AS
SELECT
    r.platform,
    r.owner,
    r.repo,
    c.username,
    c.role,
    c.openrank,
    c.last_contribution_at,
    cp.overall_risk_score,
    cp.risk_level,
    cp.prediction_date,
    cp.alert_message
FROM churn_predictions cp
JOIN contributors c ON cp.contributor_id = c.id
JOIN repositories r ON cp.repository_id = r.id
WHERE cp.risk_level IN ('orange', 'red')
    AND cp.prediction_date = CURRENT_DATE
ORDER BY cp.overall_risk_score DESC;

-- Repository health trends
CREATE OR REPLACE VIEW v_repository_health_trends AS
SELECT
    r.id AS repository_id,
    r.platform,
    r.owner,
    r.repo,
    hs.analysis_date,
    hs.overall_score,
    hs.health_level,
    LAG(hs.overall_score) OVER (PARTITION BY r.id ORDER BY hs.analysis_date) AS previous_score,
    hs.overall_score - LAG(hs.overall_score) OVER (PARTITION BY r.id ORDER BY hs.analysis_date) AS score_change
FROM repositories r
JOIN health_scores hs ON r.id = hs.repository_id
WHERE r.is_active = TRUE
ORDER BY r.id, hs.analysis_date DESC;
