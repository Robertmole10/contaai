#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="/home/rig/Projects/contaai"
BACKUP_DIR="/mnt/data4tb/backups/contaai/postgres"
LOG_FILE="/mnt/data4tb/backups/contaai/logs/postgres-backup.log"
RETENTION_DAYS=30

TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
BACKUP_FILE="${BACKUP_DIR}/contaai_${TIMESTAMP}.sql.gz"
TEMP_FILE="${BACKUP_FILE}.tmp"

mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

cleanup() {
    rm -f "$TEMP_FILE"
}

trap cleanup EXIT

cd "$PROJECT_DIR"

log "Începe backup-ul PostgreSQL."

docker compose exec -T postgres \
    pg_dump \
    --username="${POSTGRES_USER}" \
    --dbname="${POSTGRES_DB}" \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges \
    | gzip -9 > "$TEMP_FILE"

if ! gzip -t "$TEMP_FILE"; then
    log "EROARE: arhiva generată nu este validă."
    exit 1
fi

mv "$TEMP_FILE" "$BACKUP_FILE"

FILE_SIZE="$(du -h "$BACKUP_FILE" | cut -f1)"
log "Backup creat: $BACKUP_FILE, dimensiune: $FILE_SIZE"

find "$BACKUP_DIR" \
    -type f \
    -name 'contaai_*.sql.gz' \
    -mtime "+${RETENTION_DAYS}" \
    -delete

log "Retenția de ${RETENTION_DAYS} zile a fost aplicată."
log "Backup PostgreSQL finalizat cu succes."
