# ContaAI

Fundația tehnică pentru un ERP contabil asistat de AI. AI-ul generează propuneri, dar nu postează automat note contabile.

## Pornire rapidă

```bash
cp .env.example .env
nano .env   # schimbă parolele și JWT_SECRET
make up
make logs
```

Servicii:

- Web: http://SERVER_IP:3000
- API: http://SERVER_IP:8000
- API docs: http://SERVER_IP:8000/docs
- MinIO console: http://SERVER_IP:9001

## Verificare

```bash
docker compose ps
curl http://localhost:8000/health
```

## Oprire

```bash
make down
```

## Reset complet al datelor de dezvoltare

```bash
make clean
```
