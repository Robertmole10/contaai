#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="/home/rig/Projects/contaai"
BACKUP_BASE="/mnt/data4tb/backups/contaai"
LOG_DIR="$BACKUP_BASE/logs"
LOG_FILE="$LOG_DIR/backup-weekly.log"

POSTGRES_SCRIPT="$PROJECT_DIR/scripts/backup/backup-postgres.sh"
MINIO_SCRIPT="$PROJECT_DIR/scripts/backup/backup-minio.sh"
CONFIG_SCRIPT="$PROJECT_DIR/scripts/backup/backup-config.sh"

START_TIME="$(date +%s)"

mkdir -p "$LOG_DIR"

log() {
    printf '[%s] %s\n' \
        "$(date -u +"%Y-%m-%d %H:%M:%S UTC")" \
        "$1" | tee -a "$LOG_FILE"
}

run_backup() {
    local name="$1"
    local script="$2"

    if [[ ! -x "$script" ]]; then
        log "EROARE: scriptul $name nu există sau nu este executabil: $script"
        return 1
    fi

    log "Pornire etapă: $name"

    if "$script" 2>&1 | tee -a "$LOG_FILE"; then
        log "Etapa $name finalizată cu succes."
    else
        local exit_code=${PIPESTATUS[0]}
        log "EROARE: etapa $name a eșuat cu codul $exit_code."
        return "$exit_code"
    fi
}

on_error() {
    local exit_code=$?
    local end_time duration

    end_time="$(date +%s)"
    duration="$((end_time - START_TIME))"

    log "Backup-ul săptămânal a eșuat."
    log "Durată până la eroare: ${duration} secunde."
    exit "$exit_code"
}

trap on_error ERR

log "======================================="
log "Pornire backup săptămânal ContaAI"
log "Hostname: $(hostname)"
log "Versiune: $(tr -d '[:space:]' < "$PROJECT_DIR/VERSION")"

run_backup "PostgreSQL" "$POSTGRES_SCRIPT"
run_backup "MinIO" "$MINIO_SCRIPT"
run_backup "Configurație" "$CONFIG_SCRIPT"

END_TIME="$(date +%s)"
DURATION="$((END_TIME - START_TIME))"

log "Toate etapele au fost finalizate cu succes."
log "Durată totală: ${DURATION} secunde."
log "Backup săptămânal ContaAI finalizat."
