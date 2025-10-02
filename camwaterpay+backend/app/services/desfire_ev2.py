# TEMPLATE ONLY — replace with real EV2 crypto using vendor spec + HSM
from dataclasses import dataclass
from typing import Optional, Dict
from app.utils.card_profile import CardProfile

PROFILE = CardProfile.load()
AID_HEX = PROFILE.aid if PROFILE else "A0000001"
FILENO_VALUE = PROFILE.value_file if PROFILE else 1
FILENO_LEDGER = PROFILE.ledger_file if PROFILE else 2
KEYNO_WRITE = PROFILE.keyno_write if PROFILE else 1
KEYNO_READ  = PROFILE.keyno_read if PROFILE else 0

@dataclass
class EV2Session:
    uid: str
    txn_id: str
    stage: str = "SELECT"
    k_ses_enc: Optional[bytes] = None
    k_ses_mac: Optional[bytes] = None
    ti: Optional[bytes] = None
    cmd_ctr: int = 0

def _iso(cla:int, ins:int, p1:int, p2:int, data:bytes=b"", le:int|None=None)->bytes:
    apdu = bytes([cla,ins,p1,p2,len(data)]) + data
    if le is not None: apdu += bytes([le])
    return apdu

def _hex(b:bytes)->str: return b.hex().upper()

def cmd_select_aid(aid_hex:str)->str:
    return _hex(_iso(0x90,0x5A,0x00,0x00,bytes.fromhex(aid_hex),0x00))

def cmd_auth_ev2_part1(keyno:int)->str:
    return _hex(_iso(0x90,0xAA,0x00,0x00,bytes([keyno]),0x00))

def cmd_auth_ev2_part2(card_chal:bytes)->str:
    host_cryptogram = b"00"  # TODO compute per EV2
    return _hex(_iso(0x90,0xAF,0x00,0x00,host_cryptogram,0x00))

def cmd_increase_value(file_no:int, amount:int)->str:
    data = bytes([file_no]) + amount.to_bytes(4,'big',signed=True)
    return _hex(_iso(0x90,0xC1,0x00,0x00,data,0x00))

def cmd_write_record(file_no:int, record:bytes)->str:
    data = bytes([file_no,0x00,len(record)]) + record
    return _hex(_iso(0x90,0x3B,0x00,0x00,data,0x00))

def cmd_read_value(file_no:int)->str:
    return _hex(_iso(0x90,0x6C,0x00,0x00,bytes([file_no]),0x00))

def cmd_commit()->str:
    return _hex(_iso(0x90,0xC7,0x00,0x00,le=0x00))

def first_apdu_for_session()->str: return cmd_select_aid(AID_HEX)

def next_apdu(sess: EV2Session, card_resp_hex: str, amount_units:int, ledger_blob: bytes) -> Dict:
    if sess.stage == "SELECT":
        sess.stage = "AUTH1"; return {"apdu": cmd_auth_ev2_part1(KEYNO_WRITE)}
    elif sess.stage == "AUTH1":
        sess.stage = "AUTH2"; return {"apdu": cmd_auth_ev2_part2(bytes.fromhex(card_resp_hex))}
    elif sess.stage == "AUTH2":
        sess.stage = "INCREASE"; return {"apdu": cmd_increase_value(FILENO_VALUE, amount_units)}
    elif sess.stage == "INCREASE":
        sess.stage = "WRITE_REC"; return {"apdu": cmd_write_record(FILENO_LEDGER, ledger_blob)}
    elif sess.stage == "WRITE_REC":
        sess.stage = "VERIFY"; return {"apdu": cmd_read_value(FILENO_VALUE)}
    elif sess.stage == "VERIFY":
        sess.stage = "COMMIT"; return {"apdu": cmd_commit()}
    else:
        return {"done": True}
