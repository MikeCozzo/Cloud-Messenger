from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from users import router as users_router
from conversations import router as conversations_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users_router)
app.include_router(conversations_router)


@app.get("/status")
def status():
    return {"message": "Messenger backend is running"}


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")