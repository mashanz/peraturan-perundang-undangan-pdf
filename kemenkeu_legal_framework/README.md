# KEMENKEU Legal Framework & Cross-Reference System

## Overview
Comprehensive legal framework mapping and cross-reference system for Indonesia Ministry of Finance regulations.

## System Components

### 1. Legal Hierarchy Database (`legal_hierarchy/`)
- **Primary Laws (UU)**: Undang-Undang (Acts of Parliament)
- **Government Regulations (PP)**: Peraturan Pemerintah
- **Presidential Regulations (Perpres)**: Peraturan Presiden
- **Ministerial Regulations (PMK)**: Peraturan Menteri Keuangan
- **Director General Regulations (PER)**: Peraturan Direktur Jenderal

### 2. Cross-Reference Database (`cross_references/`)
- Citation networks between regulations
- "MENGINGAT" reference mapping
- Implementation dependencies
- Related regulation clusters

### 3. Amendment Tracking System (`amendments/`)
- Complete change history for each regulation
- Revocation tracking
- Amendment chains and lineage
- Status tracking (active/revoked/amended)

### 4. Implementation Framework (`implementation/`)
- System integration mappings (SPAN, SAKTI, etc.)
- Technical requirements
- Compliance frameworks
- Audit and oversight connections

### 5. International Alignment (`international/`)
- Treaty compliance mapping
- Bilateral agreement implementation
- International standard alignment
- Cross-border regulatory harmonization

## Data Sources
- peraturan.go.id (Official Indonesian Legal Database)
- kemenkeu.go.id (Ministry of Finance Official Site)
- JDIH (Legal Information and Documentation Network)
- International treaty databases

## Update Schedule
- Daily: New regulation monitoring
- Weekly: Amendment and revocation tracking
- Monthly: Cross-reference validation
- Quarterly: Comprehensive system review

## Usage
Each component includes detailed documentation, search capabilities, and API endpoints for integration with compliance systems.