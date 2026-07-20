#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="/home/rig/Projects/contaai"
BACKUP_ROOT="/mnt/data4tb/backups/contaai/minio"
LOG_FILE="/mnt/data4tb/backups/contaai/logs/minio-backup.log"
RETENTION_DAYS=30
DOCKER_NETWORK="contaai_storage_net"

TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
BACKUP_DIR="${BACKUP_ROOT}/contaai_minio_${TIMESTAMP}"
TEMP_DIR="${BACKUP_DIR}.tmp"

mkdir -p "$BACKUP_ROOT"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

cleanup() {
    rm -rf "$TEMP_DIR"
}

trap cleanup EXIT

cd "$PROJECT_DIR"

if [[ -f "$PROJECT_DIR/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$PROJECT_DIR/.env"
    set +a
fi

required_variables=(
    MINIO_ROOT_USER
    MINIO_ROOT_PASSWORD
    MINIO_BUCKET
)

for variable in "${required_variables[@]}"; do
    if [[ -z "${!variable:-}" ]]; then
        log "EROARE: variabila $variable nu este definită."
        exit 1
    fi
done

if ! docker network inspect "$DOCKER_NETWORK" >/dev/null 2>&1; then
    log "EROARE: rețeaua Docker $DOCKER_NETWORK nu există."
    exit 1
fi

if ! docker compose ps --status running minio | grep -q minio; then
    log "EROARE: containerul MinIO nu rulează."
    exit 1
fi

mkdir -p "$TEMP_DIR"

log "Începe backup-ul MinIO pentru bucket-ul: $MINIO_BUCKET"

docker run --rm \
    --network "$DOCKER_NETWORK" \
    --entrypoint /bin/sh \
    -e MC_CONFIG_DIR=/tmp/.mc \
    -e MINIO_ROOT_USER="$MINIO_ROOT_USER" \
    -e MINIO_ROOT_PASSWORD="$MINIO_ROOT_PASSWORD" \
    -e MINIO_BUCKET="$MINIO_BUCKET" \
    -v "$TEMP_DIR:/backup" \
    minio/mc:latest \
    -c '
        set -eu

        mc alias set contaai \
            http://minio:9000 \
            "$MINIO_ROOT_USER" \
            "$MINIO_ROOT_PASSWORD" >/dev/null

        mc stat "contaai/$MINIO_BUCKET" >/dev/null

        mc mirror \
            --overwrite \
            "contaai/$MINIO_BUCKET" \
            /backup
    '

FILE_COUNT="$(find "$TEMP_DIR" -type f | wc -l)"
TOTAL_SIZE="$(du -sh "$TEMP_DIR" | cut -f1)"

cat > "$TEMP_DIR/backup-info.txt" <<EOF
timestamp=${TIMESTAMP}
bucket=${MINIO_BUCKET}
file_count=${FILE_COUNT}
total_size=${TOTAL_SIZE}
source=http://minio:9000/${MINIO_BUCKET}
EOF

mv "$TEMP_DIR" "$BACKUP_DIR"

log "Backup creat: $BACKUP_DIR"
log "Fișiere salvate: $FILE_COUNT"
log "Dimensiune totală: $TOTAL_SIZE"

find "$BACKUP_ROOT" \
    -mindepth 1 \
    -maxdepth 1 \
    -type d \
    -name 'contaai_minio_*' \
    -mtime "+${RETENTION_DAYS}" \
    -exec rm -rf {} +

log "Retenția de ${RETENTION_DAYS} zile a fost aplicată."
log "Backup MinIO finalizat cu succes."
