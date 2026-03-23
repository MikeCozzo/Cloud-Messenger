# conversations.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from db import db
from datetime import datetime

router = APIRouter()

active_connections = {}

@router.get("/conversations/{username}/{other_user}")
def get_conversation(username: str, other_user: str):

    conv = db.conversations.find_one(
        {"participants": {"$all": [username, other_user]}},
        {"_id": 0}
    )

    if not conv:
        return {"participants": [username, other_user], "messages": []}

    return conv



@router.get("/conversations/{username}")
def get_user_conversations(username: str):

    convs = db.conversations.find(
        {"participants": username},
        {"_id": 0}
    )

    return list(convs)


@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):

    await websocket.accept()
    active_connections[username] = websocket

    try:
        while True:

            data = await websocket.receive_json()

            receiver = data["to"]
            message_text = data["text"]

            conversation = db.conversations.find_one({
                "participants": {"$all": [username, receiver]}
            })

            message_obj = {
                "sender": username,
                "text": message_text,
                "timestamp": datetime.utcnow().isoformat(),
                "delivered": False
            }

            if conversation:
                db.conversations.update_one(
                    {"participants": {"$all": [username, receiver]}},
                    {"$push": {"messages": message_obj}}
                )
            else:
                db.conversations.insert_one({
                    "participants": [username, receiver],
                    "messages": [message_obj]
                })

            if receiver in active_connections:
                await active_connections[receiver].send_json(message_obj)

    except WebSocketDisconnect:
        if username in active_connections:
            del active_connections[username]