#!/bin/sh
set -e

if [ -f /app/.env ]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' /app/.env | xargs -d '\n' -I {} echo {} | xargs)
fi

MODE=${SYNC_MODE:-daemon}

if [ "$MODE" = "cron" ]; then
  echo "Starting cron mode..."
  touch /var/log/cron.log || true
  chmod 0644 /etc/cron.d/sync
  crontab /etc/cron.d/sync
  exec cron -f
elif [ "$MODE" = "once" ]; then
  echo "Running once..."
  exec python3 /app/sync_agent.py --once
else
  echo "Running daemon..."
  exec python3 /app/sync_agent.py
fi
