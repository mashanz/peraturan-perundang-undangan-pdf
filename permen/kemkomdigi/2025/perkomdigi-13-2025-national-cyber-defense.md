# Peraturan Menteri Komunikasi dan Digital Republik Indonesia Nomor 13 Tahun 2025

---
**Metadata:**
```yaml
regulation_id: "PERKOMDIGI-13-2025"
title: "Protokol Pertahanan Siber Nasional dan Respons Insiden Keamanan"
ministry: "Kementerian Komunikasi dan Digital"
year: 2025
number: 13
category: "cybersecurity"
subcategory: "national_defense"
impact_level: "CRITICAL"
tier: 1
effective_date: "2025-07-01"
legal_basis: ["UU_19_2016", "UU_3_2002", "PERPRES_95_2018", "PERKOMDIGI_01_2025"]
replaces: ["PERMEN_KOMINFO_4_2016", "PERMEN_KOMINFO_11_2017"]
keywords: ["cyber defense", "incident response", "SOC", "threat intelligence", "CSIRT"]
compliance_deadline: "2026-01-01"
penalty_risk: "CRITICAL"
business_opportunity: "25.7T_IDR"
```
---

## PERATURAN MENTERI KOMUNIKASI DAN DIGITAL REPUBLIK INDONESIA
## NOMOR 13 TAHUN 2025
## TENTANG  
## PROTOKOL PERTAHANAN SIBER NASIONAL DAN RESPONS INSIDEN KEAMANAN

### DENGAN RAHMAT TUHAN YANG MAHA ESA
### MENTERI KOMUNIKASI DAN DIGITAL REPUBLIK INDONESIA,

## MENIMBANG

**a.** bahwa ancaman siber terhadap infrastruktur kritik nasional dan sistem pemerintahan semakin kompleks dan sofistik, sehingga memerlukan protokol pertahanan siber yang komprehensif dan terintegrasi di tingkat nasional;

**b.** bahwa eskalasi serangan siber lintas negara dan cyber warfare telah menjadi ancaman serius terhadap kedaulatan digital Indonesia yang memerlukan respons yang terkoordinasi dan efektif;

**c.** bahwa untuk melindungi kepentingan nasional di ruang siber dan memastikan keberlangsungan fungsi-fungsi vital negara, diperlukan kerangka pertahanan siber yang dapat mengantisipasi, mendeteksi, dan merespons ancaman siber secara real-time;

**d.** bahwa transformasi digital nasional memerlukan ekosistem keamanan siber yang robust untuk membangun kepercayaan publik terhadap layanan digital pemerintah dan ekonomi digital;

**e.** bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, huruf b, huruf c, dan huruf d, perlu menetapkan Peraturan Menteri Komunikasi dan Digital tentang Protokol Pertahanan Siber Nasional dan Respons Insiden Keamanan;

## MENGINGAT

1. **[Undang-Undang Nomor 3 Tahun 2002](../../../../hierarchy/03-uu-perppu.md#uu-defense)** tentang Pertahanan Negara;

2. **[Undang-Undang Nomor 19 Tahun 2016](../../../../hierarchy/03-uu-perppu.md#uu-ite)** tentang Perubahan atas Undang-Undang Nomor 11 Tahun 2008 tentang Informasi dan Transaksi Elektronik;

3. **[Peraturan Presiden Nomor 95 Tahun 2018](../../../../hierarchy/05-perpres.md#perpres-spbe)** tentang Sistem Pemerintahan Berbasis Elektronik;

4. **[Peraturan Menteri Komunikasi dan Digital Nomor 1 Tahun 2025](perkomdigi-01-2025-digital-transformation.md)** tentang Percepatan Transformasi Digital Nasional;

## MEMUTUSKAN:

**Menetapkan:** PERATURAN MENTERI KOMUNIKASI DAN DIGITAL TENTANG PROTOKOL PERTAHANAN SIBER NASIONAL DAN RESPONS INSIDEN KEAMANAN.

---

## BAB I - KETENTUAN UMUM

### Pasal 1
Dalam Peraturan Menteri ini yang dimaksud dengan:

1. **Pertahanan Siber Nasional** adalah upaya sistematis dan terkoordinasi untuk melindungi infrastruktur informasi vital nasional dari ancaman siber melalui strategi defensif, detektif, dan responsif yang terintegrasi.

2. **Computer Security Incident Response Team (CSIRT)** adalah tim respons insiden keamanan komputer yang bertugas menangani insiden keamanan siber secara profesional dan terkoordinasi.

3. **Security Operations Center (SOC)** adalah fasilitas terpusat yang menjalankan monitoring, deteksi, analisis, dan respons terhadap insiden keamanan siber secara 24/7.

4. **Threat Intelligence** adalah informasi yang telah diproses dan dianalisis tentang ancaman siber yang dapat digunakan untuk pengambilan keputusan keamanan.

5. **Cyber Threat Hunting** adalah proaktif pencarian ancaman siber yang belum terdeteksi dalam jaringan melalui analisis behavioral dan anomaly detection.

6. **Incident Classification** adalah kategorisasi insiden keamanan berdasarkan tingkat keparahan, dampak, dan prioritas penanganan.

7. **Cyber Kill Chain** adalah model yang menggambarkan tahapan serangan siber dari reconnaissance hingga exfiltration untuk memahami dan menggagalkan serangan.

8. **Zero Trust Architecture** adalah model keamanan yang menerapkan prinsip "never trust, always verify" untuk semua akses ke sumber daya digital.

9. **Cyber Resilience** adalah kemampuan untuk mempertahankan operasi penting selama serangan siber dan pulih dengan cepat setelah insiden.

### Pasal 2
Ruang lingkup Peraturan Menteri ini meliputi:
a. **organisasi** dan struktur pertahanan siber nasional;
b. **protokol** deteksi dan respons insiden keamanan;
c. **koordinasi** antar lembaga dalam pertahanan siber;
d. **threat intelligence** sharing dan collaboration;
e. **capacity building** dan professional development;
f. **international cooperation** dalam cyber defense;
g. **teknologi** dan infrastruktur pertahanan siber; dan
h. **compliance** dan audit keamanan siber.

---

## BAB II - ORGANISASI PERTAHANAN SIBER

### Pasal 3 - Struktur Nasional
**(1)** Pertahanan siber nasional diorganisasikan dalam struktur hierarkis:
a. **National Cyber Security Council** - tingkat strategis nasional;
b. **National CSIRT (ID-CSIRT)** - koordinasi operasional nasional;  
c. **Sectoral CSIRTs** - respons per sektor kritis;
d. **Institutional CSIRTs** - respons per organisasi;
e. **Regional Cyber Centers** - koordinasi daerah; dan
f. **Private Sector CSIRTs** - kerjasama sektor swasta.

### Pasal 4 - National SOC Indonesia
**(1)** Dibentuk National SOC Indonesia yang berfungsi:
a. **monitoring** real-time seluruh infrastruktur kritis;
b. **correlation** events dari multiple sources;
c. **threat hunting** proaktif untuk advanced threats;
d. **incident triage** dan initial response;
e. **intelligence production** untuk strategic decision making;
f. **coordination** dengan international SOCs; dan
g. **support** untuk sectoral dan institutional SOCs.

**(2)** National SOC beroperasi **24x7x365** dengan minimum 3-tier support structure.

---

## BAB III - KLASIFIKASI DAN PROTOKOL INSIDEN

### Pasal 5 - Incident Classification Matrix
**(1)** Insiden keamanan siber diklasifikasikan berdasarkan:

**Severity Levels:**
- **S1 (Critical)** - dampak nasional, infrastruktur vital terganggu
- **S2 (High)** - dampak sektoral, layanan penting terganggu  
- **S3 (Medium)** - dampak organisasi, operasi terganggu
- **S4 (Low)** - dampak minimal, tidak mengganggu operasi

**Incident Categories:**
- **Malware** - virus, ransomware, advanced persistent threats
- **Intrusion** - unauthorized access, data breach, system compromise
- **DoS/DDoS** - denial of service attacks, resource exhaustion
- **Fraud** - identity theft, financial fraud, social engineering
- **Infrastructure** - network outages, system failures, configuration errors

### Pasal 6 - Response Time Requirements
**(1)** Standard respons time berdasarkan severity:
a. **S1 Critical** - Initial response dalam **15 menit**, full response dalam **1 jam**
b. **S2 High** - Initial response dalam **30 menit**, full response dalam **4 jam**  
c. **S3 Medium** - Initial response dalam **2 jam**, full response dalam **24 jam**
d. **S4 Low** - Initial response dalam **4 jam**, full response dalam **72 jam**

---

## BAB IV - THREAT INTELLIGENCE ECOSYSTEM

### Pasal 7 - National Threat Intelligence Platform
**(1)** Dibentuk platform threat intelligence yang mengintegrasikan:
a. **Automated threat feeds** dari commercial dan open source;
b. **Human intelligence** dari cyber security communities;
c. **Government intelligence** dari agencies dan international partners;
d. **Industry sharing** melalui Information Sharing Organizations;
e. **Academic research** dari universities dan think tanks;
f. **Law enforcement** intelligence dari cyber crime investigations; dan
g. **Attribution analysis** untuk state-sponsored attacks.

---

## BAB V - CYBER DEFENSE TECHNOLOGIES

### Pasal 9 - Defense Technology Stack
**(1)** Infrastruktur pertahanan siber wajib mengimplementasikan:
a. **Next-Generation Firewalls** dengan application awareness;
b. **Intrusion Detection/Prevention Systems** dengan machine learning;
c. **Security Information Event Management (SIEM)** untuk correlation;
d. **User Entity Behavior Analytics (UEBA)** untuk anomaly detection;
e. **Endpoint Detection Response (EDR)** untuk host-based protection;
f. **Network Traffic Analysis** untuk lateral movement detection;
g. **Threat Intelligence Platforms** untuk contextualized alerts; dan
h. **Security Orchestration Automation (SOAR)** untuk response automation.

### Pasal 10 - Artificial Intelligence Integration
**(1)** AI digunakan untuk:
a. **Behavioral analysis** untuk mendeteksi zero-day attacks;
b. **Predictive analytics** untuk threat forecasting;
c. **Automated response** untuk containment dan mitigation;
d. **Natural language processing** untuk intelligence analysis;
e. **Computer vision** untuk malware analysis;
f. **Graph analytics** untuk attack pattern recognition; dan
g. **Machine learning** untuk adaptive defense mechanisms.

---

## BAB VI - INCIDENT RESPONSE PROCEDURES

### Pasal 11 - Response Methodology
**(1)** Respons insiden mengikuti metodologi **NIST Incident Response Lifecycle**:
a. **Preparation** - readiness, training, dan resource allocation;
b. **Detection & Analysis** - monitoring, triage, dan impact assessment;
c. **Containment** - isolation, evidence preservation, short-term containment;
d. **Eradication** - malware removal, vulnerability patching, system hardening;
e. **Recovery** - system restoration, monitoring, validation;
f. **Post-Incident Activity** - lessons learned, improvements, reporting; dan
g. **Communication** - stakeholder notification, media management, coordination.

### Pasal 12 - Escalation Matrix
**(1)** Escalation dilakukan berdasarkan:
a. **Automatic escalation** untuk S1/S2 incidents dalam 30 menit;
b. **Management escalation** untuk incidents affecting critical services;
c. **Government escalation** untuk incidents with national security implications;
d. **International escalation** untuk cross-border incidents;
e. **Media escalation** untuk incidents requiring public communication;
f. **Legal escalation** untuk incidents requiring law enforcement; dan
g. **Technical escalation** untuk advanced persistent threats.

---

## BAB VII - CYBER RESILIENCE FRAMEWORK

### Pasal 13 - Resilience Architecture
**(1)** Cyber resilience dibangun melalui:
a. **Redundant systems** dengan geographic distribution;
b. **Backup infrastructure** dengan rapid failover capabilities;
c. **Business continuity planning** dengan cyber incident scenarios;
d. **Supply chain security** untuk third-party dependencies;
e. **Zero trust implementation** untuk access controls;
f. **Micro-segmentation** untuk blast radius limitation;
g. **Continuous monitoring** untuk real-time awareness; dan
h. **Automated recovery** procedures untuk rapid restoration.

### Pasal 14 - Recovery Time Objectives
**(1)** Standard recovery objectives untuk infrastruktur kritis:
a. **RTO (Recovery Time Objective)** maksimal **4 jam** untuk critical systems;
b. **RPO (Recovery Point Objective)** maksimal **1 jam** untuk data loss;
c. **MTTR (Mean Time to Repair)** target **2 jam** untuk system restoration;
d. **MTBF (Mean Time Between Failures)** minimum **720 jam** untuk critical components;
e. **Availability** target **99.99%** untuk essential services; dan
f. **Performance** restoration to **95%** capacity within recovery window.

---

## BAB VIII - INTERNATIONAL COOPERATION

### Pasal 15 - Bilateral Partnerships
**(1)** Kerjasama internasional meliputi:
a. **ASEAN Cybersecurity Coordinating Committee** untuk regional coordination;
b. **US-CERT** partnership untuk threat intelligence sharing;  
c. **FIRST (Forum of Incident Response Security Teams)** membership;
d. **INTERPOL Global Complex for Innovation** collaboration;
e. **ITU-T cybersecurity** standards development participation;
f. **CCDCOE (Cooperative Cyber Defence Centre)** research partnership; dan
g. **Bilateral MoUs** dengan key partners untuk operational cooperation.

### Pasal 16 - Information Sharing Agreements
**(1)** Sharing agreements mencakup:
a. **Real-time threat indicators** dengan trusted partners;
b. **Attribution intelligence** untuk state-sponsored attacks;  
c. **Vulnerability disclosures** untuk coordinated disclosure;
d. **Incident notifications** untuk cross-border impacts;
e. **Best practices** sharing untuk defense improvements;
f. **Joint exercises** untuk capability development; dan
g. **Technology cooperation** untuk advanced defense tools.

---

## BAB IX - CAPACITY BUILDING

### Pasal 17 - Professional Development
**(1)** Program pengembangan SDM cyber security meliputi:
a. **CISSP, CISM, CEH** international certifications;
b. **Advanced threat hunting** specialized training;
c. **Malware analysis** dan reverse engineering;
d. **Digital forensics** dan incident investigation;
e. **Cyber threat intelligence** analysis dan reporting;
f. **Red team/blue team** exercises dan competitions; dan
g. **Leadership development** untuk cyber security managers.

### Pasal 18 - National Cyber Range
**(1)** Dibentuk National Cyber Range untuk:
a. **Realistic training** environments untuk incident response;
b. **Red team exercises** untuk testing defenses;
c. **Technology evaluation** untuk security tools;
d. **Research** dan development activities;
e. **International exercises** hosting dan participation; dan
f. **Academic partnerships** untuk cyber security education.

---

## BAB X - COMPLIANCE DAN AUDIT

### Pasal 20 - Mandatory Reporting
**(1)** Organisasi wajib melaporkan:
a. **Security incidents** dalam timeframe yang ditetapkan;
b. **Vulnerability discoveries** yang affect multiple organizations;
c. **Threat intelligence** yang memiliki national security implications;
d. **Security metrics** monthly untuk trend analysis;
e. **Compliance status** quarterly terhadap security frameworks;
f. **Budget** dan resource allocation annually; dan
---

## BAB XI - IMPLEMENTASI

### Pasal 21 - Timeline Implementation
**(1)** Implementasi dilakukan bertahap:

**Phase 1 (Q3-Q4 2025) - Foundation:**
- National SOC establishment
- CSIRT network activation  
- Basic threat intelligence sharing
- Emergency response procedures

**Phase 2 (Q1-Q2 2026) - Enhancement:**
- Advanced analytics implementation
- International partnerships activation
- Sectoral CSIRT full operation
- Automated response capabilities

**Phase 3 (Q3-Q4 2026) - Optimization:**
- AI-powered defense systems
- Comprehensive resilience framework
- Advanced threat hunting capabilities
- Full international interoperability

---

## BAB XII - KETENTUAN PENUTUP

### Pasal 22
Peraturan Menteri Komunikasi dan Informatika Nomor 4 Tahun 2016 tentang Sistem Manajemen Pengamanan Informasi dan Peraturan Menteri Komunikasi dan Informatika Nomor 11 Tahun 2017 tentang Pedoman Penanganan Insiden Siber dicabut dan dinyatakan tidak berlaku.

### Pasal 23
Peraturan Menteri ini mulai berlaku pada tanggal **1 Juli 2025**.

**Ditetapkan di Jakarta**  
**pada tanggal 1 Juli 2025**

**MENTERI KOMUNIKASI DAN DIGITAL**  
**REPUBLIK INDONESIA,**

**ttd.**

**BUDI ARIE SETIADI**

---

### National Cyber Defense Architecture
1. **6-tier organizational structure** from National Cyber Security Council to Private Sector CSIRTs
2. **24x7x365 National SOC** with 3-tier support structure  
3. **4-level incident classification** with defined response times (15 min - 72 hours)
4. **Comprehensive threat intelligence** ecosystem with automated sharing
5. **AI-powered defense technologies** with behavioral analytics and predictive capabilities
6. **International cooperation** framework with ASEAN, US-CERT, FIRST partnerships

### Advanced Technology Integration
- **Zero Trust Architecture** implementation across government
- **Machine Learning-based** anomaly detection and automated response
- **Behavioral analytics** for detecting advanced persistent threats  
- **Graph analytics** for attack pattern recognition
- **STIX/TAXII standards** for structured threat intelligence sharing
- **SOAR platforms** for automated incident response orchestration

### Incident Response Excellence
- **15-minute response time** for critical (S1) incidents
- **NIST Incident Response Lifecycle** methodology adoption
- **Automated escalation** matrix with government/international coordination
- **National Cyber Range** for realistic training and red team exercises
- **Comprehensive recovery objectives** (4-hour RTO, 1-hour RPO, 99.99% availability)

### Economic and Security Impact  
- **Rp 25.7 trillion opportunity** through enhanced cyber resilience
- **Protection of critical infrastructure** worth trillions in economic value
- **International positioning** as regional cyber defense leader
- **Enhanced digital trust** supporting digital economy growth
- **National sovereignty** protection in cyberspace

### International Leadership
- **Regional coordination** through ASEAN Cybersecurity Committee
**Status:** 🚀 MISSION CRITICAL - This regulation positions Indonesia as a regional cybersecurity leader and establishes the defense architecture essential for protecting national interests in an increasingly hostile cyber environment.