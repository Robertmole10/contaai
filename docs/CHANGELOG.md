# ContaAI — Istoric versiuni

Acest document descrie evoluția platformei ContaAI, funcționalitățile adăugate în fiecare versiune și modificările importante dintre versiuni.

## [În dezvoltare] — Sprint 3: Document Inbox

Planificat:
- încărcare documente PDF, JPG și PNG;
- stocare securizată în MinIO;
- inbox de documente cu statusuri și filtre;
- procesare asincronă prin worker și Redis;
- fundație pentru OCR și extracție AI.

## [0.2.0] — Multi-tenancy și ERP Workspace

Lansată după finalizarea Sprintului 2.

### Adăugat
- organizații și companii multiple;
- membership-uri pentru utilizatori;
- roluri și permisiuni RBAC;
- roluri implicite: Owner, Administrator, Accountant, Auditor și Employee;
- onboarding pentru prima organizație și prima companie;
- company switcher;
- dashboard ERP cu sidebar, metrici și acțiuni rapide;
- API-uri pentru workspace, organizații și companii;
- migrarea Alembic `0003_multi_tenancy`.

### Schimbat
- dashboard-ul simplu din versiunea 0.1 a fost înlocuit cu un workspace ERP multi-companie;
- structura aplicației a fost pregătită pentru modulele Documente, Facturi, Contabilitate, TVA și Rapoarte.

## [0.1.0] — Authentication & Identity

Prima versiune funcțională ContaAI.

### Adăugat
- înregistrare utilizator;
- autentificare și deconectare;
- JWT access token și refresh token;
- parole securizate cu Argon2;
- endpoint `/auth/me`;
- dashboard inițial;
- migrarea Alembic `0002_authentication`;
- infrastructură Docker cu PostgreSQL, Redis, MinIO, FastAPI, Next.js și worker.

## Reguli de versionare

ContaAI folosește versionare semantică:
- **MAJOR**: schimbări majore sau incompatibile;
- **MINOR**: funcționalități noi compatibile;
- **PATCH**: corecții și îmbunătățiri fără funcționalități majore noi.
