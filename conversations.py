from fastapi import APIRouter, Query
from db import db
from datetime import datetime

router = APIRouter()

# -------------------------
# GET MESSAGE HISTORY
# -------------------------
@router.get("/messages")
def get_messages(user1: str = Query(...), user2: str = Query(...)):
    convo = db.conversations.find_one(
        {"participants": {"$all": [user1, user2]}},
        {"_id": 0}
    )

    if not convo:
        return []

    messages = convo.get("messages", [])

    # convert datetime → string for JSON
    for m in messages:
        if isinstance(m.get("timestamp"), datetime):
            m["timestamp"] = m["timestamp"].isoformat()

    return messages