import os, json, time, sqlite3, re, sys
from pathlib import Path
from dotenv import load_dotenv
from luna_client import LunaClient

load_dotenv()

def env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None: return default
    return str(v).lower() in ("1","true","yes","on")

APP_DB_URL = os.getenv("APP_DB_URL","sqlite:////data/camwater.db")
STATE_PATH = Path(os.getenv("STATE_PATH","/data/state.json"))
SYNC_MODE = os.getenv("SYNC_MODE","daemon")
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL_SECONDS","300"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE","25"))

def sqlite_path_from_url(url: str) -> str:
    m = re.match(r"^sqlite(\+aiosqlite)?:///+(.*)$", url)
    if not m:
        raise SystemExit(f"Only sqlite URLs are supported for now. Got: {url}")
    p = m.group(2)
    return os.path.abspath(p)

def load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {"created": {}, "done": []}

def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.replace(STATE_PATH)

def fetch_used_tuis(sqlite_file: str) -> list:
    con = sqlite3.connect(sqlite_file)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    query = (
        "SELECT tuis.id as tui_id, tuis.txn_id, tuis.amount, tuis.meter_id, tuis.user_id, "
        "topups.currency, meters.meter_number "
        "FROM tuis "
        "JOIN topups ON topups.txn_id = tuis.txn_id "
        "JOIN meters ON meters.id = topups.meter_id "
        "WHERE tuis.status = 'USED' "
        "ORDER BY tuis.id DESC"
    )
    cur.execute(query)
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows

def process_once():
    sqlite_file = sqlite_path_from_url(APP_DB_URL)
    state = load_state()
    created = state.get("created", {})
    done = set(state.get("done", []))

    rows = fetch_used_tuis(sqlite_file)
    candidates = [r for r in rows if r["txn_id"] not in done]
    if not candidates:
        print("No USED TUIs found to sync.")
        return

    client = LunaClient()

    to_create = [r for r in candidates if r["txn_id"] not in created]
    for r in to_create[:BATCH_SIZE]:
        txn_id = r["txn_id"]
        meter = str(r["meter_number"])
        try:
            amount = float(r["amount"])
        except Exception:
            amount = float(str(r["amount"]).replace(",", ""))
        currency = r.get("currency") or "XAF"
        print(f"[create] txn={txn_id} meter={meter} amount={amount} {currency}")
        try:
            wo_id = client.create_work_order_load_credit(meter, amount, currency, txn_id)
            created[txn_id] = str(wo_id)
            state["created"] = created
            save_state(state)
        except Exception as e:
            print(f"  ! create failed: {e}")

    pending = [(tx, wo) for tx,wo in created.items() if tx not in done]
    for txn_id, wo_id in pending[:BATCH_SIZE]:
        print(f"[status] txn={txn_id} wo={wo_id}")
        try:
            st = client.check_work_order_status(wo_id)
            print(f"  status={st}")
            if st.lower() in ("successful","success","completed","complete","ok"):
                done.add(txn_id)
                state["done"] = sorted(done)
                save_state(state)
        except Exception as e:
            print(f"  ! status failed: {e}")

def main():
    if SYNC_MODE == "once":
        process_once()
        return
    if SYNC_MODE == "daemon":
        while True:
            process_once()
            time.sleep(SYNC_INTERVAL)
    if SYNC_MODE == "cron":
        process_once()
        return

if __name__ == "__main__":
    if "--once" in sys.argv:
        process_once()
    else:
        main()
