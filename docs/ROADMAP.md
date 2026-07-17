# ContaAI Roadmap

## Finalizat

### Sprint 1 — Authentication

- Înregistrare utilizator
- Autentificare JWT
- Refresh tokens
- Logout
- Argon2
- Endpoint `/auth/me`
- Dashboard inițial

Versiune: `v0.1.0`

### Sprint 2 — Multi-tenancy și RBAC

- Organizații
- Companii
- Memberships
- Roluri
- Permisiuni
- Workspace
- Dashboard multi-tenant

Versiune: `v0.2.0`

## În lucru

### Foundation v0.3 — Architecture and Documentation

- Documentație tehnică
- Architecture Decision Records
- Convenții pentru module
- Convenții Git
- Definirea ciclului de viață al documentelor
- Definirea principiilor motorului contabil
- Definirea principiilor AI

### Sprint 3 — Document Inbox

#### Sprint 3.1

- Model Document
- Migrare Alembic
- Upload PDF, JPG și PNG
- Stocare MinIO
- Checksum SHA-256
- Listarea documentelor
- Descărcare securizată
- Control acces la nivel de companie

#### Sprint 3.2

- Redis queue
- Worker pentru procesarea documentelor
- Stări de procesare

### Sprint 4 — OCR

- Extragerea textului
- Detectarea paginilor
- Stocarea rezultatului OCR
- Gestionarea erorilor

### Sprint 5 — AI Extraction

- Clasificare document
- Extragere furnizor
- Extragere număr factură
- Extragere date
- Extragere TVA
- Extragere total
- Confidence scores

### Sprint 6 — Human Review

- Interfață de verificare
- Corectarea câmpurilor
- Aprobare
- Respingere
- Audit trail

### Sprint 7 — Accounting Engine

- Plan de conturi
- Reguli contabile deterministe
- Propuneri de note contabile
- Debit și credit
- Validare balanță
- Aprobare umană obligatorie

### Sprint 8 — Journals

- Jurnal cumpărări
- Jurnal vânzări
- Registru jurnal
- Registru inventar

### Sprint 9 — VAT

- Coduri TVA
- Jurnale TVA
- Declarații
- Validări fiscale

### Sprint 10 — Reports

- Balanță
- Fișe de cont
- Profit și pierdere
- Situații financiare
