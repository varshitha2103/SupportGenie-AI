from agno.tools.decorator import tool
# from ticket_store import create_ticket, TicketStore
from mongo_store import create_ticket, get_ticket_by_id, get_tickets_by_student


@tool(name="create_ticket", description="Create a ticket for OPT, CPT, or Travel I-20 requests.")
def create_ticket_tool(student_id: str, ticket_type: str, notes: str = ""):
    ticket = create_ticket(student_id=student_id, ticket_type=ticket_type, notes=notes)
    return {
        "message": f"✅ Ticket created successfully! Ticket ID: {ticket['ticket_id']}",
        "ticket": ticket
    }

@tool(name="get_ticket_status_tool", description="Get the status of a specific ticket using ticket ID.")
def get_ticket_status_tool(student_id: str, ticket_id: str):
    ticket = get_ticket_by_id(student_id, ticket_id)

    if ticket:
        return {
            "message": f"🎫 Ticket ID: {ticket['ticket_id']}\n\n- Status: {ticket['status']}\n- Notes: {ticket.get('notes', '') or 'No notes available'}"
        }
    else:
        return {"message": "No matching tickets found."}












# @tool(name="create_ticket", description="Create a ticket for OPT, CPT, or Travel I-20 requests.")
# def create_ticket_tool(student_id: str, ticket_type: str, notes: str = ""):
#     ticket = create_ticket(student_id=student_id, ticket_type=ticket_type, notes=notes)
#     return {
#         "message": f"✅ Ticket created successfully! Ticket ID: {ticket['ticket_id']}",
#         "ticket": ticket
#     }

# @tool(name="get_ticket_status_tool", description="Get the status of a specific ticket using ticket ID.")
# def get_ticket_status_tool(student_id: str, ticket_id: str):
#     store = TicketStore()
#     ticket = store.get_ticket_by_id(student_id, ticket_id)

#     if ticket:
#         return {
#             "message": f"🎫 Ticket ID: {ticket['ticket_id']}\n\n- Status: {ticket['status']}\n- Notes: {ticket.get('notes', '') or 'No notes available'}"
#         }
#     else:
#         return {"message": "No matching tickets found."}
