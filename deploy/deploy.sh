#!/usr/bin/env bash
# Deploys one commit of the Coderr backend. Runs on the server and is fed
# through ssh by the deploy job in .github/workflows/ci.yml:
#   ssh <host> "bash -s -- <commit-sha>" < deploy/deploy.sh
#
# First version: dry run only. It reports what a deployment would change
# and takes a database backup, but touches neither code nor database.
set -euo pipefail

APP_DIR=/var/www/coderr/backend
BACKUP_DIR="$HOME/backups/coderr"
KEEP_BACKUPS=10

sha="${1:-}"
if [[ ! "$sha" =~ ^[0-9a-f]{40}$ ]]; then
    echo "Usage: deploy.sh <full commit sha>" >&2
    exit 1
fi

# Never add "set -x" to this script: it would print the database password
# into the public log of the workflow run.
env_value() {
    local value
    value="$(grep -m1 "^$1=" .env | cut -d= -f2- | tr -d "\r\"'")" || true
    if [ -z "$value" ]; then
        echo "$1 is missing in .env" >&2
        exit 1
    fi
    printf '%s' "$value"
}

backup_database() {
    local db_name db_user db_password db_host db_port file
    db_name="$(env_value DB_NAME)"
    db_user="$(env_value DB_USER)"
    db_password="$(env_value DB_PASSWORD)"
    db_host="$(env_value DB_HOST)"
    db_port="$(env_value DB_PORT)"
    file="$BACKUP_DIR/$(date +%Y-%m-%d_%H%M%S)_${sha:0:7}.sql.gz"

    mkdir -p "$BACKUP_DIR"
    chmod 700 "$HOME/backups"
    rm -f "$BACKUP_DIR"/*.partial
    PGPASSWORD="$db_password" pg_dump -h "$db_host" -p "$db_port" \
        -U "$db_user" "$db_name" | gzip > "$file.partial"
    mv "$file.partial" "$file"
    echo "Backup: $file ($(du -h "$file" | cut -f1))"

    ls -1t "$BACKUP_DIR"/*.sql.gz | tail -n +$((KEEP_BACKUPS + 1)) \
        | xargs -r rm --
}

cd "$APP_DIR"

# Tracked files edited by hand on the server would get mixed with the new
# commit. Stop and name them instead.
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "Tracked files were changed on the server:" >&2
    git status --short --untracked-files=no >&2
    exit 1
fi

git fetch --quiet origin
git cat-file -e "$sha^{commit}"
echo "Server: $(git log --oneline -1 HEAD)"
echo "Target: $(git log --oneline -1 "$sha")"

if ! git merge-base --is-ancestor HEAD "$sha"; then
    echo "Target does not build on the server's commit." >&2
    exit 1
fi

echo "--- Changed files ---"
git diff --stat HEAD "$sha"
echo "--- New migration files ---"
git diff --name-only --diff-filter=A HEAD "$sha" -- '*/migrations/*.py'
echo "--- Changes to requirements.txt ---"
git diff HEAD "$sha" -- requirements.txt
echo "--- Unapplied migrations of the running code ---"
.venv/bin/python manage.py migrate --plan

backup_database
echo "Dry run finished, nothing was deployed."
