from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# --- Ticket Input Model ---
# Incomming Data format for API
class TicketInput(BaseModel):
    ticket_id: str
    member_no: str  # Customer Profile (no.)
    messages: List[str]  # Chat Messages (List of strings)

# --- Output Structure (Structured Output) ---
class TriageResult(BaseModel):
    urgency: Literal["Critical", "High", "Medium", "Low"] = Field(..., description="Level of urgency")
    sentiment: str = Field(..., description="Customer sentiment analysis")
    category: Literal["Billing", "Technical", "Feature Request", "General"] = Field(..., description="Issue category")
    summary: str = Field(..., description="Brief summary of the issue")
    suggested_action: Literal["Auto-respond", "Route to Specialist", "Escalate to Human"]
    draft_response: str = Field(..., description="Drafted response for the agent")


# --- Customer Profile (Mock Data Structure) ---
class CustomerProfile(BaseModel):
    member_no: str
    plan: str
    region: str
    months_active: int
    is_active: bool
