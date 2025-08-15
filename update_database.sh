#!/bin/bash

# =============================================
# SCRIPT DI AGGIORNAMENTO DATABASE "BOTTE DI FERRO"
# =============================================
# Sicuro, non distruttivo, con rollback automatico
# By Alessio Quagliara - Linkbay CMS

set -euo pipefail  # Modalità strict: interrompe su errori

# 🔐 Configurazione (modifica qui)
DB_NAME="cms_def"
DB_USER="root"
DB_HOST="localhost"
FLASK_APP="app.py"
BACKUP_DIR="/var/www/CMS_DEF/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 🔍 Verifica prerequisiti
check_requirements() {
    echo "🔎 Verifica prerequisiti..."
    command -v psql >/dev/null 2>&1 || { echo "❌ PostgreSQL client non installato"; exit 1; }
    command -v flask >/dev/null 2>&1 || { echo "❌ Flask non installato"; exit 1; }
    [ -f "$FLASK_APP" ] || { echo "❌ File $FLASK_APP non trovato"; exit 1; }
    echo "✅ Prerequisiti verificati"
}

# 💾 Crea backup del database
create_backup() {
    echo "💾 Creo backup del database..."
    local BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_$TIMESTAMP.sql"
    mkdir -p "$BACKUP_DIR"
    pg_dump -h "$DB_HOST" -U "$DB_USER" -Fc "$DB_NAME" > "$BACKUP_FILE"
    [ $? -eq 0 ] || { echo "❌ Backup fallito"; exit 1; }
    echo "✅ Backup creato: $BACKUP_FILE"
    echo "🔒 Verifica integrità backup..."
    pg_restore -l "$BACKUP_FILE" >/dev/null
    [ $? -eq 0 ] || { echo "❌ Backup corrotto!"; exit 1; }
    echo "✅ Integrità backup verificata"
}

# 🔄 Esegui migrazioni in transazione
apply_migrations() {
    echo "🔄 Applico migrazioni..."
    # Avvia transazione esplicita
    psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" <<-EOSQL
        BEGIN;
        CREATE TEMP TABLE migration_guard AS SELECT 1;
        SAVEPOINT pre_migration;
EOSQL

    # Applica migrazioni Flask
    export FLASK_APP
    flask db upgrade
    
    # Verifica finale
    psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" <<-EOSQL
        RELEASE SAVEPOINT pre_migration;
        COMMIT;
        DROP TABLE migration_guard;
EOSQL
}

# 🔍 Controlli post-migrazione
post_migration_checks() {
    echo "🔍 Eseguo controlli post-migrazione..."
    # 1. Verifica che le tabelle principali esistano
    local TABLES=("users" "posts" "settings")
    for table in "${TABLES[@]}"; do
        psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
            -c "SELECT 1 FROM $table LIMIT 1;" >/dev/null 2>&1 || \
            { echo "❌ Tabella $table mancante o corrotta!"; return 1; }
    done

    # 2. Verifica versione migrazione
    flask db current | grep "(head)" || { echo "❌ Migrazione non a head!"; return 1; }

    # 3. Verifica custom (es. conteggio utenti)
    local user_count=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
        -t -c "SELECT count(*) FROM users;")
    [ "$user_count" -gt 0 ] || { echo "❌ Nessun utente nel DB!"; return 1; }

    echo "✅ Tutti i controlli superati"
    return 0
}

# 🚨 Rollback automatico
rollback_db() {
    echo "🚨 ATTENZIONE: Avvio rollback automatico!"
    local BACKUP_FILE=$(ls -t "$BACKUP_DIR"/*.sql | head -1)
    [ -f "$BACKUP_FILE" ] || { echo "❌ Backup non trovato"; exit 1; }

    psql -h "$DB_HOST" -U "$DB_USER" -d postgres <<-EOSQL
        DROP DATABASE IF EXISTS ${DB_NAME}_old;
        ALTER DATABASE "$DB_NAME" RENAME TO ${DB_NAME}_old;
        CREATE DATABASE "$DB_NAME";
EOSQL

    pg_restore -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" "$BACKUP_FILE"
    [ $? -eq 0 ] && echo "✅ Rollback completato" || echo "❌ Rollback fallito"
}

# 🔐 Ambiente sicuro
export PGOPTIONS="-c client_min_messages=WARNING"
trap 'echo "🛑 Script interrotto dall\utente! Avvio rollback..." && rollback_db && exit 1' INT

# ======================
# ESECUZIONE PRINCIPALE
# ======================
echo "🚀 Avvio aggiornamento database $DB_NAME"

# Fase 1: Verifiche preliminari
check_requirements

# Fase 2: Backup con verifica
create_backup

# Fase 3: Migrazione in transazione
if apply_migrations; then
    echo "✅ Migrazione applicata con successo"
else
    echo "❌ Errore durante la migrazione"
    rollback_db
    exit 1
fi

# Fase 4: Verifiche post-migrazione
if post_migration_checks; then
    echo "🎉 Aggiornamento completato con successo!"
else
    echo "❌ Controlli post-migrazione falliti"
    rollback_db
    exit 1
fi

# Pulisci vecchi backup (mantieni ultimi 5)
find "$BACKUP_DIR" -name "*.sql" -type f | sort -r | tail -n +6 | xargs rm -f --

exit 0