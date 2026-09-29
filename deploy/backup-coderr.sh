#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="/var/backups/coderr"
MEDIA_DIR="/var/www/coderr/backend/media"
KEEP_DAYS=14
STAMP="$(date +%F_%H%M)"

mkdir -p "$BACKUP_DIR"
sudo -u postgres pg_dump coderr | gzip > "$BACKUP_DIR/db-$STAMP.sql.gz"

if [ -d "$MEDIA_DIR" ] && [ -n "$(ls -A "$MEDIA_DIR" 2>/dev/null)" ]; then
    tar -czf "$BACKUP_DIR/media-$STAMP.tar.gz" -C /var/www/coderr/backend media
fi

find "$BACKUP_DIR" -name "*.gz" -mtime +"$KEEP_DAYS" -delete
echo "Backup abgeschlossen: $STAMP"
