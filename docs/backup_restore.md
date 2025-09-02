# Strategia di Backup e Recupero per l'architettura Multitenant

Questa documentazione descrive come eseguire backup e restore del database in ambiente multitenant (pattern schema-per-tenant). Fornisce anche due script utili: `scripts/backup.sh` e `scripts/restore.sh`.

## Principi generali

- Abbiamo uno schema globale (tipicamente `public`) che contiene le tabelle condivise (es. `tenants`, `users`, `plugins`, ecc.).
- Ogni tenant ha il proprio schema PostgreSQL, chiamato `tenant_<id>` (es. `tenant_42`).
- Strategie di backup raccomandate:
  - Backup giornaliero completo (full) per disaster recovery.
  - Backup incrementali/solo-global per cambi frequenti nelle tabelle globali.
  - Backup per-schema (per-tenant) per ripristini di singoli tenant o per esportazioni.
  - Conservazione dei backup in storage esterno durevole (S3) con versioning e ciclo di retention.

## Script inclusi

- `scripts/backup.sh` — crea dump PostgreSQL secondo diverse modalità:
  - `full` — dump completo in formato custom (consigliato per restore totali)
  - `global` — dump SQL in formato plain delle tabelle globali (esclude schemi `tenant_*`)
  - `tenants-schemas` — esegue il dump di ogni schema tenant_<id> separatamente (legge gli id dalla tabella `tenants`)
  - `tenant <id>` — dump dello schema `tenant_<id>`

- `scripts/restore.sh` — ripristina dump creati con `backup.sh`:
  - `full <file>` — ripristina un dump custom (usa `pg_restore --clean`)
  - `tenant <id> <file>` — ripristina il singolo schema tenant (elimina e ricrea lo schema prima del restore)
  - `sqlfile <file>` — applica un file SQL plain (`.sql` o `.sql.gz`)

Entrambi gli script usano la variabile d'ambiente `DATABASE_URL` per connettersi al DB. `backup.sh` può caricare i file su S3 se si impostano le variabili `S3_BUCKET` e (opzionale) `S3_PATH`.

## Requisiti

- pg_dump, pg_restore, psql, gzip, gunzip
- AWS CLI configurata (se si vuole il caricamento su S3)
- Variabili d'ambiente:
  - `DATABASE_URL` (es. `postgresql://user:pass@host:5432/dbname`)
  - `S3_BUCKET` opzionale
  - `S3_PATH` opzionale

## Esempi di utilizzo

1) Backup completo locale e upload su S3

```bash
export DATABASE_URL="postgresql://linkbay:secret@db.internal:5432/linkbay_prod"
export S3_BUCKET="my-company-backups"
export S3_PATH="linkbay-cms/prod"
./scripts/backup.sh full
```

Il file sarà creato in `./backups` con suffisso timestamp e caricato su `s3://my-company-backups/linkbay-cms/prod/`.

2) Dump di tutti i tenant separatamente

```bash
export DATABASE_URL="postgresql://linkbay:secret@db.internal:5432/linkbay_prod"
./scripts/backup.sh tenants-schemas
```

Questo crea un file per ogni schema `tenant_<id>` e opzionalmente li carica su S3 se `S3_BUCKET` è impostato.

3) Restore completo (attenzione: sovrascrive lo stato corrente)

```bash
export DATABASE_URL="postgresql://linkbay:secret@db.internal:5432/linkbay_prod"
./scripts/restore.sh full backups/linkbay_full_20250902T120000Z.dump.gz
```

4) Ripristino di un singolo tenant

```bash
export DATABASE_URL="postgresql://linkbay:secret@db.internal:5432/linkbay_prod"
./scripts/restore.sh tenant 42 backups/tenant_42_20250902T120000Z.dump.gz
```

## Raccomandazioni operative

- Automatizzare i backup con cron/cronjobs (k8s CronJob) e inviare notifiche in caso di failure.
- Testare periodicamente i restore (DR drills). Tenere una procedura documentata che includa:
  - Test in un ambiente isolato
  - Verifica dell'integrità dei dati per il tenant ripristinato
  - Validazione delle funzionalità critiche
- Impostare ciclo di retention su S3 (Lifecycle rules) e cifratura lato server (SSE) o lato client.
- Considerare backup PITR (point-in-time recovery) usando WAL archiving o base backups con pg_basebackup per esigenze di RTO/RPO stringenti.

## Note di sicurezza

- Limitare chi può accedere e ripristinare i backup.
- Non memorizzare credenziali in chiaro nei backup (vanno cifrati a riposo su S3).

## Troubleshooting

- "pg_dump: error: connection to server at \"\" failed" — verificare `DATABASE_URL` e che il DB sia raggiungibile.
- "permission denied" durante restore — eseguire il restore con un utente con i permessi necessari, o usare `--no-owner`/`--role` se richiesto.

---

File creati dagli script:

- `backups/` directory (creata localmente dallo script se non esiste)

Se vuoi, posso:
- aggiungere un job di esempio per Kubernetes `CronJob` che usa questi script e carica i log su un bucket S3;
- integrare versioning dei backup con nomi che includono il commit SHA del deploy;
- implementare un meccanismo di rotazione/retention locale prima dell'upload su S3.
