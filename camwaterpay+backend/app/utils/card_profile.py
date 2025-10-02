import json
from dataclasses import dataclass
from app.core.config import settings

@dataclass
class CardProfile:
    aid: str
    value_file: int
    ledger_file: int
    keyno_write: int
    keyno_read: int
    decimals: int = 0

    @classmethod
    def load(cls):
        if not settings.LUNA_CARD_PROFILE_JSON: return None
        d = json.loads(settings.LUNA_CARD_PROFILE_JSON)
        return cls(d.get('aid',''), int(d.get('value_file',1)), int(d.get('ledger_file',2)),
                   int(d.get('keyno_write',1)), int(d.get('keyno_read',0)), int(d.get('decimals',0)))
