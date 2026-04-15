from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from users import router as users_router
from conversations import router as conversations_router
from db import db

app = FastAPI(title="Messenger App Backend")

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- API ROUTES --------------------
app.include_router(users_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")

# -------------------- HEALTH CHECK --------------------
@app.get("/status")
def status():
    return {"message": "Messenger backend is running"}

# -------------------- WEBSOCKET CONNECTIONS --------------------
active_connections = {}

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    active_connections[username] = websocket

    print(f"User connected: {username}")

    try:
        while True:
            data = await websocket.receive_json()

            receiver = data.get("to")
            message_text = data.get("text")

            if not receiver or not message_text:
                continue

            message_obj = {
                "sender": username,
                "text": message_text,
                "timestamp": datetime.utcnow()
            }

            # ---------------- SAVE TO MONGODB ----------------
            result = db.conversations.update_one(
                {"participants": {"$all": [username, receiver]}},
                {"$push": {"messages": message_obj}}
            )

            if result.matched_count == 0:
                db.conversations.insert_one({
                    "participants": [username, receiver],
                    "messages": [message_obj]
                })

            # ---------------- SEND TO RECEIVER IF ONLINE ----------------
            if receiver in active_connections:
                try:
                    await active_connections[receiver].send_json(message_obj)
                except:
                    pass

    except WebSocketDisconnect:
        print(f"User disconnected: {username}")
        active_connections.pop(username, None)

    except Exception as e:
        print("WebSocket error:", e)
        active_connections.pop(username, None)

# -------------------- FRONTEND --------------------
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")