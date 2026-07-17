# ContaAI

ERP contabil asistat de AI. AI-ul generează propuneri; postarea contabilă necesită aprobarea explicită a unui utilizator autorizat.

## Sprint 1 — Identity & Authentication

- parole Argon2
- access token JWT, 15 minute
- refresh token JWT, 30 zile, rotație și revocare în PostgreSQL
- cookie-uri HttpOnly
- register, login, refresh, logout și profil curent
- pagini Next.js pentru autentificare, înregistrare și dashboard

## Actualizare din foundation-v1

Păstrează fișierul `.env` existent și adaugă variabilele lipsă din `.env.example`, apoi:

```bash
docker compose up --build -d
docker compose logs --tail=100 api web
```

Endpoint-uri:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`
- `GET /health`

UI:

- `http://SERVER_IP:3000/login`
- `http://SERVER_IP:3000/register`
- `http://SERVER_IP:3000/dashboard`
