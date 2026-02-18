-- KEMENKEU Regulation Database - Analytics Tables
-- Usage analytics, conversion tracking, and performance monitoring
-- Real-time metrics and reporting system

-- ============================================================================
-- CONVERSION TRACKING TABLES
-- ============================================================================

-- Conversion jobs - track the conversion process for each regulation
CREATE TABLE conversion_jobs (
    id BIGSERIAL PRIMARY KEY,
    regulation_id BIGINT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL, -- 'pdf_to_text', 'text_processing', 'metadata_extraction', 'quality_check'
    status VARCHAR(30) NOT NULL DEFAULT 'pending', -- pending, processing, completed, failed, cancelled
    priority INTEGER DEFAULT 100, -- Lower number = higher priority
    
    -- Timing metrics
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_duration INTERVAL,
    
    -- Progress tracking
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    current_step VARCHAR(100),
    total_steps INTEGER,
    
    -- Resource usage
    memory_usage_mb INTEGER,
    cpu_time_seconds DECIMAL(10,3),
    
    -- Quality metrics
    input_quality_score DECIMAL(3,2), -- Quality of input document
    output_quality_score DECIMAL(3,2), -- Quality of conversion result
    error_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    
    -- Error handling
    error_message TEXT,
    error_details JSONB,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- Metadata
    assigned_worker VARCHAR(100), -- Worker process/server handling the job
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    CONSTRAINT chk_progress CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    CONSTRAINT chk_quality_scores CHECK (
        (input_quality_score IS NULL OR (input_quality_score >= 0 AND input_quality_score <= 10)) AND
        (output_quality_score IS NULL OR (output_quality_score >= 0 AND output_quality_score <= 10))
    )
);

-- Conversion pipeline stages - detailed step-by-step tracking
CREATE TABLE conversion_pipeline_stages (
    id BIGSERIAL PRIMARY KEY,
    job_id BIGINT NOT NULL REFERENCES conversion_jobs(id) ON DELETE CASCADE,
    stage_name VARCHAR(100) NOT NULL,
    stage_order INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration INTERVAL,
    
    -- Metrics
    input_size_bytes BIGINT,
    output_size_bytes BIGINT,
    processing_speed DECIMAL(10,2), -- bytes per second or pages per minute
    
    -- Results
    success_rate DECIMAL(5,2), -- Percentage of successful processing
    artifacts_generated INTEGER DEFAULT 0, -- Number of output files/data created
    
    -- Issues
    errors JSONB, -- Structured error information
    warnings JSONB, -- Structured warning information
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(job_id, stage_name)
);

-- Quality assessments - detailed quality metrics for converted content
CREATE TABLE quality_assessments (
    id BIGSERIAL PRIMARY KEY,
    regulation_id BIGINT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) NOT NULL, -- 'automated', 'manual', 'expert_review'
    assessor VARCHAR(100), -- Who performed the assessment
    
    -- Overall scores
    overall_quality_score DECIMAL(3,2) NOT NULL,
    content_accuracy DECIMAL(3,2),
    structural_integrity DECIMAL(3,2),
    formatting_quality DECIMAL(3,2),
    metadata_completeness DECIMAL(3,2),
    
    -- Specific metrics
    text_extraction_accuracy DECIMAL(5,2), -- Percentage of text correctly extracted
    table_extraction_success DECIMAL(5,2), -- Percentage of tables properly converted
    image_processing_quality DECIMAL(3,2),
    reference_link_accuracy DECIMAL(5,2), -- Accuracy of cross-references
    
    -- Issues found
    critical_issues_count INTEGER DEFAULT 0,
    major_issues_count INTEGER DEFAULT 0,
    minor_issues_count INTEGER DEFAULT 0,
    issues_detail JSONB, -- Structured list of specific issues
    
    -- Recommendations
    recommended_actions TEXT,
    requires_manual_review BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_quality_scores CHECK (
        overall_quality_score >= 0 AND overall_quality_score <= 10 AND
        (content_accuracy IS NULL OR (content_accuracy >= 0 AND content_accuracy <= 10)) AND
        (structural_integrity IS NULL OR (structural_integrity >= 0 AND structural_integrity <= 10)) AND
        (formatting_quality IS NULL OR (formatting_quality >= 0 AND formatting_quality <= 10)) AND
        (metadata_completeness IS NULL OR (metadata_completeness >= 0 AND metadata_completeness <= 10))
    )
);

-- ============================================================================
-- USAGE ANALYTICS TABLES
-- ============================================================================

-- Access logs - track all access to regulations
CREATE TABLE access_logs (
    id BIGSERIAL PRIMARY KEY,
    regulation_id BIGINT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    
    -- Access details
    access_type VARCHAR(30) NOT NULL, -- 'view', 'download', 'search', 'api_call'
    access_method VARCHAR(50), -- 'web_portal', 'api', 'mobile_app', 'export'
    user_type VARCHAR(30), -- 'public', 'government', 'business', 'researcher', 'developer'
    user_identifier VARCHAR(255), -- Hashed user ID (for privacy)
    
    -- Request details
    ip_address INET,
    user_agent TEXT,
    referrer_url TEXT,
    session_id VARCHAR(100),
    
    -- Geographic info (for public access patterns)
    country_code VARCHAR(2),
    region VARCHAR(100),
    city VARCHAR(100),
    
    -- Technical details
    response_time_ms INTEGER,
    response_size_bytes INTEGER,
    http_status_code INTEGER,
    
    -- Context
    search_query TEXT, -- If accessed via search
    filter_criteria JSONB, -- Applied filters
    
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_access_type CHECK (access_type IN ('view', 'download', 'search', 'api_call', 'export')),
    CONSTRAINT chk_user_type CHECK (user_type IN ('public', 'government', 'business', 'researcher', 'developer', 'unknown'))
);

-- Usage statistics - aggregated usage metrics
CREATE TABLE usage_statistics (
    id BIGSERIAL PRIMARY KEY,
    regulation_id BIGINT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    
    -- Time period
    period_type VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly', 'yearly'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Access counts
    total_views INTEGER DEFAULT 0,
    total_downloads INTEGER DEFAULT 0,
    unique_visitors INTEGER DEFAULT 0,
    api_calls INTEGER DEFAULT 0,
    
    -- User breakdown
    public_users INTEGER DEFAULT 0,
    government_users INTEGER DEFAULT 0,
    business_users INTEGER DEFAULT 0,
    researcher_users INTEGER DEFAULT 0,
    
    -- Geographic breakdown
    domestic_access INTEGER DEFAULT 0,
    international_access INTEGER DEFAULT 0,
    top_countries JSONB, -- Array of {country_code, count} objects
    
    -- Performance metrics
    avg_response_time_ms DECIMAL(8,2),
    bounce_rate DECIMAL(5,2), -- Percentage of single-page sessions
    
    -- Trends
    growth_rate DECIMAL(6,2), -- Percentage growth from previous period
    popularity_rank INTEGER, -- Rank among all regulations for this period
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(regulation_id, period_type, period_start),
    CONSTRAINT chk_period_type CHECK (period_type IN ('daily', 'weekly', 'monthly', 'yearly'))
);

-- Search analytics - track search behavior and effectiveness
CREATE TABLE search_analytics (
    id BIGSERIAL PRIMARY KEY,
    
    -- Search details
    search_query TEXT NOT NULL,
    normalized_query TEXT, -- Cleaned/normalized version
    search_type VARCHAR(30), -- 'basic', 'advanced', 'semantic', 'autocomplete'
    filters_applied JSONB, -- Applied filters
    
    -- Results
    results_count INTEGER,
    clicked_results INTEGER DEFAULT 0, -- How many results were actually clicked
    first_click_position INTEGER, -- Position of first clicked result
    
    -- User context
    user_type VARCHAR(30),
    user_identifier VARCHAR(255), -- Hashed
    session_id VARCHAR(100),
    
    -- Performance
    search_duration_ms INTEGER,
    
    -- Geographic
    country_code VARCHAR(2),
    
    searched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_search_type CHECK (search_type IN ('basic', 'advanced', 'semantic', 'autocomplete', 'suggestion'))
);

-- Popular content - trending and popular regulations
CREATE TABLE popular_content (
    id SERIAL PRIMARY KEY,
    regulation_id BIGINT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    
    -- Popularity metrics
    popularity_score DECIMAL(8,4), -- Computed popularity score
    trending_score DECIMAL(8,4), -- Short-term trending score
    
    -- Rankings
    overall_rank INTEGER,
    category_rank INTEGER, -- Rank within policy area/theme
    
    -- Time-based metrics
    last_7_days_views INTEGER DEFAULT 0,
    last_30_days_views INTEGER DEFAULT 0,
    last_90_days_views INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    
    -- Engagement metrics
    avg_time_spent INTERVAL,
    download_rate DECIMAL(5,2), -- Downloads per view
    share_count INTEGER DEFAULT 0,
    
    -- Computed at
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(regulation_id)
);

-- ============================================================================
-- PERFORMANCE MONITORING TABLES
-- ============================================================================

-- System performance metrics
CREATE TABLE system_performance_metrics (
    id BIGSERIAL PRIMARY KEY,
    
    -- Timestamp
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metric_type VARCHAR(50) NOT NULL, -- 'database', 'api', 'search', 'conversion'
    
    -- Performance metrics
    avg_response_time_ms DECIMAL(8,2),
    p95_response_time_ms DECIMAL(8,2),
    p99_response_time_ms DECIMAL(8,2),
    throughput_per_second DECIMAL(10,2),
    error_rate DECIMAL(5,2),
    
    -- Resource utilization
    cpu_usage_percent DECIMAL(5,2),
    memory_usage_percent DECIMAL(5,2),
    disk_usage_percent DECIMAL(5,2),
    network_io_mbps DECIMAL(10,2),
    
    -- Database specific
    active_connections INTEGER,
    slow_queries_count INTEGER,
    deadlocks_count INTEGER DEFAULT 0,
    
    -- Additional context
    metadata JSONB,
    
    CONSTRAINT chk_metric_type CHECK (metric_type IN ('database', 'api', 'search', 'conversion', 'overall'))
);

-- Data quality metrics over time
CREATE TABLE data_quality_metrics (
    id BIGSERIAL PRIMARY KEY,
    
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Completeness metrics
    total_regulations INTEGER,
    regulations_with_content INTEGER,
    regulations_with_metadata INTEGER,
    regulations_fully_converted INTEGER,
    
    -- Quality scores
    avg_conversion_quality DECIMAL(3,2),
    avg_metadata_completeness DECIMAL(3,2),
    avg_content_accuracy DECIMAL(3,2),
    
    -- Issues tracking
    critical_issues INTEGER DEFAULT 0,
    major_issues INTEGER DEFAULT 0,
    minor_issues INTEGER DEFAULT 0,
    
    -- Conversion pipeline health
    pending_conversions INTEGER,
    failed_conversions INTEGER,
    conversion_success_rate DECIMAL(5,2),
    avg_conversion_time INTERVAL,
    
    -- Data freshness
    regulations_updated_last_24h INTEGER,
    regulations_updated_last_7d INTEGER,
    oldest_unprocessed_regulation_days INTEGER
);

-- ============================================================================
-- ANALYTICS INDEXES
-- ============================================================================

-- Conversion tracking indexes
CREATE INDEX idx_conversion_jobs_regulation_id ON conversion_jobs(regulation_id);
CREATE INDEX idx_conversion_jobs_status ON conversion_jobs(status);
CREATE INDEX idx_conversion_jobs_priority ON conversion_jobs(priority, created_at) WHERE status = 'pending';
CREATE INDEX idx_conversion_jobs_timing ON conversion_jobs(started_at, completed_at) WHERE started_at IS NOT NULL;

CREATE INDEX idx_conversion_pipeline_stages_job ON conversion_pipeline_stages(job_id, stage_order);
CREATE INDEX idx_quality_assessments_regulation ON quality_assessments(regulation_id, assessment_type);

-- Usage analytics indexes
CREATE INDEX idx_access_logs_regulation_time ON access_logs(regulation_id, accessed_at);
CREATE INDEX idx_access_logs_user_type ON access_logs(user_type, accessed_at);
CREATE INDEX idx_access_logs_access_type ON access_logs(access_type, accessed_at);
CREATE INDEX idx_access_logs_country ON access_logs(country_code, accessed_at) WHERE country_code IS NOT NULL;

CREATE INDEX idx_usage_statistics_period ON usage_statistics(period_type, period_start);
CREATE INDEX idx_usage_statistics_popularity ON usage_statistics(regulation_id, popularity_rank) WHERE popularity_rank IS NOT NULL;

CREATE INDEX idx_search_analytics_query ON search_analytics(normalized_query, searched_at);
CREATE INDEX idx_search_analytics_performance ON search_analytics(results_count, clicked_results, searched_at);

CREATE INDEX idx_popular_content_rank ON popular_content(overall_rank) WHERE overall_rank IS NOT NULL;
CREATE INDEX idx_popular_content_trending ON popular_content(trending_score DESC, computed_at);

-- Performance monitoring indexes
CREATE INDEX idx_system_performance_metrics_type_time ON system_performance_metrics(metric_type, measured_at);
CREATE INDEX idx_data_quality_metrics_time ON data_quality_metrics(measured_at);

-- ============================================================================
-- ANALYTICS FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Update conversion job timing
CREATE OR REPLACE FUNCTION update_conversion_job_timing()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate processing duration when job is completed
    IF NEW.status IN ('completed', 'failed', 'cancelled') AND OLD.status = 'processing' THEN
        NEW.completed_at = NOW();
        NEW.processing_duration = NEW.completed_at - NEW.started_at;
    END IF;
    
    -- Set started_at when job begins processing
    IF NEW.status = 'processing' AND OLD.status = 'pending' THEN
        NEW.started_at = NOW();
    END IF;
    
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_conversion_job_timing_trigger
    BEFORE UPDATE ON conversion_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_conversion_job_timing();

-- Function to calculate popularity scores
CREATE OR REPLACE FUNCTION update_popularity_scores()
RETURNS void AS $$
DECLARE
    reg_record RECORD;
    popularity DECIMAL(8,4);
    trending DECIMAL(8,4);
BEGIN
    FOR reg_record IN 
        SELECT r.id, 
               COALESCE(SUM(CASE WHEN al.accessed_at > NOW() - INTERVAL '7 days' THEN 1 ELSE 0 END), 0) as views_7d,
               COALESCE(SUM(CASE WHEN al.accessed_at > NOW() - INTERVAL '30 days' THEN 1 ELSE 0 END), 0) as views_30d,
               COALESCE(COUNT(al.id), 0) as total_views
        FROM regulations r
        LEFT JOIN access_logs al ON r.id = al.regulation_id
        WHERE r.status = 'active'
        GROUP BY r.id
    LOOP
        -- Simple popularity calculation (can be enhanced with more sophisticated algorithms)
        popularity := (reg_record.views_30d * 0.7) + (reg_record.total_views * 0.3);
        trending := reg_record.views_7d * 2.0; -- Higher weight for recent activity
        
        INSERT INTO popular_content (
            regulation_id, popularity_score, trending_score, 
            last_7_days_views, last_30_days_views, total_views
        ) VALUES (
            reg_record.id, popularity, trending,
            reg_record.views_7d, reg_record.views_30d, reg_record.total_views
        ) 
        ON CONFLICT (regulation_id) 
        DO UPDATE SET
            popularity_score = EXCLUDED.popularity_score,
            trending_score = EXCLUDED.trending_score,
            last_7_days_views = EXCLUDED.last_7_days_views,
            last_30_days_views = EXCLUDED.last_30_days_views,
            total_views = EXCLUDED.total_views,
            computed_at = NOW();
    END LOOP;
END;
$$ LANGUAGE plpgsql;