from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Status(str, Enum):
    open = "open"
    ai_resolved = "ai_resolved"
    agent_review = "agent_review"
    closed = "closed"


class Category(str, Enum):
    billing = "billing"
    technical = "technical"
    account = "account"
    shipping = "shipping"
    general = "general"


class TicketCreate(BaseModel):
    customer_name: str
    customer_email: str
    subject: str
    description: str


class TicketUpdate(BaseModel):
    status: Optional[Status] = None
    agent_notes: Optional[str] = None
    resolution: Optional[str] = None


class Ticket(BaseModel):
    id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: Status = Status.open
    priority: Priority = Priority.medium
    category: Category = Category.general
    ai_resolution: Optional[str] = None
    ai_confidence: Optional[float] = None
    agent_notes: Optional[str] = None
    resolution: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
