# ContaAI Documentation

ContaAI este un ERP contabil asistat de inteligență artificială.

## Principii fundamentale

1. AI-ul nu postează automat în contabilitate.
2. Orice propunere contabilă trebuie aprobată de un utilizator autorizat.
3. Motorul contabil este determinist.
4. Operațiunile importante trebuie să fie auditabile.
5. Datele contabile nu sunt șterse fizic fără un motiv legal și un proces controlat.
6. Fiecare companie este izolată în cadrul arhitecturii multi-tenant.

## Structura documentației

- `ROADMAP.md` — direcția și etapele de dezvoltare
- `CHANGELOG.md` — modificările implementate
- `FEATURES.md` — funcționalitățile disponibile
- `architecture/` — arhitectura tehnică
- `adr/` — decizii de arhitectură
- `versions/` — istoricul versiunilor

## Stack tehnologic

### Backend

- FastAPI
- SQLAlchemy 2
- PostgreSQL
- Alembic
- Redis
- MinIO

### Frontend

- Next.js

### Infrastructură

- Docker Compose
- Cloudflare Tunnel
- GitHub
