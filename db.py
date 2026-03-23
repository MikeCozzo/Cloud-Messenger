# db.py
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from urllib.parse import quote_plus


load_dotenv()  


username = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASS")
cluster = os.getenv("MONGO_CLUSTER")
db_name = os.getenv("DB_NAME")


if not all([username, password, cluster, db_name]):
    raise EnvironmentError("One or more MongoDB environment variables are missing!")

# URL-encode username and password 
username = quote_plus(username)
password = quote_plus(password)

# Build MongoDB URI
uri = f"mongodb+srv://{username}:{password}@{cluster}/{db_name}?retryWrites=true&w=majority"

# Connect to MongoDB
client = MongoClient(uri)

# Get the database
db = client[db_name]

# Get the messages collection
messages_collection = db["messages"]

# Optional: print confirmation
print(f"Connected to MongoDB database: {db_name}")