# db.py
from dotenv import load_dotenv
# load_dotenv → loads environment variables from the .env file
import os
# os → used to access environment variables
from pymongo import MongoClient
# MongoClient → allows connection to MongoDB database
from urllib.parse import quote_plus
# quote_plus → safely encodes special characters in username/password

#load environment variables
load_dotenv()  

#read database credentials
username = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASS")
cluster = os.getenv("MONGO_CLUSTER")
db_name = os.getenv("DB_NAME")

#validation check
if not all([username, password, cluster, db_name]):
    raise EnvironmentError("One or more MongoDB environment variables are missing!")

# Stops the app immediately if any required config is missing

#encode username and password 
username = quote_plus(username)
password = quote_plus(password)

# Build MongoDb URI
uri = f"mongodb+srv://{username}:{password}@{cluster}/{db_name}?retryWrites=true&w=majority"

# Connect to MongoDB
client = MongoClient(uri)

# Get the database
db = client[db_name]

# Get the collection
messages_collection = db["messages"]


print(f"Connected to MongoDB database: {db_name}")