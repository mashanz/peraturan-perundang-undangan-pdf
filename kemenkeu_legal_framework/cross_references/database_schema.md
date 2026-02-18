# Cross-Reference Database Schema

## Core Tables

### 1. regulations
Primary registry of all regulations
```sql
CREATE TABLE regulations (
    id VARCHAR(50) PRIMARY KEY,           -- e.g., "PMK-123/PMK.03/2024"
    type ENUM('UU','PP','Perpres','PMK','PER','SE','KMK') NOT NULL,
    number VARCHAR(20) NOT NULL,          -- e.g., "123"
    year INTEGER NOT NULL,                -- e.g., 2024
    series VARCHAR(10),                   -- e.g., "PMK.03" for tax series
    title TEXT NOT NULL,
    subject_area VARCHAR(100),            -- Tax, Budget, Customs, etc.
    date_enacted DATE NOT NULL,
    date_effective DATE NOT NULL,
    status ENUM('active','revoked','amended','superseded') DEFAULT 'active',
    authority_level INTEGER NOT NULL,     -- 1=UU, 2=PP, 3=Perpres, 4=PMK, etc.
    issuing_authority VARCHAR(100),       -- Ministry/Agency name
    full_text_url TEXT,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 2. citations
Legal citations and references between regulations
```sql
CREATE TABLE citations (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    citing_regulation_id VARCHAR(50) NOT NULL,    -- The regulation making the reference
    cited_regulation_id VARCHAR(50) NOT NULL,     -- The regulation being referenced
    citation_type ENUM('mengingat','implementing','related','superseded','amended') NOT NULL,
    citation_context TEXT,                        -- Where/how it's cited
    section_reference VARCHAR(50),                -- Specific article/section cited
    citation_strength ENUM('mandatory','supporting','informational') DEFAULT 'supporting',
    verified BOOLEAN DEFAULT FALSE,               -- Has citation been validated
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (citing_regulation_id) REFERENCES regulations(id),
    FOREIGN KEY (cited_regulation_id) REFERENCES regulations(id),
    INDEX idx_citing (citing_regulation_id),
    INDEX idx_cited (cited_regulation_id),
    INDEX idx_type (citation_type)
);
```

### 3. amendments
Complete amendment history tracking
```sql
CREATE TABLE amendments (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    original_regulation_id VARCHAR(50) NOT NULL,
    amending_regulation_id VARCHAR(50) NOT NULL,
    amendment_type ENUM('partial','complete','revocation','supersession') NOT NULL,
    sections_affected TEXT,                       -- JSON array of affected sections
    amendment_date DATE NOT NULL,
    effective_date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (original_regulation_id) REFERENCES regulations(id),
    FOREIGN KEY (amending_regulation_id) REFERENCES regulations(id),
    INDEX idx_original (original_regulation_id),
    INDEX idx_amending (amending_regulation_id),
    INDEX idx_date (amendment_date)
);
```

### 4. implementation_systems
System integration and technical requirements
```sql
CREATE TABLE implementation_systems (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    regulation_id VARCHAR(50) NOT NULL,
    system_name VARCHAR(100) NOT NULL,           -- SPAN, SAKTI, SIAP, etc.
    system_type ENUM('core','supporting','reporting','compliance') NOT NULL,
    integration_level ENUM('required','optional','recommended') DEFAULT 'required',
    technical_requirements TEXT,                  -- JSON object with tech specs
    implementation_status ENUM('planned','in_progress','completed','deprecated') DEFAULT 'planned',
    go_live_date DATE,
    responsible_unit VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (regulation_id) REFERENCES regulations(id),
    INDEX idx_regulation (regulation_id),
    INDEX idx_system (system_name),
    INDEX idx_status (implementation_status)
);
```

### 5. international_alignments
International treaty and agreement compliance tracking
```sql
CREATE TABLE international_alignments (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    regulation_id VARCHAR(50) NOT NULL,
    agreement_name VARCHAR(200) NOT NULL,        -- Treaty/Agreement name
    agreement_type ENUM('multilateral','bilateral','regional','standard') NOT NULL,
    counterpart_country VARCHAR(100),            -- For bilateral agreements
    alignment_status ENUM('compliant','partial','non_compliant','under_review') NOT NULL,
    compliance_requirements TEXT,                -- What must be implemented
    deviation_justification TEXT,                -- If not fully compliant
    review_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (regulation_id) REFERENCES regulations(id),
    INDEX idx_regulation (regulation_id),
    INDEX idx_agreement (agreement_name),
    INDEX idx_status (alignment_status)
);
```

## Views and Query Patterns

### 1. Active Regulation Hierarchy
```sql
CREATE VIEW active_regulation_hierarchy AS
SELECT 
    r.id,
    r.type,
    r.title,
    r.authority_level,
    GROUP_CONCAT(c.cited_regulation_id) as legal_basis,
    r.date_effective
FROM regulations r
LEFT JOIN citations c ON r.id = c.citing_regulation_id 
    AND c.citation_type = 'mengingat'
WHERE r.status = 'active'
GROUP BY r.id
ORDER BY r.authority_level, r.date_effective DESC;
```

### 2. Amendment Chain View
```sql
CREATE VIEW amendment_chains AS
WITH RECURSIVE amendment_history AS (
    SELECT 
        original_regulation_id,
        amending_regulation_id,
        amendment_date,
        1 as level
    FROM amendments
    WHERE original_regulation_id NOT IN (
        SELECT DISTINCT amending_regulation_id FROM amendments
    )
    
    UNION ALL
    
    SELECT 
        ah.original_regulation_id,
        a.amending_regulation_id,
        a.amendment_date,
        ah.level + 1
    FROM amendment_history ah
    JOIN amendments a ON ah.amending_regulation_id = a.original_regulation_id
)
SELECT * FROM amendment_history;
```

### 3. Implementation Readiness
```sql
CREATE VIEW implementation_readiness AS
SELECT 
    r.id,
    r.title,
    COUNT(CASE WHEN i.implementation_status = 'completed' THEN 1 END) as completed_systems,
    COUNT(i.id) as total_systems,
    ROUND(100.0 * COUNT(CASE WHEN i.implementation_status = 'completed' THEN 1 END) / COUNT(i.id), 2) as readiness_percentage
FROM regulations r
LEFT JOIN implementation_systems i ON r.id = i.regulation_id
WHERE r.status = 'active'
GROUP BY r.id, r.title
HAVING total_systems > 0
ORDER BY readiness_percentage ASC;
```

## Data Quality Controls

### 1. Citation Validation Rules
- All PMK must cite at least one UU in "MENGINGAT"
- Citation hierarchy must be consistent (PMK cannot cite another PMK as primary authority)
- Circular references are not allowed
- Revoked regulations cannot be cited as active authority

### 2. Amendment Integrity Checks
- Amendment dates must be after original regulation date
- Cannot amend revoked regulations
- Amendment chains must be complete
- Status updates must be consistent across related regulations

### 3. System Integration Validation
- Required systems must have implementation plans
- Go-live dates must be realistic and coordinated
- Dependencies between systems must be mapped
- Responsible units must be valid organizational entities