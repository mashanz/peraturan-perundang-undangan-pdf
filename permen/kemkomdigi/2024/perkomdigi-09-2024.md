# Peraturan Menteri Komunikasi dan Digital Republik Indonesia Nomor 9 Tahun 2024

---
**Metadata:**
```yaml
regulation_id: "PERKOMDIGI-09-2024"
title: "Identitas Digital Nasional"
ministry: "Kementerian Komunikasi dan Digital"
year: 2024
number: 9
category: "transformasi_digital"
subcategory: "digital_identity"
impact_level: "CRITICAL"
tier: 3
effective_date: "2024-12-17"
legal_basis: ["UU_19_2016", "UU_27_2022"]
keywords: ["digital identity", "authentication", "interoperability", "single sign-on"]
rollout_timeline: "2025-2027"
penalty_risk: "MEDIUM"
business_opportunity: "12.1T_IDR"
```
---

## PERATURAN MENTERI KOMUNIKASI DAN DIGITAL REPUBLIK INDONESIA
## NOMOR 9 TAHUN 2024
## TENTANG
## IDENTITAS DIGITAL NASIONAL

### DENGAN RAHMAT TUHAN YANG MAHA ESA
### MENTERI KOMUNIKASI DAN DIGITAL REPUBLIK INDONESIA,

## MENIMBANG

**a.** bahwa dalam era transformasi digital, identitas digital yang terintegrasi dan interoperabel merupakan fondasi penting untuk memberikan layanan digital yang efisien, aman, dan terpercaya kepada masyarakat;

**b.** bahwa untuk mendukung visi Indonesia Digital 2045 dan mempercepat transformasi digital nasional, diperlukan sistem identitas digital nasional yang dapat digunakan secara universal di berbagai platform dan layanan digital;

**c.** bahwa sistem identitas digital nasional harus memenuhi standar keamanan tertinggi dan memberikan perlindungan optimal terhadap data pribadi warga negara;

**d.** bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, huruf b, dan huruf c, perlu menetapkan Peraturan Menteri Komunikasi dan Digital tentang Identitas Digital Nasional;

## MENGINGAT

1. **[Undang-Undang Nomor 19 Tahun 2016](../../../../hierarchy/03-uu-perppu.md#uu-ite)** tentang Perubahan atas Undang-Undang Nomor 11 Tahun 2008 tentang Informasi dan Transaksi Elektronik;

2. **[Undang-Undang Nomor 27 Tahun 2022](../../../../hierarchy/03-uu-perppu.md#uu-pdp)** tentang Pelindungan Data Pribadi;

3. **[Peraturan Presiden Nomor 95 Tahun 2018](../../../../hierarchy/05-perpres.md#perpres-spbe)** tentang Sistem Pemerintahan Berbasis Elektronik;

## MEMUTUSKAN:

**Menetapkan:** PERATURAN MENTERI KOMUNIKASI DAN DIGITAL TENTANG IDENTITAS DIGITAL NASIONAL.

---

## BAB I - KETENTUAN UMUM

### Pasal 1
Dalam Peraturan Menteri ini yang dimaksud dengan:

1. **Identitas Digital Nasional** yang selanjutnya disingkat **IDN** adalah sistem identitas digital terintegrasi yang menyediakan layanan autentikasi dan otorisasi digital untuk warga negara Indonesia dalam mengakses layanan digital pemerintah dan swasta.

2. **Digital ID** adalah identitas unik yang diberikan kepada setiap warga negara Indonesia untuk mengakses layanan digital melalui sistem IDN.

3. **Penyedia Identitas Digital** yang selanjutnya disingkat **Identity Provider (IdP)** adalah entitas yang bertanggung jawab untuk mengelola dan memverifikasi identitas digital pengguna.

4. **Penyedia Layanan** yang selanjutnya disingkat **Service Provider (SP)** adalah entitas yang menyediakan layanan digital dan menggunakan IDN untuk autentikasi pengguna.

5. **Level of Assurance (LoA)** adalah tingkat kepercayaan dalam proses autentikasi identitas digital yang terdiri dari LoA-1 (rendah), LoA-2 (sedang), LoA-3 (tinggi), dan LoA-4 (sangat tinggi).

6. **Single Sign-On (SSO)** adalah mekanisme autentikasi yang memungkinkan pengguna mengakses multiple layanan digital dengan satu kali proses login.

7. **Federasi Identitas** adalah sistem yang memungkinkan berbagai organisasi saling berbagi informasi identitas digital dengan aman dan terpercaya.

8. **Biometrik** adalah teknologi pengenalan pola biologis atau perilaku manusia untuk keperluan identifikasi dan verifikasi identitas.

9. **Multi-Factor Authentication (MFA)** adalah metode autentikasi yang menggunakan kombinasi dua atau lebih faktor: sesuatu yang diketahui (password), sesuatu yang dimiliki (token), dan sesuatu yang melekat (biometrik).

10. **Menteri** adalah menteri yang menyelenggarakan urusan pemerintahan di bidang komunikasi dan informatika.

### Pasal 2
Tujuan penyelenggaraan IDN adalah:
a. **menyediakan identitas digital yang aman dan terpercaya** bagi warga negara Indonesia;
b. **memfasilitasi akses yang mudah** terhadap layanan digital pemerintah dan swasta;
c. **meningkatkan efisiensi** dalam pemberian layanan publik;
d. **mengurangi biaya administrasi** dan meningkatkan transparansi;
e. **mendorong inovasi** dalam pengembangan layanan digital; dan
f. **melindungi data pribadi** dan privasi warga negara.

---

## BAB II - ARSITEKTUR SISTEM IDN

### Pasal 3 - Komponen Utama
**(1)** Sistem IDN terdiri dari komponen utama:
a. **Identity Management System** - sistem pengelolaan identitas digital;
b. **Authentication Service** - layanan autentikasi pengguna;
c. **Authorization Service** - layanan otorisasi akses;
d. **Federation Gateway** - gateway untuk integrasi dengan berbagai SP;
e. **Credential Management** - pengelolaan kredensial digital;
f. **Audit and Logging** - sistem audit dan pencatatan aktivitas; dan
g. **Security Operations Center** - pusat operasi keamanan.

**(2)** Setiap komponen sebagaimana dimaksud pada ayat (1) harus memenuhi standar keamanan internasional dan diaudit secara berkala.

### Pasal 4 - Standar Teknis
**(1)** Sistem IDN menggunakan standar teknis internasional yang meliputi:
a. **SAML 2.0** untuk federasi identitas;
b. **OpenID Connect** untuk autentikasi modern;
c. **OAuth 2.0** untuk otorisasi;
d. **FIDO2/WebAuthn** untuk autentikasi tanpa password;
e. **X.509** untuk sertifikat digital; dan
f. **FIPS 140-2 Level 3** untuk modul keamanan kriptografi.

**(2)** Standar teknis dapat disesuaikan atau ditambah sesuai dengan perkembangan teknologi dan kebutuhan keamanan.

---

## BAB III - TINGKAT JAMINAN IDENTITAS (LEVEL OF ASSURANCE)

### Pasal 5 - Klasifikasi LoA
**(1)** Sistem IDN menerapkan 4 (empat) tingkat jaminan identitas:

**a. LoA-1 (Rendah)**
- Self-assertion identitas
- Autentikasi single-factor (username/password)
- Untuk layanan berisiko rendah

**b. LoA-2 (Sedang)**  
- Verifikasi identitas dengan dokumen
- Multi-factor authentication
- Untuk layanan pemerintah umum

**c. LoA-3 (Tinggi)**
- Verifikasi identitas in-person atau remote verification
- Strong cryptographic authentication
- Untuk layanan keuangan dan kesehatan

**d. LoA-4 (Sangat Tinggi)**
- Verifikasi identitas in-person dengan supervised enrollment
- Hardware-based cryptographic authentication
- Untuk layanan kritikal keamanan nasional

### Pasal 6 - Persyaratan Setiap LoA
**(1)** Untuk mencapai LoA-2, pengguna wajib:
a. **memverifikasi identitas** dengan KTP elektronik atau dokumen resmi;
b. **menyediakan informasi kontak** yang dapat diverifikasi;
c. **mengaktifkan MFA** dengan minimal 2 faktor autentikasi; dan
d. **menyetujui** syarat dan ketentuan penggunaan IDN.

**(2)** Untuk mencapai LoA-3, pengguna wajib:
a. **memenuhi persyaratan LoA-2**;
b. **melakukan verifikasi biometrik** (sidik jari atau face recognition);
c. **menyediakan informasi tambahan** sesuai kebutuhan verifikasi; dan
d. **menjalani proses review** oleh petugas verifikasi.

**(3)** Untuk mencapai LoA-4, pengguna wajib:
a. **memenuhi persyaratan LoA-3**;
b. **hadir secara fisik** di lokasi pendaftaran resmi;
c. **menggunakan hardware token** yang disertifikasi; dan
d. **mendapat persetujuan** dari otoritas yang berwenang.

---

## BAB IV - PENYELENGGARAAN IDN

### Pasal 7 - Penyelenggara Utama
**(1)** Menteri bertanggung jawab sebagai penyelenggara utama sistem IDN.

**(2)** Dalam penyelenggaraan IDN, Menteri dapat bekerja sama dengan:
a. **kementerian/lembaga** terkait;
b. **pemerintah daerah**;
c. **BUMN** yang memenuhi kriteria teknis dan keamanan;
d. **penyedia teknologi** yang tersertifikasi; dan
e. **organisasi internasional** untuk standarisasi dan interoperabilitas.

### Pasal 8 - Identity Provider (IdP)
**(1)** IdP adalah entitas yang dapat menerbitkan dan mengelola identitas digital untuk sistem IDN.

**(2)** IdP wajib memenuhi persyaratan:
a. **sertifikasi keamanan** dari lembaga yang diakui;
b. **kepatuhan** terhadap standar teknis IDN;
c. **kapasitas infrastruktur** yang memadai;
d. **sumber daya manusia** yang kompeten;
e. **sistem backup dan recovery** yang handal; dan
f. **asuransi pertanggungjawaban** sesuai ketentuan.

**(3)** IdP wajib menjalani audit keamanan minimal **1 (satu) kali per tahun** oleh auditor independen yang diakui.

### Pasal 9 - Service Provider (SP)
**(1)** SP adalah entitas yang menggunakan layanan IDN untuk autentikasi pengguna dalam layanan digitalnya.

**(2)** SP wajib:
a. **terintegrasi** dengan sistem IDN sesuai standar teknis;
b. **menerapkan protokol keamanan** yang sesuai dengan LoA yang digunakan;
c. **melindungi data** yang diterima dari sistem IDN;
d. **melaporkan insiden keamanan** yang berkaitan dengan IDN; dan
e. **mematuhi** ketentuan penggunaan sistem IDN.

---

## BAB V - PROSES PENDAFTARAN DAN VERIFIKASI

### Pasal 10 - Pendaftaran IDN
**(1)** Setiap warga negara Indonesia berhak mendaftar untuk memperoleh Digital ID.

**(2)** Pendaftaran dapat dilakukan melalui:
a. **portal online** resmi IDN;
b. **aplikasi mobile** IDN;
c. **kantor layanan** pemerintah yang ditunjuk; atau
d. **agen pendaftaran** yang diotorisasi.

**(3)** Proses pendaftaran meliputi:
a. **pengisian formulir** pendaftaran online;
b. **upload dokumen** identitas yang diperlukan;
c. **verifikasi identitas** sesuai LoA yang diinginkan;
d. **aktivasi akun** melalui email atau SMS; dan
e. **setup autentikasi** tambahan (MFA, biometrik).

### Pasal 11 - Verifikasi Identitas
**(1)** Verifikasi identitas dilakukan dengan metode:
a. **document verification** - verifikasi dokumen identitas;
b. **biometric matching** - pencocokan biometrik dengan database;
c. **liveness detection** - deteksi kehidupan untuk mencegah spoofing;
d. **cross-reference check** - pengecekan silang dengan database resmi; dan
e. **manual review** - review manual untuk kasus tertentu.

**(2)** Untuk LoA-3 dan LoA-4, wajib dilakukan **in-person verification** atau **supervised remote verification**.

---

## BAB VI - KEAMANAN DAN PRIVASI

### Pasal 12 - Perlindungan Data
**(1)** Sistem IDN wajib menerapkan prinsip **privacy by design** dan **data minimization**.

**(2)** Data yang disimpan dalam sistem IDN meliputi:
a. **data identitas dasar** - nama, NIK, tanggal lahir;
b. **data autentikasi** - credential, biometrik (dalam bentuk template);
c. **data log** - aktivitas autentikasi dan akses;
d. **data atribut** - informasi tambahan sesuai kebutuhan layanan; dan
e. **data konsent** - persetujuan penggunaan data.

**(3)** **Biometrik** disimpan dalam bentuk **irreversible template** yang tidak dapat direkonstruksi kembali menjadi data asli.

### Pasal 13 - Enkripsi dan Keamanan
**(1)** Semua data dalam sistem IDN wajib dienkripsi menggunakan algoritma yang disetujui oleh BSSN.

**(2)** Komunikasi antar komponen sistem menggunakan **TLS 1.3** atau protokol yang lebih tinggi.

**(3)** Kunci enkripsi dikelola menggunakan **Hardware Security Module (HSM)** yang memenuhi standar FIPS 140-2 Level 3.

**(4)** Sistem IDN menerapkan **zero trust architecture** dengan prinsip "never trust, always verify".

### Pasal 14 - Audit dan Monitoring
**(1)** Sistem IDN dilengkapi dengan **real-time monitoring** dan **Security Information and Event Management (SIEM)**.

**(2)** Seluruh aktivitas dalam sistem IDN wajib dicatat dalam **audit log** yang tidak dapat diubah (immutable).

**(3)** **Penetration testing** dilakukan minimal **2 (dua) kali per tahun** oleh ethical hacker bersertifikat.

---

## BAB VII - INTEROPERABILITAS DAN INTEGRASI

### Pasal 15 - Federasi dengan Sistem Lain
**(1)** Sistem IDN dapat melakukan federasi dengan:
a. **sistem identitas internasional** yang memenuhi standar yang diakui;
b. **sistem identitas sektor** (perbankan, kesehatan, pendidikan);
c. **sistem identitas regional** (ASEAN Digital ID); dan
d. **sistem identitas swasta** yang tersertifikasi.

**(2)** Federasi dilakukan berdasarkan **mutual recognition agreement** dan **trust framework** yang disepakati.

### Pasal 16 - API dan SDK
**(1)** Sistem IDN menyediakan **Application Programming Interface (API)** dan **Software Development Kit (SDK)** untuk integrasi dengan SP.

**(2)** API dan SDK meliputi:
a. **Authentication API** - untuk proses autentikasi;
b. **Attribute API** - untuk mengambil atribut pengguna;
c. **Status API** - untuk cek status identitas;
d. **Notification API** - untuk notifikasi real-time; dan
e. **Admin API** - untuk pengelolaan integrasi.

---

## BAB VIII - IMPLEMENTASI BERTAHAP

### Pasal 17 - Roadmap Implementasi
**(1)** Implementasi IDN dilakukan secara bertahap dalam 3 (tiga) fase:

**Fase 1 (2025)** - Foundation
- Pembangunan infrastruktur core system
- Pendaftaran untuk layanan pemerintah prioritas  
- LoA-1 dan LoA-2 tersedia
- Integrasi dengan 10 layanan pemerintah utama

**Fase 2 (2026)** - Expansion  
- LoA-3 tersedia untuk layanan komersial
- Integrasi dengan sektor perbankan dan fintech
- Mobile app dengan fitur lengkap
- Federasi dengan sistem identitas sektoral

**Fase 3 (2027)** - Maturation
- LoA-4 untuk layanan kritikal
- Federasi internasional (ASEAN Digital ID)  
- AI-powered fraud detection
- Universal adoption across sectors

### Pasal 18 - Kriteria Prioritas Implementasi
**(1)** Prioritas implementasi berdasarkan:
a. **dampak terhadap masyarakat** - layanan yang digunakan secara massal;
b. **tingkat digitalisasi** - sektor yang sudah digital mature;
c. **kebutuhan keamanan** - layanan yang memerlukan autentikasi kuat;
d. **readiness teknologi** - kesiapan infrastruktur dan SDM; dan
e. **dukungan regulasi** - ada payung hukum yang mendukung.

---

## BAB IX - TATA KELOLA DAN PENGAWASAN

### Pasal 19 - Struktur Tata Kelola
**(1)** Tata kelola IDN dilakukan melalui struktur:
a. **Steering Committee** - komite pengarah tingkat strategis;
b. **Technical Committee** - komite teknis untuk standar dan implementasi;
c. **Security Committee** - komite keamanan dan manajemen risiko;
d. **Privacy Committee** - komite privasi dan perlindungan data; dan
e. **Operational Team** - tim operasional harian.

### Pasal 20 - Pengawasan dan Evaluasi
**(1)** Menteri melakukan pengawasan terhadap penyelenggaraan IDN secara berkala.

**(2)** Evaluasi dilakukan setiap **6 (enam) bulan** meliputi:
a. **kinerja sistem** - availability, response time, throughput;
b. **keamanan** - incident, vulnerability, compliance;
c. **user experience** - satisfaction score, usability metrics;
d. **adoption rate** - tingkat adopsi di berbagai sektor; dan
e. **return on investment** - manfaat ekonomi dan sosial.

---

## BAB X - SANKSI DAN PENEGAKAN

### Pasal 21 - Sanksi untuk IdP dan SP
**(1)** IdP atau SP yang melanggar ketentuan dikenai sanksi administratif berupa:
a. **teguran tertulis**;
b. **penghentian sementara** layanan integrasi IDN;
c. **pencabutan sertifikasi** atau otorisasi; dan/atau
d. **denda administratif** maksimal Rp 10.000.000.000,00 (sepuluh miliar rupiah).

**(2)** Sanksi dijatuhkan dengan mempertimbangkan tingkat pelanggaran, dampak terhadap pengguna, dan itikad baik dalam perbaikan.

---

## BAB XI - KETENTUAN PERALIHAN

### Pasal 22
**(1)** Sistem identitas digital yang telah ada sebelum Peraturan Menteri ini berlaku dapat melakukan migrasi atau federasi dengan sistem IDN.

**(2)** Migrasi atau federasi sebagaimana dimaksud pada ayat (1) wajib memenuhi standar teknis dan keamanan yang ditetapkan dalam Peraturan Menteri ini.

**(3)** Proses migrasi atau federasi dilakukan dalam jangka waktu paling lama **2 (dua) tahun** sejak sistem IDN beroperasi penuh.

---

## BAB XII - KETENTUAN PENUTUP

### Pasal 23
Peraturan Menteri ini mulai berlaku pada tanggal **17 Desember 2024**.

**Ditetapkan di Jakarta**  
**pada tanggal 17 Desember 2024**

**MENTERI KOMUNIKASI DAN DIGITAL**  
**REPUBLIK INDONESIA,**

**ttd.**

**BUDI ARIE SETIADI**

**BERITA NEGARA REPUBLIK INDONESIA TAHUN 2024 NOMOR 856**

---

### Business Opportunities
- **Digital transformation acceleration** - Universal authentication infrastructure
- **Service innovation** - New services enabled by trusted identity
- **Cost reduction** - Reduced onboarding and KYC costs
- **International integration** - ASEAN Digital ID participation

### Security Architecture
- **Zero trust model** - Never trust, always verify
- **Hardware security** - HSM for key management, FIPS 140-2 Level 3
- **Real-time monitoring** - SIEM and immutable audit logs
- **Regular testing** - Bi-annual penetration testing

### Privacy Protection
- **GDPR-compliant** - Privacy by design, data minimization
- **Biometric protection** - Irreversible templates, no raw data storage
- **User control** - Consent management, data portability
- **Cross-border safeguards** - Mutual recognition agreements

### Cross-References
- **Legal Foundation:** [UU 19/2016 ITE](../../../../hierarchy/03-uu-perppu.md#uu-ite), [UU 27/2022 PDP](../../../../hierarchy/03-uu-perppu.md#uu-pdp)
- **Digital Government:** [Perpres 95/2018 SPBE](../../../../hierarchy/05-perpres.md#perpres-spbe)
- **Data Protection:** [PDP Implementation (Perkomdigi 2/2024)](perkomdigi-02-2024.md)
- **Platform Integration:** [PSE Platform (Perkomdigi 5/2024)](perkomdigi-05-2024.md)

### Critical Dates
- **Effective:** December 17, 2024
- **Phase 1 Launch:** January 2025 (government services)
- **Commercial Integration:** January 2026 (banking, fintech)
- **Full Maturation:** January 2027 (international federation)

**Status:** 🚀 TRANSFORMATIONAL - Foundation for Indonesia's digital future, enabling new services and economic opportunities