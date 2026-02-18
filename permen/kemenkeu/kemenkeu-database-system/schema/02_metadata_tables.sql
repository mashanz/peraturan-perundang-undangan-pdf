-- KEMENKEU Regulation Database - Metadata Tables
-- Standardized metadata schemas and tagging systems
-- AI-powered classification and semantic organization

-- ============================================================================
-- METADATA TAXONOMY TABLES
-- ============================================================================

-- Policy areas - hierarchical classification of policy domains
CREATE TABLE policy_areas (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    description TEXT,
    parent_id INTEGER REFERENCES policy_areas(id),
    level INTEGER NOT NULL DEFAULT 1, -- 1=main category, 2=subcategory, etc.
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_level CHECK (level >= 1 AND level <= 5)
);

-- Themes - cross-cutting themes that span multiple policy areas
CREATE TABLE themes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    description TEXT,
    color_code VARCHAR(7), -- Hex color for UI display
    icon VARCHAR(50), -- Icon identifier for UI
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tags - flexible tagging system for detailed classification
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    name_en VARCHAR(100),
    category VARCHAR(50), -- technical, subject, audience, etc.
    description TEXT,
    usage_count INTEGER DEFAULT 0,
    is_system_generated BOOLEAN DEFAULT FALSE, -- AI-generated vs manual
    confidence_score DECIMAL(3,2), -- AI confidence for generated tags
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_confidence CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1))
);

-- Keywords - extracted and curated keywords for search optimization
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(200) NOT NULL,
    normalized_form VARCHAR(200) NOT NULL, -- Stemmed/normalized version
    language VARCHAR(10) NOT NULL DEFAULT 'id',
    frequency INTEGER DEFAULT 1,
    importance_score DECIMAL(5,4), -- TF-IDF or similar scoring
    is_stopword BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(normalized_form, language)
);

-- ============================================================================
-- REGULATION METADATA MAPPING TABLES
-- ============================================================================

-- Regulation to policy area mappings
CREATE TABLE regulation_policy_areas (
    regulation_id BIGINT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    policy_area_id INTEGER NOT NULL REFERENCES policy_areas(id),
    confidence_score DECIMAL(3,2), -- AI classification confidence
    is_primary BOOLEAN DEFAULT FALSE, -- Primary vs secondary classification
    assigned_by VARCHAR(50), -- 'ai_classifier', 'manual', 'expert_review'
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (regulation_id, policy_area_id),
    CONSTRAINT chk_confidence CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1))
);

-- Regulation to theme mappings
CREATE TABLE regulation_themes (
    regulation_id BIGINT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    theme_id INTEGER NOT NULL REFERENCES themes(id),
    relevance_score DECIMAL(3,2), -- How relevant this theme is to the regulation
    assigned_by VARCHAR(50),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (regulation_id, theme_id),
    CONSTRAINT chk_relevance CHECK (relevance_score IS NULL OR (relevance_score >= 0 AND relevance_score <= 1))
);

-- Regulation to tag mappings
CREATE TABLE regulation_tags (
    regulation_id BIGINT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id),
    confidence_score DECIMAL(3,2),
    assigned_by VARCHAR(50),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (regulation_id, tag_id)
);

-- Regulation keywords - extracted and weighted keywords per regulation
CREATE TABLE regulation_keywords (
    regulation_id BIGINT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    keyword_id INTEGER NOT NULL REFERENCES keywords(id),
    frequency INTEGER NOT NULL DEFAULT 1,
    tf_idf_score DECIMAL(8,6), -- Term frequency-inverse document frequency
    position_weight DECIMAL(3,2), -- Higher weight for title, headings, etc.
    extraction_method VARCHAR(50), -- 'ai_extraction', 'manual', 'nlp_pipeline'
    
    PRIMARY KEY (regulation_id, keyword_id)
);

-- ============================================================================
-- CLASSIFICATION RULES AND PATTERNS
-- ============================================================================

-- Classification rules - patterns for automatic classification
CREATE TABLE classification_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(200) NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- 'keyword_pattern', 'title_pattern', 'content_pattern', 'ml_model'
    pattern TEXT NOT NULL, -- Regex pattern, keyword list, or model config
    target_type VARCHAR(50) NOT NULL, -- 'policy_area', 'theme', 'tag'
    target_id INTEGER NOT NULL,
    confidence_threshold DECIMAL(3,2) DEFAULT 0.8,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100),
    
    CONSTRAINT chk_rule_type CHECK (rule_type IN ('keyword_pattern', 'title_pattern', 'content_pattern', 'ml_model', 'composite')),
    CONSTRAINT chk_target_type CHECK (target_type IN ('policy_area', 'theme', 'tag'))
);

-- Similarity clusters - groups of similar regulations
CREATE TABLE similarity_clusters (
    id SERIAL PRIMARY KEY,
    cluster_name VARCHAR(200),
    description TEXT,
    similarity_threshold DECIMAL(3,2) DEFAULT 0.8,
    cluster_method VARCHAR(50), -- 'content_similarity', 'keyword_overlap', 'ml_clustering'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Regulation cluster memberships
CREATE TABLE regulation_clusters (
    regulation_id BIGINT NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
    cluster_id INTEGER NOT NULL REFERENCES similarity_clusters(id),
    similarity_score DECIMAL(5,4),
    distance_measure VARCHAR(50), -- 'cosine', 'jaccard', 'euclidean'
    
    PRIMARY KEY (regulation_id, cluster_id)
);

-- ============================================================================
-- INDEXES FOR METADATA TABLES
-- ============================================================================

-- Policy areas indexes
CREATE INDEX idx_policy_areas_parent ON policy_areas(parent_id) WHERE parent_id IS NOT NULL;
CREATE INDEX idx_policy_areas_level ON policy_areas(level);
CREATE INDEX idx_policy_areas_active ON policy_areas(is_active) WHERE is_active = TRUE;

-- Tags and keywords indexes
CREATE INDEX idx_tags_category ON tags(category);
CREATE INDEX idx_tags_usage ON tags(usage_count DESC);
CREATE INDEX idx_tags_system_generated ON tags(is_system_generated);
CREATE INDEX idx_keywords_language ON keywords(language);
CREATE INDEX idx_keywords_frequency ON keywords(frequency DESC);
CREATE INDEX idx_keywords_importance ON keywords(importance_score DESC) WHERE importance_score IS NOT NULL;

-- Mapping table indexes
CREATE INDEX idx_regulation_policy_areas_primary ON regulation_policy_areas(regulation_id, is_primary);
CREATE INDEX idx_regulation_themes_relevance ON regulation_themes(theme_id, relevance_score DESC);
CREATE INDEX idx_regulation_tags_confidence ON regulation_tags(tag_id, confidence_score DESC);
CREATE INDEX idx_regulation_keywords_tfidf ON regulation_keywords(regulation_id, tf_idf_score DESC);

-- Classification and clustering indexes
CREATE INDEX idx_classification_rules_type ON classification_rules(rule_type, is_active);
CREATE INDEX idx_classification_rules_target ON classification_rules(target_type, target_id);
CREATE INDEX idx_similarity_clusters_method ON similarity_clusters(cluster_method, is_active);
CREATE INDEX idx_regulation_clusters_similarity ON regulation_clusters(cluster_id, similarity_score DESC);

-- ============================================================================
-- INITIAL METADATA SETUP
-- ============================================================================

-- Core policy areas for Ministry of Finance
INSERT INTO policy_areas (code, name, name_en, description, level) VALUES
-- Level 1: Main Categories
('TAX', 'Perpajakan', 'Taxation', 'Regulations related to tax policy, collection, and administration', 1),
('BUDGET', 'Anggaran', 'Budget', 'Government budget planning, execution, and monitoring', 1),
('DEBT', 'Utang', 'Debt Management', 'Government debt policy and management', 1),
('CUSTOMS', 'Kepabeanan', 'Customs', 'Customs procedures, tariffs, and trade facilitation', 1),
('FINANCE', 'Keuangan', 'Financial Management', 'Government financial management and administration', 1),
('PROCUREMENT', 'Pengadaan', 'Procurement', 'Government procurement policies and procedures', 1),
('ACCOUNTING', 'Akuntansi', 'Accounting', 'Government accounting standards and practices', 1),
('AUDIT', 'Audit', 'Audit', 'Internal audit and financial oversight', 1);

-- Level 2: Subcategories for Taxation
INSERT INTO policy_areas (code, name, name_en, description, parent_id, level) VALUES
('TAX_INCOME', 'Pajak Penghasilan', 'Income Tax', 'Personal and corporate income tax regulations', 1, 2),
('TAX_VAT', 'Pajak Pertambahan Nilai', 'Value Added Tax', 'VAT regulations and procedures', 1, 2),
('TAX_PROPERTY', 'Pajak Bumi dan Bangunan', 'Property Tax', 'Property tax assessment and collection', 1, 2),
('TAX_LUXURY', 'Pajak Penjualan Barang Mewah', 'Luxury Goods Tax', 'Tax on luxury goods and services', 1, 2);

-- Core themes
INSERT INTO themes (code, name, name_en, description, color_code, icon) VALUES
('TRANSPARENCY', 'Transparansi', 'Transparency', 'Regulations promoting government transparency and openness', '#2196F3', 'visibility'),
('EFFICIENCY', 'Efisiensi', 'Efficiency', 'Measures to improve government efficiency and reduce bureaucracy', '#4CAF50', 'speed'),
('COMPLIANCE', 'Kepatuhan', 'Compliance', 'Compliance requirements and enforcement measures', '#FF9800', 'rule'),
('DIGITALIZATION', 'Digitalisasi', 'Digitalization', 'Digital transformation and e-government initiatives', '#9C27B0', 'computer'),
('INTERNATIONAL', 'Internasional', 'International', 'International cooperation and standards alignment', '#607D8B', 'public'),
('MSME', 'UMKM', 'Micro, Small & Medium Enterprises', 'Special provisions for MSMEs', '#795548', 'business'),
('COVID19', 'COVID-19', 'COVID-19', 'Pandemic-related financial measures', '#F44336', 'health_and_safety');

-- Initial tag categories
INSERT INTO tags (name, name_en, category, description) VALUES
('urgent', 'Urgent', 'priority', 'Regulations requiring immediate attention'),
('routine', 'Routine', 'priority', 'Standard operational regulations'),
('technical', 'Technical', 'complexity', 'Highly technical regulations requiring expertise'),
('general', 'General', 'complexity', 'Regulations for general public understanding'),
('taxpayer', 'Taxpayer', 'audience', 'Regulations primarily affecting taxpayers'),
('government_agency', 'Government Agency', 'audience', 'Internal government procedures'),
('business', 'Business', 'audience', 'Regulations affecting businesses and corporations'),
('public', 'Public', 'audience', 'Regulations affecting general public');

-- ============================================================================
-- METADATA UTILITY FUNCTIONS
-- ============================================================================

-- Function to calculate tag usage
CREATE OR REPLACE FUNCTION update_tag_usage_counts()
RETURNS void AS $$
BEGIN
    UPDATE tags SET usage_count = (
        SELECT COUNT(*) FROM regulation_tags WHERE tag_id = tags.id
    );
END;
$$ LANGUAGE plpgsql;

-- Function to find similar regulations based on keywords
CREATE OR REPLACE FUNCTION find_similar_regulations(target_regulation_id BIGINT, threshold DECIMAL DEFAULT 0.7)
RETURNS TABLE(regulation_id BIGINT, similarity_score DECIMAL) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rk2.regulation_id,
        (COUNT(*) * 1.0 / (
            SELECT COUNT(DISTINCT keyword_id) 
            FROM regulation_keywords 
            WHERE regulation_id IN (target_regulation_id, rk2.regulation_id)
        ))::DECIMAL(5,4) as similarity_score
    FROM regulation_keywords rk1
    JOIN regulation_keywords rk2 ON rk1.keyword_id = rk2.keyword_id
    WHERE rk1.regulation_id = target_regulation_id 
    AND rk2.regulation_id != target_regulation_id
    GROUP BY rk2.regulation_id
    HAVING (COUNT(*) * 1.0 / (
        SELECT COUNT(DISTINCT keyword_id) 
        FROM regulation_keywords 
        WHERE regulation_id IN (target_regulation_id, rk2.regulation_id)
    ))::DECIMAL(5,4) >= threshold
    ORDER BY similarity_score DESC;
END;
$$ LANGUAGE plpgsql;