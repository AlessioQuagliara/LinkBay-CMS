# SAML local test setup

Questi sono i passi eseguiti per abilitare un provider SAML di prova per il tenant 1 nello sviluppo locale.

1. Generazione certificato self-signed (IdP):

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -subj '/CN=test-local-idp' -keyout /tmp/test-local-idp.key -out /tmp/test-local-idp.crt
```

2. Inserimento provider di test in `tenant_saml_providers` (esempio di colonne usate):
- `issuer`: `urn:test-local-idp`
- `certificate`: contenuto PEM del certificato generato
- `sso_login_url`: `http://localhost:8080/sso`
- `metadata_url`: NULL (usiamo certificato + issuer)

3. Comandi utilizzati per aggiornare il DB (esempio):

```bash
# creare file SQL che contiene il certificato PEM in modo sicuro
cat > /tmp/update_saml.sql <<'SQL'
UPDATE tenant_saml_providers
SET issuer = 'urn:test-local-idp',
    certificate = $$
$(cat /tmp/test-local-idp.crt)
$$,
    metadata_url = NULL,
    sso_login_url = 'http://localhost:8080/sso'
WHERE id = 1
RETURNING id;
SQL

PGPASSWORD=root psql -h 127.0.0.1 -U root -p 5432 -d linkbay_dev -f /tmp/update_saml.sql
```

4. Verifica endpoints (usare Host: test-tenant.lvh.me):

```bash
curl -i -H "Host: test-tenant.lvh.me" http://localhost:3001/auth/saml/1/metadata.xml
curl -i -L -H "Host: test-tenant.lvh.me" http://localhost:3001/auth/saml/1
```

Note:
- In locale l'IdP di test può rispondere 410 o comportarsi diversamente; l'importante è che l'app generi correttamente il redirect e i metadata.
- La migration `20250902_add_sso_login_url_to_tenant_saml_providers.ts` è stata aggiunta per creare la colonna `sso_login_url` in modo idempotente.
