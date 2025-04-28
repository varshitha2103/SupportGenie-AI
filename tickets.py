# tickets.py
import os
import json
import uuid
import datetime
from pathlib import Path

class TicketManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.tickets_file = self.data_dir / "tickets.json"
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create tickets file if it doesn't exist
        if not self.tickets_file.exists():
            with open(self.tickets_file, 'w') as f:
                json.dump({}, f)
    
    def get_timestamp(self):
        """Get current timestamp in ISO format"""
        return datetime.datetime.now().isoformat()
    
    def create_ticket(self, username, subject, description, priority="medium"):
        """Create a new ticket"""
        try:
            with open(self.tickets_file, 'r') as f:
                tickets = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            tickets = {}
        
        # Generate ticket ID
        ticket_id = str(uuid.uuid4())
        
        # Create ticket
        tickets[ticket_id] = {
            "ticket_id": ticket_id,
            "username": username,
            "subject": subject,
            "description": description,
            "status": "open",
            "priority": priority,
            "created_at": self.get_timestamp(),
            "updated_at": self.get_timestamp(),
            "assigned_to": "",
            "conversation": [
                {
                    "sender": username,
                    "message": description,
                    "timestamp": self.get_timestamp()
                }
            ]
        }
        
        with open(self.tickets_file, 'w') as f:
            json.dump(tickets, f, indent=2)
        
        return ticket_id
    
    def get_ticket(self, ticket_id):
        """Get ticket details"""
        try:
            with open(self.tickets_file, 'r') as f:
                tickets = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            tickets = {}
        
        return tickets.get(ticket_id)
    
    def add_message(self, ticket_id, sender, message):
        """Add a message to a ticket"""
        try:
            with open(self.tickets_file, 'r') as f:
                tickets = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            tickets = {}
        
        if ticket_id not in tickets:
            return False, "Ticket not found"
        
        tickets[ticket_id]["conversation"].append({
            "sender": sender,
            "message": message,
            "timestamp": self.get_timestamp()
        })
        
        tickets[ticket_id]["updated_at"] = self.get_timestamp()
        
        with open(self.tickets_file, 'w') as f:
            json.dump(tickets, f, indent=2)
        
        return True, "Message added"
    
    def update_status(self, ticket_id, status):
        """Update ticket status"""
        try:
            with open(self.tickets_file, 'r') as f:
                tickets = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            tickets = {}
        
        if ticket_id not in tickets:
            return False, "Ticket not found"
        
        tickets[ticket_id]["status"] = status
        tickets[ticket_id]["updated_at"] = self.get_timestamp()
        
        with open(self.tickets_file, 'w') as f:
            json.dump(tickets, f, indent=2)
        
        return True, "Status updated"
    
    def get_user_tickets(self, username):
        """Get all tickets for a user"""
        try:
            with open(self.tickets_file, 'r') as f:
                tickets = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            tickets = {}
        
        user_tickets = {}
        for ticket_id, ticket in tickets.items():
            if ticket["username"] == username:
                user_tickets[ticket_id] = ticket
        
        return user_tickets