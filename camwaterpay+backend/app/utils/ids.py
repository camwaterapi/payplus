import uuid
def new_txn_id(): return uuid.uuid4().hex[:24]
