from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
# FastAPI → main framework for building API
# WebSocket → enables real-time messaging connections
# WebSocketDisconnect → handles user disconnect events
# Query → used for required URL query parameters

from fastapi.staticfiles import StaticFiles
# Serves frontend files (HTML/CSS/JS) from a directory
from fastapi.middleware.cors import CORSMiddleware
# Enables cross-origin requests (frontend ↔ backend communication)

from datetime import datetime
# Used to timestamp messages

# Import routers (modular API routes)
from users import router as users_router
from conversations import router as conversations_router

from db import db
# Import database connection

#CREATE FASTAPI APP
app = FastAPI(title="Messenger App Backend")

# Cors configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(users_router, prefix="/api")
# Adds user-related endpoints under /api/users, etc.
app.include_router(conversations_router, prefix="/api")
# Adds conversation-related endpoints under /api

# status check endpoint
@app.get("/status")
def status():
    return {"message": "Messenger backend is running"}

# get messages endpoint
@app.get("/messages")
def get_messages(user1: str = Query(...), user2: str = Query(...)):
    convo = db.conversations.find_one({
        "participants": {"$all": [user1, user2]}
    })

    if not convo:
        return []

    return convo.get("messages", [])

#WEBSOCKET CONNECTIONS

# Stores active users and their WebSocket connections
active_connections = {}

# WebSocket route for real-time chat
@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
     # Accept incoming WebSocket connection
    await websocket.accept()
     # Store connection so we can send messages later
    active_connections[username] = websocket

    print(f"User connected: {username}")

    try:
         # Keep connection alive and listen for messages
        while True:
               # Receive JSON message from frontend
            data = await websocket.receive_json()

            receiver = data.get("to")
            message_text = data.get("text")
            #ignore invalid messages
            if not receiver or not message_text:
                continue

             # Create message object
            message_obj = {
                "sender": username,
                "text": message_text,
                "timestamp": datetime.utcnow().isoformat()
            }

            # SAVE TO MONGODB

             # Try to update existing conversation
            result = db.conversations.update_one(
                {"participants": {"$all": [username, receiver]}},
                {"$push": {"messages": message_obj}}
            )
             # If no conversation exists, create one
            if result.matched_count == 0:
                db.conversations.insert_one({
                    "participants": [username, receiver],
                    "messages": [message_obj]
                })

            # REALTIME MESSAGE DELIVERY

            # If receiver is online, send message instantly
            if receiver in active_connections:
                try:
                    await active_connections[receiver].send_json(message_obj)
                except:
                     # If sending fails, ignore error
                    pass
    #handle user disconnect         
    except WebSocketDisconnect:
        print(f"User disconnected: {username}")
        active_connections.pop(username, None)
  # Handle unexpected errors
    except Exception as e:
        print("WebSocket error:", e)
        active_connections.pop(username, None)

# SERVE FRONTEND FILES
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")