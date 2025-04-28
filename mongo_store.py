import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_DB_URI")
DB_NAME = os.getenv("MONGODB_DB")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

tickets_collection = db["tickets"]
users_collection = db["users"]

print(f"[DEBUG] Connected to MongoDB database: {db.name}")
print(f"[DEBUG] User count in 'users' collection: {users_collection.count_documents({})}")


def create_ticket(student_id, ticket_type, notes=""):
    ticket_id = f"TICKET_{str(uuid.uuid4())[:8]}"
    ticket = {
        "ticket_id": ticket_id,
        "student_id": student_id,
        "ticket_type": ticket_type,
        "status": "Open",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "notes": notes
    }
    tickets_collection.insert_one(ticket)
    return ticket

def get_ticket_by_id(student_id, ticket_id):
    ticket = tickets_collection.find_one({"student_id": student_id, "ticket_id": ticket_id})
    return ticket

def get_tickets_by_student(student_id):
    tickets = list(tickets_collection.find({"student_id": student_id}))
    return tickets

def get_user_by_username(username):
    user = users_collection.find_one({"username": username})
    return user

def get_all_users():
    return list(users_collection.find())

def get_all_tickets():
    return list(tickets_collection.find())

