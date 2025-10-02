# Camwater PAY+ — LUNA Sync Agent (Python + Dockerfile + cron)

Run in **Card-Only Mode** and sync completed top-ups to **LUNA OASYS** in the background — with **no changes** to your existing app.

## What it does
- Scans your backend DB (SQLite) for TUIs marked **USED** (card write succeeded).
- Creates a **LoadCredit** work order in LUNA OASYS for each unsynced txn.
- Polls until **Successful**.
- Persists idempotent state in `/data/state.json` so nothing is double-sent.

## Quick start (Docker, daemon mode)
```bash
cp .env.example .env
# edit .env: APP_DB_URL, LUNA_* creds/urls
docker compose up -d --build
docker logs -f camwater-sync-agent
```

## Cron mode (inside container)
```bash
# in .env set: SYNC_MODE=cron
docker compose up -d --build
# job runs every 5 minutes as defined in cron/sync
```

## Host cron alternative (no cron in container)
```cron
*/5 * * * * cd /path/to/camwater-sync-agent && docker run --rm --env-file .env -v $(pwd)/data:/data --name camwater-sync-agent camwater-sync-agent:latest python3 /app/sync_agent.py --once
```

## Configuration (.env)
- `APP_DB_URL` — e.g., `sqlite:////data/camwater.db` (mount your backend DB file read-only).
- `LUNA_BASE_URL` + `LUNA_USERNAME`/`LUNA_PASSWORD` (or `LUNA_TOKEN` for bearer auth).
- Optional field overrides if your server differs (`LUNA_AMOUNT_FIELD`, `LUNA_CLIENT_REF_FIELD`, etc.).
- `SYNC_MODE` = `daemon|cron|once`.

## Binding the backend DB
If your backend stores SQLite at `backend/camwater.db`:
```yaml
# docker-compose.yml
volumes:
  - ../backend/camwater.db:/data/camwater.db:ro
```

## Notes
- Defaults assume **REST-style** OASYS endpoints. If you use SOAP, adapt `luna_client.py` (or expose a tiny REST facade).
- The agent only **reads** your DB; it persists sync state in `/data/state.json` in its own volume.
- Idempotency: each `txn_id` is sent once; progress survives restarts.

## Test run
1) Ensure your app has at least one TUI with status `USED` (after a successful card write).
2) Start the agent (`daemon` mode).
3) Watch logs for `[create] ...` then `[status] ... status=Successful`.
4) Confirm the work order in OASYS.
