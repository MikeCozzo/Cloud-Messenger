from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from users import router as users_router
from conversations import router as conversations_router
import os

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

# -------------------- FRONTEND --------------------
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")

# Serve index.html at root
from fastapi.responses import FileResponse

@app.get("/")
def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Serve chat.html
@app.get("/chat.html")
def chat():
    return FileResponse(os.path.join(frontend_path, "chat.html"))

# Mount static assets (JS, CSS, images) under /static
app.mount("/static", StaticFiles(directory=frontend_path), name="static")