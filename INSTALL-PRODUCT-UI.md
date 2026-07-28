# Instalare ContaAI Product UI v1

Din rădăcina proiectului:

```bash
unzip -o contaai-product-ui-v1.zip

docker compose build web
docker compose up -d --force-recreate web
docker compose logs --tail=100 web
```

Verificare build înainte de commit:

```bash
docker compose exec web npm run build
```

Verificare browser:
- login-ul rămâne funcțional;
- dashboard-ul încarcă `/auth/me` și `/workspace`;
- schimbarea workspace-ului schimbă lista companiilor;
- Owner/Admin pot deschide formularul de companie;
- rolurile fără `company.manage` văd butonul dezactivat;
- meniul mobil se deschide și se închide;
- Members afișează utilizatorul curent și marchează invitațiile drept funcție viitoare.

Commit recomandat:

```bash
git add apps/web
git commit -m "feat(ui): add ContaAI product design system and workspace views"
git push origin feature/rbac-foundation
```
