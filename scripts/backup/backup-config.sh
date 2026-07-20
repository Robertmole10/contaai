#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="/home/rig/Projects/contaai"
BACKUP_DIR="/mnt/data4tb/backups/contaai/config"
LOG_DIR="/mnt/data4tb/backups/contaai/logs"
RETENTION_DAYS=30

DATE="$(date -u +"%Y-%m-%d_%H-%M-%S")"
VERSION="$(tr -d '[:space:]' < "$PROJECT_DIR/VERSION")"

ARCHIVE_NAME="contaai-config-${VERSION}-${DATE}.tar.zst"
ARCHIVE_PATH="$BACKUP_DIR/$ARCHIVE_NAME"
CHECKSUM_PATH="${ARCHIVE_PATH}.sha256"
LOG_FILE="$LOG_DIR/backup-config.log"

log() {
    local message="$1"
    printf '[%s] %s\n' "$(date -u +"%Y-%m-%d %H:%M:%S UTC")" "$message" \
        | tee -a "$LOG_FILE"
}

cleanup_partial_backup() {
    rm -f "$ARCHIVE_PATH" "$CHECKSUM_PATH"
}

on_error() {
    local exit_code=$?
    log "EROARE: backup-ul configurației a eșuat cu codul $exit_code."
    cleanup_partial_backup
    exit "$exit_code"
}

trap on_error ERR

mkdir -p "$BACKUP_DIR" "$LOG_DIR"

if [[ ! -d "$PROJECT_DIR" ]]; then
    log "EROARE: directorul proiectului nu există: $PROJECT_DIR"
    exit 1
fi

if [[ ! -f "$PROJECT_DIR/VERSION" ]]; then
    log "EROARE: fișierul VERSION nu există."
    exit 1
fi

if ! command -v tar >/dev/null 2>&1; then
    log "EROARE: comanda tar nu este instalată."
    exit 1
fi

if ! command -v zstd >/dev/null 2>&1; then
    log "EROARE: comanda zstd nu este instalată."
    exit 1
fi

if ! command -v sha256sum >/dev/null 2>&1; then
    log "EROARE: comanda sha256sum nu este disponibilă."
    exit 1
fi

log "======================================="
log "Pornire backup configurație ContaAI"
log "Versiune: $VERSION"
log "Arhivă: $ARCHIVE_NAME"

tar \
    --directory="$(dirname "$PROJECT_DIR")" \
    --exclude='contaai/.git' \
    --exclude='contaai/node_modules' \
    --exclude='contaai/**/node_modules' \
    --exclude='contaai/.next' \
    --exclude='contaai/**/.next' \
    --exclude='contaai/__pycache__' \
    --exclude='contaai/**/__pycache__' \
    --exclude='contaai/.pytest_cache' \
    --exclude='contaai/**/.pytest_cache' \
    --exclude='contaai/.mypy_cache' \
    --exclude='contaai/**/.mypy_cache' \
    --exclude='contaai/.ruff_cache' \
    --exclude='contaai/**/.ruff_cache' \
    --exclude='contaai/*.pyc' \
    --exclude='contaai/**/*.pyc' \
    --exclude='contaai/*.pyo' \
    --exclude='contaai/**/*.pyo' \
    --exclude='contaai/logs' \
    --exclude='contaai/**/logs' \
    --exclude='contaai/backups' \
    --exclude='contaai/**/backups' \
    --exclude='contaai/.DS_Store' \
    --exclude='contaai/**/.DS_Store' \
    --exclude='contaai/.env.local' \
    --exclude='contaai/**/.env.local' \
    --exclude='contaai/*.backup-*' \
    --exclude='contaai/**/*.backup-*' \
    --use-compress-program='zstd -T0 -10' \
    --create \
    --file="$ARCHIVE_PATH" \
    "$(basename "$PROJECT_DIR")"

log "Arhiva a fost creată."

zstd --test "$ARCHIVE_PATH" >/dev/null

log "Verificarea internă zstd a trecut."

(
    cd "$BACKUP_DIR"
    sha256sum "$ARCHIVE_NAME" > "$(basename "$CHECKSUM_PATH")"
    sha256sum --check "$(basename "$CHECKSUM_PATH")" >/dev/null
)

log "Checksum SHA-256 creat și verificat."

ARCHIVE_SIZE="$(du -h "$ARCHIVE_PATH" | awk '{print $1}')"
FILE_COUNT="$(
    tar \
        --use-compress-program='zstd -d -q' \
        --list \
        --file="$ARCHIVE_PATH" \
        | wc -l
)"

log "Dimensiune arhivă: $ARCHIVE_SIZE"
log "Intrări arhivate: $FILE_COUNT"

find "$BACKUP_DIR" \
    -maxdepth 1 \
    -type f \
    \( -name 'contaai-config-*.tar.zst' -o -name 'contaai-config-*.tar.zst.sha256' \) \
    -mtime "+$RETENTION_DAYS" \
    -delete

log "Retenția de $RETENTION_DAYS zile a fost aplicată."
log "Backup configurație finalizat cu succes."
