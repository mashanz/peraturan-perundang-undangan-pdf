-- KEMENKEU Regulation Database - Core Tables
-- Master Database Schema for 50,000+ regulations
-- Optimized for PostgreSQL 15+ with performance indexes

-- ============================================================================
-- CORE REGULATION TABLES
-- ============================================================================

-- Main regulations table - the heart of the system
CREATE TABLE regulations (
    id BIGSERIAL PRIMARY KEY,
    regulation_number VARCHAR(100) NOT NULL UNIQUE,
    title TEXT NOT NULL,
    title_en TEXT, -- English translation for international accessibility
    regulation_type VARCHAR(50) NOT NULL, -- PMK, SE, PER, etc.
    issuing_directorate VARCHAR(100) NOT NULL,
    issue_date DATE NOT NULL,
    effective_date DATE,
    expiry_date DATE,
    status VARCHAR(30) NOT NULL DEFAULT 'active', -- active, superseded, revoked, draft
    classification_level VARCHAR(20) DEFAULT 'public', -- public, restricted, confidential
    language VARCHAR(10) DEFAULT 'id', -- id, en, both
    
    -- Content metadata
    page_count INTEGER,
    article_count INTEGER,
    complexity_score DECIMAL(3,2), -- 0.00-10.00 scale
    readability_score DECIMAL(5,2), -- Flesch-Kincaid equivalent for Indonesian
    
    -- International alignment
    international_standard_alignment JSONB, -- References to international standards
    
    -- Document management
    source_file_path TEXT,
    source_file_hash VARCHAR(64), -- SHA-256 for integrity
    pdf_url TEXT,
    conversion_status VARCHAR(30) DEFAULT 'pending', -- pending, processing, completed, error
    conversion_quality_score DECIMAL(3,2), -- Quality assessment of conversion
    
    -- Timestamps and versioning
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    
    -- Full text search
    search_vector tsvector,
    
    CONSTRAINT chk_status CHECK (status IN ('active', 'superseded', 'revoked', 'draft')),
    CONSTRAINT chk_classification CHECK (classification_level IN ('public', 'restricted', 'confidential')),
    CONSTRAINT chk_conversion_status CHECK (conversion_status IN ('pending', 'processing', 'completed', 'error')),
    CONSTRAINT chk_complexity_score CHECK (complexity_score >= 0 AND complexity_score <= 10),
    CONSTRAINT chk_quality_score CHECK (conversion_quality_score >= 0 AND conversion_quality_score <= 10)
);

-- Regulation content - structured content storage
CREATE TABLE regulation_content (
    id BIGSERIAL PRIMARY KEY,
    regulation_id BIGINT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    content_type VARCHAR(20) NOT NULL, -- article, chapter, section, appendix
    sequence_number INTEGER NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    content_en TEXT, -- English translation
    parent_content_id BIGINT REFERENCES regulation_content(id),
    
    -- Structure metadata
    depth_level INTEGER NOT NULL DEFAULT 1,
    is_numbered BOOLEAN DEFAULT TRUE,
    
    -- Content analysis
    word_count INTEGER,
    has_tables BOOLEAN DEFAULT FALSE,
    has_formulas BOOLEAN DEFAULT FALSE,
    has_references BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(regulation_id, sequence_number)
);

-- Regulation relationships - amendments, references, hierarchies
CREATE TABLE regulation_relationships (
    id BIGSERIAL PRIMARY KEY,
    source_regulation_id BIGINT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    target_regulation_id BIGINT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    relationship_type VARCHAR(30) NOT NULL, -- amends, supersedes, references, implements, cites
    relationship_description TEXT,
    article_reference VARCHAR(100), -- Specific article/section reference
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_relationship_type CHECK (relationship_type IN ('amends', 'supersedes', 'references', 'implements', 'cites', 'relates_to')),
    CONSTRAINT chk_no_self_reference CHECK (source_regulation_id != target_regulation_id),
    UNIQUE(source_regulation_id, target_regulation_id, relationship_type)
);

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- Primary lookup indexes
CREATE INDEX idx_regulations_number ON regulations(regulation_number);
CREATE INDEX idx_regulations_type_date ON regulations(regulation_type, issue_date DESC);
CREATE INDEX idx_regulations_directorate ON regulations(issuing_directorate);
CREATE INDEX idx_regulations_status ON regulations(status) WHERE status = 'active';
CREATE INDEX idx_regulations_conversion_status ON regulations(conversion_status);

-- Search and filtering indexes
CREATE INDEX idx_regulations_full_text ON regulations USING GIN(search_vector);
CREATE INDEX idx_regulations_date_range ON regulations(effective_date, expiry_date) WHERE status = 'active';
CREATE INDEX idx_regulations_complexity ON regulations(complexity_score) WHERE complexity_score IS NOT NULL;

-- Content indexes
CREATE INDEX idx_regulation_content_regulation_id ON regulation_content(regulation_id);
CREATE INDEX idx_regulation_content_type ON regulation_content(content_type);
CREATE INDEX idx_regulation_content_parent ON regulation_content(parent_content_id) WHERE parent_content_id IS NOT NULL;

-- Relationship indexes
CREATE INDEX idx_regulation_relationships_source ON regulation_relationships(source_regulation_id);
CREATE INDEX idx_regulation_relationships_target ON regulation_relationships(target_regulation_id);
CREATE INDEX idx_regulation_relationships_type ON regulation_relationships(relationship_type);

-- Composite indexes for common queries
CREATE INDEX idx_regulations_active_by_directorate ON regulations(issuing_directorate, issue_date DESC) WHERE status = 'active';
CREATE INDEX idx_regulations_conversion_ready ON regulations(conversion_status, conversion_quality_score DESC) WHERE conversion_status = 'completed';

-- ============================================================================
-- TRIGGERS AND FUNCTIONS
-- ============================================================================

-- Auto-update timestamps
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_regulations_timestamp
    BEFORE UPDATE ON regulations
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_regulation_content_timestamp
    BEFORE UPDATE ON regulation_content
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Auto-update search vector
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('indonesian', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('indonesian', COALESCE(NEW.title_en, '')), 'A') ||
        setweight(to_tsvector('indonesian', COALESCE(NEW.regulation_number, '')), 'B') ||
        setweight(to_tsvector('indonesian', COALESCE(NEW.issuing_directorate, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_regulations_search_vector
    BEFORE INSERT OR UPDATE OF title, title_en, regulation_number, issuing_directorate ON regulations
    FOR EACH ROW
    EXECUTE FUNCTION update_search_vector();

-- ============================================================================
-- INITIAL DATA SETUP
-- ============================================================================

-- Create initial directorate lookup
INSERT INTO regulations (regulation_number, title, regulation_type, issuing_directorate, issue_date, status) VALUES
('SYSTEM-INIT-001', 'Database System Initialization', 'SYSTEM', 'Database Administration', CURRENT_DATE, 'active')
ON CONFLICT (regulation_number) DO NOTHING;