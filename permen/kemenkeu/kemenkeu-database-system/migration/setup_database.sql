-- KEMENKEU Database Setup - COMPLETE SYSTEM DEPLOYMENT
-- Execute this file to create production-ready database for 4,631+ regulations
-- Single-command setup for immediate deployment

-- ============================================================================
-- COMPLETE DATABASE INITIALIZATION
-- ============================================================================

-- Create database and extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Execute all schema files in order
\i schema/01_core_tables.sql
\i schema/02_metadata_tables.sql
\i schema/03_analytics_tables.sql

-- ============================================================================
-- PRODUCTION DATA SETUP
-- ============================================================================

-- Insert comprehensive policy area taxonomy
INSERT INTO policy_areas (code, name, name_en, description, level) VALUES
-- Level 1: Core Ministry Areas
('TAX', 'Perpajakan', 'Taxation', 'Tax policy, collection, and administration', 1),
('BUDGET', 'Anggaran', 'Budget Management', 'Government budget planning and execution', 1),
('DEBT', 'Pengelolaan Utang', 'Debt Management', 'Government debt policy and management', 1),
('CUSTOMS', 'Kepabeanan dan Cukai', 'Customs and Excise', 'Trade facilitation and border control', 1),
('TREASURY', 'Perbendaharaan', 'Treasury', 'Cash management and payment systems', 1),
('FINANCE', 'Keuangan Negara', 'State Finance', 'Public financial management', 1),
('PROCUREMENT', 'Pengadaan Barang/Jasa', 'Procurement', 'Government procurement policies', 1),
('ACCOUNTING', 'Akuntansi Pemerintah', 'Government Accounting', 'Public sector accounting standards', 1),

-- Level 2: Detailed Tax Categories
('TAX_INCOME', 'Pajak Penghasilan', 'Income Tax', 'Personal and corporate income tax', 2),
('TAX_VAT', 'Pajak Pertambahan Nilai', 'Value Added Tax', 'VAT and luxury goods tax', 2),
('TAX_PROPERTY', 'Pajak Bumi dan Bangunan', 'Property Tax', 'Land and building tax', 2),
('TAX_TRANSFER', 'Bea Perolehan Hak', 'Transfer Tax', 'Property transfer duties', 2),
('TAX_VEHICLE', 'Pajak Kendaraan Bermotor', 'Motor Vehicle Tax', 'Vehicle registration and annual tax', 2),
('TAX_INTERNATIONAL', 'Pajak Internasional', 'International Tax', 'Cross-border taxation and treaties', 2),

-- Level 2: Budget Categories  
('BUDGET_PLAN', 'Perencanaan Anggaran', 'Budget Planning', 'Annual budget preparation', 2),
('BUDGET_EXEC', 'Pelaksanaan Anggaran', 'Budget Execution', 'Budget implementation and monitoring', 2),
('BUDGET_CONTROL', 'Pengendalian Anggaran', 'Budget Control', 'Financial controls and oversight', 2),

-- Level 2: Customs Categories
('CUSTOMS_TARIFF', 'Tarif Bea Masuk', 'Import Tariffs', 'Import duty rates and classifications', 2),
('CUSTOMS_PROCEDURE', 'Prosedur Kepabeanan', 'Customs Procedures', 'Import/export procedures', 2),
('CUSTOMS_ENFORCEMENT', 'Penegakan Hukum', 'Customs Enforcement', 'Compliance and penalties', 2);

-- Update parent relationships
UPDATE policy_areas SET parent_id = 1 WHERE code IN ('TAX_INCOME', 'TAX_VAT', 'TAX_PROPERTY', 'TAX_TRANSFER', 'TAX_VEHICLE', 'TAX_INTERNATIONAL');
UPDATE policy_areas SET parent_id = 2 WHERE code IN ('BUDGET_PLAN', 'BUDGET_EXEC', 'BUDGET_CONTROL');
UPDATE policy_areas SET parent_id = 4 WHERE code IN ('CUSTOMS_TARIFF', 'CUSTOMS_PROCEDURE', 'CUSTOMS_ENFORCEMENT');

-- Core themes for regulation classification
INSERT INTO themes (code, name, name_en, description, color_code, icon) VALUES
('TRANSPARENCY', 'Transparansi', 'Transparency', 'Government transparency and accountability', '#2196F3', 'visibility'),
('EFFICIENCY', 'Efisiensi', 'Efficiency', 'Process improvement and cost reduction', '#4CAF50', 'speed'),
('COMPLIANCE', 'Kepatuhan', 'Compliance', 'Legal compliance and enforcement', '#FF9800', 'gavel'),
('DIGITALIZATION', 'Digitalisasi', 'Digital Transformation', 'E-government and digital services', '#9C27B0', 'computer'),
('INTERNATIONAL', 'Kerjasama Internasional', 'International Cooperation', 'Global standards and agreements', '#607D8B', 'public'),
('MSME', 'UMKM', 'Micro Small Medium Enterprises', 'Support for small businesses', '#795548', 'business'),
('PANDEMIC', 'Pandemi', 'Pandemic Response', 'COVID-19 and emergency measures', '#F44336', 'health_and_safety'),
('REFORM', 'Reformasi', 'Structural Reform', 'Policy and institutional reforms', '#FF5722', 'trending_up'),
('INVESTMENT', 'Investasi', 'Investment', 'Investment facilitation and incentives', '#009688', 'trending_up'),
('ENVIRONMENT', 'Lingkungan', 'Environmental', 'Green finance and sustainability', '#8BC34A', 'eco');

-- Essential tags for detailed classification
INSERT INTO tags (name, name_en, category, description) VALUES
-- Priority tags
('urgent', 'Urgent', 'priority', 'Requires immediate attention'),
('routine', 'Routine', 'priority', 'Standard operational regulation'),
('strategic', 'Strategic', 'priority', 'Strategic policy direction'),

-- Complexity tags
('technical', 'Technical', 'complexity', 'Highly technical content'),
('general', 'General', 'complexity', 'General public understanding'),
('expert', 'Expert', 'complexity', 'Requires professional expertise'),

-- Audience tags
('taxpayer', 'Taxpayer', 'audience', 'Individual and corporate taxpayers'),
('government', 'Government Agency', 'audience', 'Government internal procedures'),
('business', 'Business', 'audience', 'Business and commercial entities'),
('public', 'General Public', 'audience', 'General public services'),

-- Implementation tags
('immediate', 'Immediate Implementation', 'implementation', 'Effective immediately'),
('phased', 'Phased Implementation', 'implementation', 'Gradual implementation'),
('pilot', 'Pilot Program', 'implementation', 'Trial implementation');

-- ============================================================================
-- PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Analyze tables for optimal query planning
ANALYZE regulations;
ANALYZE regulation_content;
ANALYZE regulation_relationships;
ANALYZE regulation_policy_areas;
ANALYZE regulation_themes;
ANALYZE regulation_tags;

-- Create materialized views for common queries
CREATE MATERIALIZED VIEW mv_active_regulations AS
SELECT 
    r.*,
    COUNT(rc.id) as content_sections,
    COUNT(DISTINCT rpa.policy_area_id) as policy_area_count,
    COUNT(DISTINCT rt.theme_id) as theme_count,
    COUNT(DISTINCT rtag.tag_id) as tag_count
FROM regulations r
LEFT JOIN regulation_content rc ON r.id = rc.regulation_id
LEFT JOIN regulation_policy_areas rpa ON r.id = rpa.regulation_id
LEFT JOIN regulation_themes rt ON r.id = rt.regulation_id
LEFT JOIN regulation_tags rtag ON r.id = rtag.regulation_id
WHERE r.status = 'active'
GROUP BY r.id;

CREATE UNIQUE INDEX idx_mv_active_regulations_id ON mv_active_regulations(id);
CREATE INDEX idx_mv_active_regulations_type_date ON mv_active_regulations(regulation_type, issue_date DESC);

-- Popular regulations view
CREATE MATERIALIZED VIEW mv_popular_regulations AS
SELECT 
    r.id,
    r.regulation_number,
    r.title,
    r.regulation_type,
    r.issue_date,
    COALESCE(pc.popularity_score, 0) as popularity_score,
    COALESCE(pc.total_views, 0) as total_views,
    COALESCE(pc.last_30_days_views, 0) as recent_views
FROM regulations r
LEFT JOIN popular_content pc ON r.id = pc.regulation_id
WHERE r.status = 'active'
ORDER BY COALESCE(pc.popularity_score, 0) DESC;

-- ============================================================================
-- SEARCH OPTIMIZATION
-- ============================================================================

-- Create search configuration
CREATE TEXT SEARCH CONFIGURATION kemenkeu_search (COPY = indonesian);

-- Update search vectors for existing data
UPDATE regulations SET search_vector = 
    setweight(to_tsvector('kemenkeu_search', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('kemenkeu_search', COALESCE(title_en, '')), 'A') ||
    setweight(to_tsvector('kemenkeu_search', COALESCE(regulation_number, '')), 'B');

-- ============================================================================
-- SAMPLE DATA FOR TESTING
-- ============================================================================

-- Insert sample regulation for system testing
INSERT INTO regulations (
    regulation_number, title, title_en, regulation_type, issuing_directorate,
    issue_date, effective_date, status, page_count, article_count, complexity_score
) VALUES (
    'PMK-001/PMK.03/2024',
    'Peraturan Menteri Keuangan tentang Pajak Penghasilan Wajib Pajak Dalam Negeri',
    'Minister of Finance Regulation on Income Tax for Domestic Taxpayers',
    'PMK',
    'Direktorat Jenderal Pajak',
    '2024-01-15',
    '2024-02-01',
    'active',
    45,
    28,
    7.5
);

-- Link to policy areas and themes
INSERT INTO regulation_policy_areas (regulation_id, policy_area_id, is_primary, confidence_score, assigned_by)
SELECT 
    (SELECT id FROM regulations WHERE regulation_number = 'PMK-001/PMK.03/2024'),
    pa.id,
    CASE WHEN pa.code = 'TAX_INCOME' THEN true ELSE false END,
    0.95,
    'system_initialization'
FROM policy_areas pa 
WHERE pa.code IN ('TAX_INCOME', 'TAX');

-- System health check function
CREATE OR REPLACE FUNCTION system_health_check()
RETURNS TABLE(
    component TEXT,
    status TEXT,
    details TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'Database' as component,
        CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'ERROR' END as status,
        COUNT(*)::TEXT || ' regulations loaded' as details
    FROM regulations
    
    UNION ALL
    
    SELECT 
        'Metadata' as component,
        CASE WHEN COUNT(*) >= 10 THEN 'OK' ELSE 'WARNING' END as status,
        COUNT(*)::TEXT || ' policy areas configured' as details
    FROM policy_areas
    
    UNION ALL
    
    SELECT 
        'Search' as component,
        CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'ERROR' END as status,
        COUNT(*)::TEXT || ' regulations indexed for search' as details
    FROM regulations 
    WHERE search_vector IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FINAL SETUP COMMANDS
-- ============================================================================

-- Refresh materialized views
REFRESH MATERIALIZED VIEW mv_active_regulations;
REFRESH MATERIALIZED VIEW mv_popular_regulations;

-- Final system check
SELECT * FROM system_health_check();

-- Grant permissions for application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO kemenkeu_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO kemenkeu_app_user;

COMMIT;

-- Success message
\echo 'KEMENKEU Database System Setup Complete!'
\echo 'Ready for 4,631+ regulation records'
\echo 'All core components initialized and optimized'