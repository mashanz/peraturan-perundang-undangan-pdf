-- KEMENKEU LEGAL HIERARCHY DATABASE - OPERATIONAL SYSTEM
-- Execute immediately for functional legal framework mapping

-- Drop existing tables if they exist
DROP TABLE IF EXISTS implementation_systems CASCADE;
DROP TABLE IF EXISTS international_alignments CASCADE;
DROP TABLE IF EXISTS amendments CASCADE;
DROP TABLE IF EXISTS citations CASCADE;
DROP TABLE IF EXISTS regulations CASCADE;

-- 1. CORE REGULATIONS TABLE
CREATE TABLE regulations (
    id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(10) NOT NULL,
    number VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL,
    series VARCHAR(20),
    title TEXT NOT NULL,
    subject_area VARCHAR(100),
    date_enacted DATE NOT NULL,
    date_effective DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    authority_level INTEGER NOT NULL,
    issuing_authority VARCHAR(100),
    full_text_url TEXT,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. CITATIONS TABLE - LEGAL CROSS-REFERENCES
CREATE TABLE citations (
    id SERIAL PRIMARY KEY,
    citing_regulation_id VARCHAR(50) NOT NULL,
    cited_regulation_id VARCHAR(50) NOT NULL,
    citation_type VARCHAR(20) NOT NULL,
    citation_context TEXT,
    section_reference VARCHAR(50),
    citation_strength VARCHAR(20) DEFAULT 'supporting',
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (citing_regulation_id) REFERENCES regulations(id),
    FOREIGN KEY (cited_regulation_id) REFERENCES regulations(id)
);

-- 3. AMENDMENTS TRACKING TABLE
CREATE TABLE amendments (
    id SERIAL PRIMARY KEY,
    original_regulation_id VARCHAR(50) NOT NULL,
    amending_regulation_id VARCHAR(50) NOT NULL,
    amendment_type VARCHAR(20) NOT NULL,
    sections_affected TEXT,
    amendment_date DATE NOT NULL,
    effective_date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (original_regulation_id) REFERENCES regulations(id),
    FOREIGN KEY (amending_regulation_id) REFERENCES regulations(id)
);

-- 4. SYSTEM IMPLEMENTATION TABLE
CREATE TABLE implementation_systems (
    id SERIAL PRIMARY KEY,
    regulation_id VARCHAR(50) NOT NULL,
    system_name VARCHAR(100) NOT NULL,
    system_type VARCHAR(20) NOT NULL,
    integration_level VARCHAR(20) DEFAULT 'required',
    implementation_status VARCHAR(20) DEFAULT 'planned',
    go_live_date DATE,
    responsible_unit VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (regulation_id) REFERENCES regulations(id)
);

-- 5. INTERNATIONAL COMPLIANCE TABLE
CREATE TABLE international_alignments (
    id SERIAL PRIMARY KEY,
    regulation_id VARCHAR(50) NOT NULL,
    agreement_name VARCHAR(200) NOT NULL,
    agreement_type VARCHAR(20) NOT NULL,
    alignment_status VARCHAR(20) NOT NULL,
    compliance_requirements TEXT,
    review_date DATE,
    
    FOREIGN KEY (regulation_id) REFERENCES regulations(id)
);

-- CORE DATA INSERT - CRITICAL PMK REGULATIONS
INSERT INTO regulations VALUES 
('PMK-68/PMK.03/2022', 'PMK', '68', 2022, 'PMK.03', 'Faktur Pajak Elektronik', 'Tax Administration', '2022-08-15', '2022-10-01', 'active', 4, 'Menteri Keuangan', 'https://peraturan.go.id/pmk-68-2022', 'Electronic tax invoice implementation', NOW()),
('PMK-142/PMK.03/2023', 'PMK', '142', 2023, 'PMK.03', 'Perubahan PMK-68/2022 Faktur Pajak Elektronik', 'Tax Administration', '2023-07-20', '2023-10-01', 'active', 4, 'Menteri Keuangan', 'https://peraturan.go.id/pmk-142-2023', 'Amendment to e-invoice regulation', NOW()),
('PMK-01/PMK.01/2024', 'PMK', '01', 2024, 'PMK.01', 'Pelaksanaan APBN Tahun Anggaran 2024', 'Budget Management', '2024-01-02', '2024-01-01', 'active', 4, 'Menteri Keuangan', 'https://peraturan.go.id/pmk-01-2024', '2024 State Budget implementation', NOW()),
('PMK-187/PMK.05/2023', 'PMK', '187', 2023, 'PMK.05', 'Standar Akuntansi Pemerintahan', 'Government Accounting', '2023-12-01', '2024-01-01', 'active', 4, 'Menteri Keuangan', 'https://peraturan.go.id/pmk-187-2023', 'Government accounting standards', NOW()),
('PMK-75/PMK.04/2023', 'PMK', '75', 2023, 'PMK.04', 'Tata Cara Pemeriksaan Pabean', 'Customs', '2023-06-15', '2023-07-01', 'active', 4, 'Menteri Keuangan', 'https://peraturan.go.id/pmk-75-2023', 'Customs inspection procedures', NOW()),
('UU-6/1983', 'UU', '6', 1983, NULL, 'Ketentuan Umum dan Tata Cara Perpajakan', 'Tax Law', '1983-12-31', '1984-01-01', 'active', 1, 'DPR RI', 'https://peraturan.go.id/uu-6-1983', 'General tax provisions and procedures', NOW()),
('UU-8/1983', 'UU', '8', 1983, NULL, 'Pajak Pertambahan Nilai Barang dan Jasa', 'Tax Law', '1983-12-31', '1984-01-01', 'active', 1, 'DPR RI', 'https://peraturan.go.id/uu-8-1983', 'Value Added Tax law', NOW()),
('PP-74/2011', 'PP', '74', 2011, NULL, 'Tata Cara Pelaksanaan Hak dan Kewajiban Perpajakan', 'Tax Implementation', '2011-12-20', '2012-01-01', 'active', 2, 'Presiden RI', 'https://peraturan.go.id/pp-74-2011', 'Tax rights and obligations procedures', NOW());

-- LEGAL CITATIONS - AUTHORITY CHAIN MAPPING
INSERT INTO citations VALUES 
(DEFAULT, 'PMK-68/PMK.03/2022', 'UU-6/1983', 'mengingat', 'Primary tax law authority', 'Pasal 13, 14', 'mandatory', true, NOW()),
(DEFAULT, 'PMK-68/PMK.03/2022', 'UU-8/1983', 'mengingat', 'VAT law authority', 'Pasal 13, 16', 'mandatory', true, NOW()),
(DEFAULT, 'PMK-68/PMK.03/2022', 'PP-74/2011', 'mengingat', 'Implementation procedures', 'Pasal 10, 11', 'supporting', true, NOW()),
(DEFAULT, 'PMK-142/PMK.03/2023', 'PMK-68/PMK.03/2022', 'amending', 'Amendment to original regulation', 'Pasal 8, 15', 'mandatory', true, NOW()),
(DEFAULT, 'PMK-01/PMK.01/2024', 'UU-6/1983', 'mengingat', 'Budget law authority', 'Pasal 1', 'mandatory', true, NOW());

-- AMENDMENT TRACKING
INSERT INTO amendments VALUES 
(DEFAULT, 'PMK-68/PMK.03/2022', 'PMK-142/PMK.03/2023', 'partial', 'Pasal 8, Pasal 15, Lampiran II', '2023-07-20', '2023-10-01', 'Extended implementation timeline and updated technical specifications', NOW());

-- SYSTEM IMPLEMENTATIONS
INSERT INTO implementation_systems VALUES 
(DEFAULT, 'PMK-68/PMK.03/2022', 'SPAN', 'core', 'required', 'completed', '2022-10-01', 'DJP', NOW()),
(DEFAULT, 'PMK-68/PMK.03/2022', 'SIAP', 'supporting', 'required', 'completed', '2022-10-01', 'DJP', NOW()),
(DEFAULT, 'PMK-01/PMK.01/2024', 'SAKTI', 'core', 'required', 'completed', '2024-01-01', 'Setjen', NOW()),
(DEFAULT, 'PMK-75/PMK.04/2023', 'SPAN', 'core', 'required', 'in_progress', '2023-09-01', 'DJBC', NOW());

-- INTERNATIONAL ALIGNMENTS
INSERT INTO international_alignments VALUES 
(DEFAULT, 'PMK-68/PMK.03/2022', 'WTO Agreement on Technical Barriers to Trade', 'multilateral', 'compliant', 'Electronic documentation standards', '2024-06-01'),
(DEFAULT, 'PMK-75/PMK.04/2023', 'WTO Agreement on Trade Facilitation', 'multilateral', 'compliant', 'Customs procedures modernization', '2024-03-01'),
(DEFAULT, 'PMK-187/PMK.05/2023', 'OECD Government Accounting Standards', 'standard', 'substantially_compliant', 'International accounting alignment', '2024-12-01');

-- CREATE INDEXES FOR PERFORMANCE
CREATE INDEX idx_regulations_type_year ON regulations(type, year);
CREATE INDEX idx_regulations_status ON regulations(status);
CREATE INDEX idx_citations_citing ON citations(citing_regulation_id);
CREATE INDEX idx_citations_cited ON citations(cited_regulation_id);
CREATE INDEX idx_amendments_original ON amendments(original_regulation_id);
CREATE INDEX idx_implementation_regulation ON implementation_systems(regulation_id);
CREATE INDEX idx_international_regulation ON international_alignments(regulation_id);

-- OPERATIONAL VIEWS FOR QUICK ACCESS
CREATE VIEW active_pmk_hierarchy AS
SELECT 
    r.id,
    r.title,
    r.series,
    r.date_effective,
    STRING_AGG(DISTINCT cr.id, ', ') as cited_authorities,
    r.status
FROM regulations r
LEFT JOIN citations c ON r.id = c.citing_regulation_id AND c.citation_type = 'mengingat'
LEFT JOIN regulations cr ON c.cited_regulation_id = cr.id
WHERE r.status = 'active' AND r.type = 'PMK'
GROUP BY r.id, r.title, r.series, r.date_effective, r.status
ORDER BY r.date_effective DESC;

CREATE VIEW amendment_chains AS
WITH RECURSIVE amendment_history AS (
    SELECT original_regulation_id, amending_regulation_id, amendment_date, 1 as level
    FROM amendments
    UNION ALL
    SELECT ah.original_regulation_id, a.amending_regulation_id, a.amendment_date, ah.level + 1
    FROM amendment_history ah
    JOIN amendments a ON ah.amending_regulation_id = a.original_regulation_id
    WHERE ah.level < 10
)
SELECT ah.*, r1.title as original_title, r2.title as amending_title
FROM amendment_history ah
JOIN regulations r1 ON ah.original_regulation_id = r1.id
JOIN regulations r2 ON ah.amending_regulation_id = r2.id
ORDER BY ah.original_regulation_id, ah.level;

CREATE VIEW implementation_status AS
SELECT 
    r.id,
    r.title,
    COUNT(i.id) as total_systems,
    COUNT(CASE WHEN i.implementation_status = 'completed' THEN 1 END) as completed_systems,
    ROUND(100.0 * COUNT(CASE WHEN i.implementation_status = 'completed' THEN 1 END) / NULLIF(COUNT(i.id), 0), 1) as completion_percentage
FROM regulations r
LEFT JOIN implementation_systems i ON r.id = i.regulation_id
WHERE r.status = 'active' AND r.type = 'PMK'
GROUP BY r.id, r.title
ORDER BY completion_percentage DESC;