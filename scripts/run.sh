#!/bin/sh

set -e

python -m infrastructure.db.wait_for_db

# start the backup script in the background
if [ "$DEV" != "true" ]; then
  (
    while true; do
      cd /scripts
      ./dump_db.sh || true
      sleep 86400
    done
  ) &
fi
cd /app

alembic upgrade head

exec python main.py
