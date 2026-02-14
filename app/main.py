from fastapi import FastAPI, HTTPException
from app.models import TicketInput, TriageResult
from app.services.agent_service import process_ticket

app = FastAPI(
    title="Support Ticket Triage Agent",
    description="AI Agent that classifies tickets using OpenAI & RAG",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "Agent is operational"}

@app.post("/triage", response_model=TriageResult)
async def triage_ticket(ticket: TicketInput):
    """
    Main endpoint for send Ticket to AI analyze
    """
    try:
        # Call Service Layer
        result = await process_ticket(ticket)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
