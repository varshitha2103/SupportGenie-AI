#ticket_store.py
import json
import os
from datetime import datetime
import uuid

TICKET_FILE = "tickets.json"

class TicketStore:
    def __init__(self, file_path="tickets.json"):
        import json
        self.file_path = file_path
        with open(file_path, "r") as f:
            self.tickets = json.load(f)

    def get_ticket_by_id(self, student_id, ticket_id):
        for ticket in self.tickets:
            if ticket["student_id"] == student_id and ticket["ticket_id"] == ticket_id:
                return ticket
        return None


def load_tickets():
    """Load tickets from the local JSON file."""
    if not os.path.exists(TICKET_FILE):
        return []
    with open(TICKET_FILE, "r") as file:
        return json.load(file)

def save_tickets(tickets):
    """Save tickets to the local JSON file."""
    with open(TICKET_FILE, "w") as file:
        json.dump(tickets, file, indent=4)

def create_ticket(student_id, ticket_type, notes=""):
    """Create a new ticket."""
    tickets = load_tickets()
    ticket_id = f"TICKET_{str(uuid.uuid4())[:8]}"  # e.g., TICKET_abcd1234
    new_ticket = {
        "ticket_id": ticket_id,
        "student_id": student_id,
        "ticket_type": ticket_type,
        "status": "Open",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "notes": notes
    }
    tickets.append(new_ticket)
    save_tickets(tickets)
    return new_ticket

def get_ticket_status(student_id, ticket_id=None):
    """Get ticket(s) for a given student."""
    tickets = load_tickets()
    student_tickets = [
        ticket for ticket in tickets if ticket["student_id"] == student_id
    ]

    if ticket_id:
        student_tickets = [
            ticket for ticket in student_tickets if ticket["ticket_id"].lower() == ticket_id.lower()
        ]

    return student_tickets
