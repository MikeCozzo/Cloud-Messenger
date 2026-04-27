#imports
from fastapi import APIRouter, Query
# APIRouter → lets us create grouped API routes (modular backend structure)
# Query → used to define required query parameters (?user1=...&user2=...)
from db import db
# db → your database connection
from datetime import datetime
# datetime → used to detect and convert timestamps for JSON responses

#create router
router = APIRouter()

#message history endpoint
@router.get("/messages")
def get_messages(user1: str = Query(...), user2: str = Query(...)):
    convo = db.conversations.find_one(
        {"participants": {"$all": [user1, user2]}},
        {"_id": 0}
    )

    if not convo:
        return []

    messages = convo.get("messages", [])

#MongoDB stores datetime objects which are NOT JSON serializable So we convert them into ISO string format
    for m in messages:
        if isinstance(m.get("timestamp"), datetime):
            m["timestamp"] = m["timestamp"].isoformat()

# quote_plus → safely encodes special characters in username/password
    return messages