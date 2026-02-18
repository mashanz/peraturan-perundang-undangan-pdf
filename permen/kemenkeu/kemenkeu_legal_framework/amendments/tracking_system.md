# Amendment Tracking System

## Overview
Comprehensive system for tracking all changes to KEMENKEU regulations, including amendments, revocations, and supersessions.

## Amendment Types

### 1. Partial Amendment (Sebagian)
- **Definition**: Changes to specific articles/sections while keeping regulation structure intact
- **Keywords**: "mengubah", "sebagian", "diubah"
- **Impact**: Original regulation remains active with modifications
- **Tracking**: Section-level change mapping required

### 2. Complete Amendment (Keseluruhan)
- **Definition**: Comprehensive rewrite of entire regulation
- **Keywords**: "mengubah keseluruhan", "diganti"
- **Impact**: Original regulation effectively replaced
- **Tracking**: Full content comparison and mapping

### 3. Revocation (Pencabutan)
- **Definition**: Complete elimination of regulation
- **Keywords**: "dicabut", "tidak berlaku lagi"
- **Impact**: Regulation becomes inactive, no longer enforceable
- **Tracking**: Termination date and replacement mapping

### 4. Supersession (Penggantian)
- **Definition**: Old regulation replaced by new regulation on same subject
- **Keywords**: "menggantikan", "sebagai pengganti"
- **Impact**: Seamless transition from old to new regulation
- **Tracking**: Continuity analysis between old and new provisions

## Amendment Detection Patterns

### Text Pattern Recognition
```regex
# Indonesian Amendment Indicators
AMENDMENT_PATTERNS = {
    'partial_amendment': [
        r'mengubah\s+(?:beberapa\s+)?(?:ketentuan\s+)?(?:dalam\s+)?(?:Peraturan\s+Menteri\s+Keuangan)',
        r'merubah\s+(?:sebagian\s+)?(?:ketentuan\s+)?(?:dalam\s+)?(?:PMK)',
        r'diubah\s+sebagai\s+berikut'
    ],
    'complete_amendment': [
        r'mengubah\s+(?:keseluruhan\s+)?(?:atas\s+)?(?:Peraturan\s+Menteri\s+Keuangan)',
        r'mengganti\s+(?:seluruhnya\s+)?(?:PMK)',
        r'diganti\s+(?:keseluruhan)?'
    ],
    'revocation': [
        r'mencabut\s+(?:dan\s+menyatakan\s+tidak\s+berlaku\s+)?(?:PMK|Peraturan\s+Menteri\s+Keuangan)',
        r'dicabut\s+(?:dan\s+dinyatakan\s+tidak\s+berlaku)',
        r'tidak\s+berlaku\s+lagi'
    ],
    'supersession': [
        r'menggantikan\s+(?:PMK|Peraturan\s+Menteri\s+Keuangan)',
        r'sebagai\s+pengganti\s+(?:PMK)',
        r'mengganti\s+(?:PMK)'
    ]
}
```

### Legal Citation Extraction
```python
def extract_amended_regulation_id(text):
    """Extract regulation ID being amended from legal text"""
    patterns = [
        r'PMK[-.\s]?(\d+)[-/]PMK\.(\d+)[-/](\d{4})',
        r'Peraturan\s+Menteri\s+Keuangan\s+Nomor\s+(\d+)[-/]PMK\.(\d+)[-/](\d{4})',
        r'Nomor\s+(\d+)\s+Tahun\s+(\d{4})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return construct_regulation_id(match.groups())
    
    return None
```

## Amendment Chain Tracking

### Chain Structure
```yaml
amendment_chain:
  root_regulation: "PMK-100/PMK.03/2020"
  chain_events:
    - event_id: 1
      date: "2021-06-15"
      type: "partial_amendment"
      amending_regulation: "PMK-150/PMK.03/2021"
      sections_affected: ["Pasal 5", "Pasal 12", "Lampiran I"]
      description: "Updated tax calculation methods"
      
    - event_id: 2
      date: "2022-03-20"
      type: "partial_amendment"
      amending_regulation: "PMK-075/PMK.03/2022"
      sections_affected: ["Pasal 8", "Pasal 15"]
      description: "Extended deadline for compliance"
      
    - event_id: 3
      date: "2024-01-10"
      type: "revocation"
      amending_regulation: "PMK-025/PMK.03/2024"
      sections_affected: ["all"]
      description: "Completely revoked due to new framework"
  
  current_status: "revoked"
  effective_periods:
    - start: "2020-08-01"
      end: "2021-06-14"
      version: "original"
    - start: "2021-06-15"
      end: "2022-03-19"
      version: "amended_v1"
    - start: "2022-03-20"
      end: "2024-01-09"
      version: "amended_v2"
    - start: "2024-01-10"
      end: null
      version: "revoked"
```

### Version Control System
```json
{
  "regulation_id": "PMK-123/PMK.03/2023",
  "versions": {
    "v1.0": {
      "effective_date": "2023-01-01",
      "source_regulation": "PMK-123/PMK.03/2023",
      "content_hash": "sha256:abc123...",
      "sections": {
        "pasal_1": "content...",
        "pasal_2": "content...",
        "lampiran_1": "content..."
      }
    },
    "v1.1": {
      "effective_date": "2023-06-15",
      "source_regulation": "PMK-200/PMK.03/2023",
      "amendment_type": "partial",
      "content_hash": "sha256:def456...",
      "changed_sections": ["pasal_2"],
      "sections": {
        "pasal_1": "content...",
        "pasal_2": "updated content...",
        "lampiran_1": "content..."
      },
      "change_summary": "Updated calculation methodology in Article 2"
    }
  },
  "current_version": "v1.1"
}
```

## Automated Monitoring

### Daily Monitoring Tasks
```python
def daily_amendment_scan():
    """Scan for new amendments in official sources"""
    sources = [
        "https://peraturan.go.id/",
        "https://www.kemenkeu.go.id/informasi-publik/peraturan-perundang-undangan",
        "https://jdih.kemenkeu.go.id/"
    ]
    
    new_amendments = []
    for source in sources:
        regulations = fetch_recent_regulations(source, days=1)
        for reg in regulations:
            if is_amendment_regulation(reg):
                amendment_data = extract_amendment_details(reg)
                new_amendments.append(amendment_data)
                update_amendment_chain(amendment_data)
    
    return new_amendments
```

### Change Impact Analysis
```python
def analyze_amendment_impact(amendment_data):
    """Analyze the impact of regulation amendments"""
    impact_analysis = {
        'affected_systems': [],
        'compliance_changes': [],
        'implementation_timeline': {},
        'stakeholder_notifications': []
    }
    
    # Check system integrations
    affected_systems = query_systems_by_regulation(amendment_data['original_regulation'])
    for system in affected_systems:
        impact_analysis['affected_systems'].append({
            'system_name': system.name,
            'impact_level': assess_system_impact(system, amendment_data),
            'required_changes': identify_system_changes(system, amendment_data)
        })
    
    # Check compliance requirements
    compliance_changes = analyze_compliance_impact(amendment_data)
    impact_analysis['compliance_changes'] = compliance_changes
    
    return impact_analysis
```

## Notification System

### Stakeholder Categories
1. **Internal KEMENKEU Units**
   - Policy makers
   - Implementation teams
   - Compliance officers
   - System administrators

2. **External Stakeholders**
   - Taxpayers and businesses
   - Financial institutions
   - Legal practitioners
   - Audit firms

3. **System Integrators**
   - SPAN operators
   - SAKTI administrators
   - Third-party service providers

### Notification Templates
```yaml
amendment_notification:
  template_id: "PMK_AMENDMENT_ALERT"
  recipients:
    internal:
      - unit: "Direktorat Jenderal Pajak"
        notification_level: "high"
      - unit: "Sekretariat Jenderal"
        notification_level: "medium"
    external:
      - category: "registered_taxpayers"
        notification_level: "high"
        delivery_method: ["email", "website_banner"]
  
  content_template: |
    PEMBERITAHUAN PERUBAHAN PERATURAN
    
    Peraturan: {original_regulation_title}
    Nomor: {original_regulation_id}
    
    DIUBAH DENGAN:
    Peraturan: {amending_regulation_title}
    Nomor: {amending_regulation_id}
    Tanggal Berlaku: {effective_date}
    
    RINGKASAN PERUBAHAN:
    {change_summary}
    
    DAMPAK TERHADAP SISTEM:
    {system_impact_summary}
    
    TINDAKAN YANG DIPERLUKAN:
    {required_actions}
```

## Quality Assurance

### Validation Checkpoints
1. **Amendment Detection Accuracy**
   - False positive rate < 2%
   - False negative rate < 1%
   - Manual review for complex cases

2. **Chain Integrity**
   - No missing links in amendment chains
   - Consistent timeline ordering
   - Proper status propagation

3. **Impact Analysis Completeness**
   - All affected systems identified
   - Compliance requirements mapped
   - Stakeholder notifications sent

### Performance Metrics
```yaml
tracking_metrics:
  detection_speed:
    target: "< 4 hours from publication"
    current: "2.3 hours average"
  
  accuracy_rates:
    amendment_classification: "97.8%"
    regulation_identification: "99.1%"
    impact_assessment: "94.2%"
  
  coverage_completeness:
    pmk_regulations: "100%"
    per_regulations: "85%"
    international_alignments: "78%"
```