from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import json, uuid, os
from models import Ticket, TicketCreate, TicketUpdate, Status
from ai_engine import analyze_ticket

app = FastAPI(title="AI Support Ticket Resolution", version="1.0.0")

TICKETS_FILE = "tickets.json"


def load_tickets() -> dict:
    if not os.path.exists(TICKETS_FILE):
        return {}
    with open(TICKETS_FILE) as f:
        return json.load(f)


def save_tickets(tickets: dict):
    with open(TICKETS_FILE, "w") as f:
        json.dump(tickets, f, indent=2)


@app.get("/")
def root():
    return FileResponse("index.html")


@app.post("/tickets", response_model=Ticket)
def create_ticket(payload: TicketCreate):
    tickets = load_tickets()
    ticket_id = str(uuid.uuid4())[:8]

    # Run AI analysis
    ai_result = analyze_ticket(payload.subject, payload.description)

    ticket = Ticket(
        id=ticket_id,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        subject=payload.subject,
        description=payload.description,
        category=ai_result["category"],
        priority=ai_result["priority"],
        ai_resolution=ai_result["ai_resolution"],
        ai_confidence=ai_result["confidence"],
        status=Status.ai_resolved if ai_result["confidence"] >= 0.8 else Status.agent_review,
    )

    tickets[ticket_id] = ticket.model_dump()
    save_tickets(tickets)
    return ticket


@app.get("/tickets")
def list_tickets(status: str = None, priority: str = None):
    tickets = load_tickets()
    result = list(tickets.values())
    if status:
        result = [t for t in result if t["status"] == status]
    if priority:
        result = [t for t in result if t["priority"] == priority]
    result.sort(key=lambda t: t["created_at"], reverse=True)
    return result


@app.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: str):
    tickets = load_tickets()
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return tickets[ticket_id]


@app.patch("/tickets/{ticket_id}", response_model=Ticket)
def update_ticket(ticket_id: str, payload: TicketUpdate):
    tickets = load_tickets()
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket = tickets[ticket_id]
    updates = payload.model_dump(exclude_none=True)
    ticket.update(updates)
    ticket["updated_at"] = datetime.utcnow().isoformat()
    tickets[ticket_id] = ticket
    save_tickets(tickets)
    return ticket


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: str):
    tickets = load_tickets()
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket not found")
    del tickets[ticket_id]
    save_tickets(tickets)
    return {"message": "Ticket deleted"}


@app.get("/stats")
def get_stats():
    tickets = list(load_tickets().values())
    return {
        "total": len(tickets),
        "by_status": {s: sum(1 for t in tickets if t["status"] == s) for s in ["open", "ai_resolved", "agent_review", "closed"]},
        "by_priority": {p: sum(1 for t in tickets if t["priority"] == p) for p in ["low", "medium", "high", "critical"]},
        "by_category": {c: sum(1 for t in tickets if t["category"] == c) for c in ["billing", "technical", "account", "shipping", "general"]},
        "ai_resolution_rate": round(sum(1 for t in tickets if t["status"] == "ai_resolved") / len(tickets) * 100, 1) if tickets else 0,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
