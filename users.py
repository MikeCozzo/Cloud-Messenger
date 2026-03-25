# users.py
from fastapi import APIRouter
from pydantic import BaseModel
from db import db
from datetime import datetime
import bcrypt

router = APIRouter()

class UserAuth(BaseModel):
    username: str
    password: str

# -------------------- REGISTER --------------------
@router.post("/register")
def register_user(user: UserAuth):
    if db.users.find_one({"username": user.username}):
        return {"error": "User already exists"}

    try:
        password_hash = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
        password_hash_str = password_hash.decode("utf-8")

        db.users.insert_one({
            "username": user.username,
            "password_hash": password_hash_str,
            "created_at": datetime.utcnow()
        })
        return {"status": "User created"}

    except Exception as e:
        return {"error": str(e)}

# -------------------- LOGIN --------------------
@router.post("/login")
def login_user(user: UserAuth):
    existing_user = db.users.find_one({"username": user.username})
    if not existing_user:
        return {"error": "User not found"}

    stored_hash = existing_user["password_hash"].encode("utf-8")
    if bcrypt.checkpw(user.password.encode("utf-8"), stored_hash):
        return {"status": "Login successful"}
    return {"error": "Incorrect password"}

# -------------------- LIST USERS --------------------
@router.get("/users")
def get_users():
    return list(db.users.find({}, {"_id": 0, "username": 1}))