#!/usr/bin/env bash
# Restore probe for the Coderr database. Loads one backup into a throwaway
# database, checks it against the live database and drops it again.
# The live database is only read, never written.
#   ssh vps "bash -s -- <path to .sql.gz>" < restore_probe.sh
set -euo pipefail

APP_DIR=/var/www/coderr/backend
TEST_DB=coderr_restore_test

backup="${1:-}"
if [ ! -r "$backup" ]; then
    echo "Usage: restore_probe.sh <readable .sql.gz backup>" >&2
    exit 1
fi

# Never add "set -x" to this script: it would print the database password.
env_value() {
    local value
    value="$(grep -m1 "^$1=" .env | cut -d= -f2- | tr -d "\r\"'")" || true
    if [ -z "$value" ]; then
        echo "$1 is missing in .env" >&2
        exit 1
    fi
    printf '%s' "$value"
}

cd "$APP_DIR"
live_db="$(env_value DB_NAME)"
PGHOST="$(env_value DB_HOST)"
PGPORT="$(env_value DB_PORT)"
PGUSER="$(env_value DB_USER)"
PGPASSWORD="$(env_value DB_PASSWORD)"
export PGHOST PGPORT PGUSER PGPASSWORD

if [ "$live_db" = "$TEST_DB" ]; then
    echo "The test database name equals the live database, aborting." >&2
    exit 1
fi

sql() {
    psql -X -At -v ON_ERROR_STOP=1 -d "$1" -c "$2"
}

if [ "$(sql "$live_db" "select count(*) from pg_database where datname = '$TEST_DB'")" != "0" ]; then
    echo "$TEST_DB already exists and is left untouched, aborting." >&2
    exit 1
fi

created=0
errors="$(mktemp)"
cleanup() {
    rm -f "$errors"
    if [ "$created" = 1 ]; then
        dropdb --if-exists "$TEST_DB" && echo "--- Dropped $TEST_DB ---"
    fi
}
trap cleanup EXIT

echo "Backup: $backup ($(du -h "$backup" | cut -f1))"
echo "Live:   $live_db, PostgreSQL $(sql "$live_db" 'show server_version')"

createdb "$TEST_DB"
created=1

started=$SECONDS
if ! gunzip -c "$backup" | psql -X -q -v ON_ERROR_STOP=1 -d "$TEST_DB" >/dev/null 2>"$errors"; then
    echo "--- Restore FAILED ---"
    cat "$errors"
    exit 1
fi
echo "--- Restore finished in $((SECONDS - started)) s, messages below (empty is good) ---"
cat "$errors"

# Exact counts: n_live_tup in pg_stat_user_tables is only an estimate.
count_rows() {
    sql "$1" "select c.relname || ' ' || (xpath('/row/n/text()', query_to_xml(
                  format('select count(*) as n from %I.%I', n.nspname, c.relname), false, true, '')))[1]
              from pg_class c join pg_namespace n on n.oid = c.relnamespace
              where c.relkind = 'r' and n.nspname = 'public'" | LC_ALL=C sort
}

echo "--- Row counts: table, backup, live ---"
LC_ALL=C join -a1 -a2 -e missing -o 0,1.2,2.2 \
    <(count_rows "$TEST_DB") <(count_rows "$live_db") \
    | awk '{ printf "%-45s %8s %8s%s\n", $1, $2, $3, ($2 == $3 ? "" : "  <- differs") }'

# A sequence below the highest id makes the next insert fail with a
# duplicate key, which a row count alone would never reveal.
echo "--- Sequences behind their table (empty is good) ---"
sql "$TEST_DB" "
    select t.tbl || '.' || t.col || ' max=' || t.max_id || ' seq=' || coalesce(t.seq_value::text, 'unused')
    from (
        select format('%I.%I', n.nspname, c.relname) as tbl,
               a.attname as col,
               (xpath('/row/m/text()', query_to_xml(
                   format('select max(%I) as m from %I.%I', a.attname, n.nspname, c.relname),
                   false, true, '')))[1]::text::bigint as max_id,
               pg_sequence_last_value(
                   pg_get_serial_sequence(format('%I.%I', n.nspname, c.relname), a.attname)::regclass
               ) as seq_value
        from pg_attribute a
        join pg_class c on c.oid = a.attrelid
        join pg_namespace n on n.oid = c.relnamespace
        where n.nspname = 'public' and c.relkind = 'r' and a.attnum > 0 and not a.attisdropped
          and pg_get_serial_sequence(format('%I.%I', n.nspname, c.relname), a.attname) is not null
    ) t
    where coalesce(t.max_id, 0) > coalesce(t.seq_value, 0)"

# load_dotenv() does not override variables that are already set, so this
# points Django at the restored copy while everything else comes from .env.
echo "--- Migrations the deployed code would still apply to the copy ---"
DB_NAME="$TEST_DB" .venv/bin/python manage.py migrate --plan
