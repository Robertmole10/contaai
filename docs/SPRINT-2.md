# Sprint 2 — Multi-tenancy and ERP workspace

## Included

- Organization ownership through memberships
- Multiple companies per organization
- Roles: Owner, Administrator, Accountant, Auditor, Employee
- Permission catalog and role-permission mappings
- Tenant-scoped organization and company endpoints
- Initial organization/company onboarding
- Company switcher
- ERP sidebar, metrics, recent activity and quick actions

## API endpoints

- `GET /workspace`
- `GET /organizations`
- `POST /organizations`
- `GET /organizations/{organization_id}/companies`
- `POST /organizations/{organization_id}/companies`

All workspace endpoints require the existing authenticated session cookie.

## Apply on Ubuntu

Copy the archive contents over the project while preserving `.env` and `.git`, then run:

```bash
cd ~/Projects/contaai
docker compose down
docker compose up --build -d

docker compose exec api alembic current
docker compose exec api alembic heads
docker compose logs --tail=100 api web
```

The API startup script already runs `alembic upgrade head`.
