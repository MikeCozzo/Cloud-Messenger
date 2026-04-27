# users.py
from fastapi import APIRouter
# APIRouter → lets us group user-related API endpoints (/register, /login, /users)

from pydantic import BaseModel
# BaseModel → defines structure + validation for incoming request data
from db import db
# db → MongoDB connection (used to access users collection)
from datetime import datetime
# datetime → used to store account creation time

import bcrypt
# bcrypt → securely hashes passwords and verifies them

#CREATE ROUTER
router = APIRouter()

#data model
class UserAuth(BaseModel):
    username: str
    password: str

# register endpoint
@router.post("/register")
def register_user(user: UserAuth):
    if db.users.find_one({"username": user.username}):
        return {"error": "User already exists"}

    try:
        #password hashing to secure format (bcrypt)
        password_hash = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
        password_hash_str = password_hash.decode("utf-8")

        #store users in database
        db.users.insert_one({
            "username": user.username,
            "password_hash": password_hash_str,
            "created_at": datetime.utcnow()
        })
        return {"status": "User created"}

    except Exception as e:
        #catch any database or hashing errors
        return {"error": str(e)}

# login endpoint
@router.post("/login")
#look up user in database
def login_user(user: UserAuth):
    existing_user = db.users.find_one({"username": user.username})
    #if user does not exist, return error
    if not existing_user:
        return {"error": "User not found"}
# Get stored hashed password and convert back to bytes
    stored_hash = existing_user["password_hash"].encode("utf-8")
    # Compare entered password with stored hash
    if bcrypt.checkpw(user.password.encode("utf-8"), stored_hash):
        return {"status": "Login successful"}
     # If password doesn't match
    return {"error": "Incorrect password"}

# get all users endpoint
@router.get("/users")
def get_users():
    # Fetch all users from database
    # {"_id": 0} → removes MongoDB internal ID from response
    # {"username": 1} → only return username field
    return list(db.users.find({}, {"_id": 0, "username": 1}))