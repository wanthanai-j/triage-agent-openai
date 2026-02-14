**Support Ticket Triage Agent 🤖**
==================================

An intelligent AI Agent designed to triage customer support tickets. It classifies urgency, extracts key information, searches a knowledge base (RAG), and determines the next best action (Auto-respond, Route, or Escalate).

Built with **FastAPI**, **OpenAI (Function Calling)**, and a **Mock Vector Store**.

**🚀 Features**
---------------

*   **Context-Aware Analysis:** Enriches ticket data with customer profiles (Mock CRM) to determine priority based on user tier (e.g., Enterprise vs. Free).
    
*   **Agentic Workflow:** Uses OpenAI function calling to dynamically choose tools (Look up user -> Search KB -> Log Incident).
    
*   **Mock RAG (Retrieval-Augmented Generation):** Simulates a vector search against an internal Knowledge Base to provide grounded answers.
    
*   **Critical Incident Logging:** Automatically logs critical issues (e.g., System Outages, Data Breaches) to a CSV audit trail.
    
*   **Structured Output:** Guarantees JSON responses using Pydantic models for reliable downstream integration.
    

**🛠️ Prerequisites**
---------------------

*   Python 3.10 or higher
    
*   OpenAI API Key (GPT-4o or GPT-3.5-turbo)
    

**📦 Installation**
-------------------

1.  **Clone the repository** <br>
```git clone https://github.com/wanthanai-j/triage-agent-openai.git``` <br>
```cd triage-agent-openai```
    
2.  **Create and activate a virtual environment**
* Windows <br>
```python -m venv venvvenv``` <br>
```Scripts\\activate```
* macOS/Linux <br>
```python3 -m venv venv``` <br>
```source venv/bin/activate```
    
3.  **Install dependencies** <br>
```pip install -r requirements.txt```
    

**⚙️ Configuration**
--------------------

1.  Create a .env file in the root directory (or rename .env.example).
    
2.  Add your OpenAI API Key:<br>
```OPENAI_API_KEY=your-api-key-here```<br>
```OPENAI_API_MODEL=pick-your-model-here```<br><br>
_Note: You can also set this directly in app/services/agent\_service.py for testing purposes, but using environment variables is recommended._
    

**▶️ Running the Application**
------------------------------

Start the FastAPI server using **Uvicorn**:

```uvicorn app.main:app --reload```

The server will start at http://127.0.0.1:8000.

**🧪 Usage & Testing**
----------------------

### **1\. Swagger UI (Interactive Docs)**

Open your browser and navigate to:

👉  **http://127.0.0.1:8000/docs**

You can test the /triage endpoint directly from the UI.

### **2\. Sample Request (CURL)**

You can use the following CURL command to test a scenario:
```
curl -X 'POST' \
  '[http://127.0.0.1:8000/triage](http://127.0.0.1:8000/triage)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "ticket_id": "TKT-001",
  "member_no": "CUST_002",
  "messages": [
    "ระบบเข้าไม่ได้ครับ ขึ้น error 500",
    "ลูกค้าโวยเข้ามาเยอะมาก deal นี้อาจจะหลุด"
  ]
}'
```

OR this, in POST (/triage) Swagger UI

```
{
  "ticket_id": "TKT-001",
  "member_no": "CUST_002",
  "messages": [
    "ระบบเข้าไม่ได้ครับ ขึ้น error 500",
    "ลูกค้าโวยเข้ามาเยอะมาก deal นี้อาจจะหลุด"
  ]
}
```
**📂 Project Structure**
------------------------

```
support-agent/
├── app/
│   ├── __init__.py
│   ├── main.py            # API Entry Point (FastAPI)
│   ├── models.py          # Pydantic Data Models (Input/Output Schemas)
│   └── services/
│       ├── __init__.py
│       ├── agent_service.py   # Core Agent Logic & Prompting
│       └── tools.py           # Mock Tools (Customer DB, KB Search, CSV Logger)
├── critical_incidents_log.csv # Generated automatically for critical cases
├── requirements.txt           # Project Dependencies
└── README.md                  # Documentation
```
