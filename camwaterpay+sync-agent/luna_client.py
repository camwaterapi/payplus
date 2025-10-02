import os, json, httpx

def env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None: return default
    return str(v).lower() in ("1","true","yes","on")

class LunaClient:
    def __init__(self):
        self.base = os.getenv("LUNA_BASE_URL", "").rstrip("/")
        self.create_url = os.getenv("LUNA_CREATE_URL") or (self.base + "/workorders")
        self.status_url_tmpl = os.getenv("LUNA_STATUS_URL") or (self.base + "/workorders/{id}")
        self.lastread_url_tmpl = os.getenv("LUNA_LASTREAD_URL") or (self.base + "/meters/{meter}/lastreadout")
        self.username = os.getenv("LUNA_USERNAME") or ""
        self.password = os.getenv("LUNA_PASSWORD") or ""
        self.token = os.getenv("LUNA_TOKEN") or ""
        self.amount_field = os.getenv("LUNA_AMOUNT_FIELD","CreditAmount")
        self.client_ref_field = os.getenv("LUNA_CLIENT_REF_FIELD","ClientReference")
        self.status_field = os.getenv("LUNA_STATUS_FIELD","Status")
        self.status_success = os.getenv("LUNA_STATUS_SUCCESS","Successful")
        self.status_waiting = os.getenv("LUNA_STATUS_WAITING","Waiting")
        self.verify_tls = env_bool("VERIFY_TLS", True)
        self.timeout = int(os.getenv("TIMEOUT_SECONDS","20"))

        headers = {"Content-Type":"application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        auth = None if self.token else (self.username, self.password)

        self.client = httpx.Client(timeout=self.timeout, verify=self.verify_tls, headers=headers, auth=auth)

    def create_work_order_load_credit(self, meter_number: str, amount: float, currency: str, txn_id: str) -> str:
        payload = {
            "WorkOrderType": "LoadCredit",
            "MeterNumber": meter_number,
            "WorkOrderInputs": { self.amount_field: amount, "Currency": currency },
            self.client_ref_field: txn_id
        }
        r = self.client.post(self.create_url, json=payload)
        r.raise_for_status()
        data = r.json()
        wo_id = data.get("WorkOrderId") or data.get("id") or data.get("data",{}).get("WorkOrderId")
        if not wo_id:
            raise RuntimeError(f"Cannot parse WorkOrderId from response: {data}")
        return str(wo_id)

    def check_work_order_status(self, work_order_id: str) -> str:
        url = self.status_url_tmpl.format(id=work_order_id)
        r = self.client.get(url)
        r.raise_for_status()
        data = r.json()
        status = data.get(self.status_field) or data.get("status") or data.get("data",{}).get(self.status_field)
        if not status:
            raise RuntimeError(f"Cannot parse status from response: {data}")
        return str(status)

    def get_meter_last_readout(self, meter_number: str) -> dict:
        url = self.lastread_url_tmpl.format(meter=meter_number)
        r = self.client.get(url)
        r.raise_for_status()
        return r.json()
