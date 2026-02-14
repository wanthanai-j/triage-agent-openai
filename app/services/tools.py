from typing import List, Dict
import json
import csv
import os
from datetime import datetime

# --- 1. Customer Data Tool (Mock Implementation) ---
# จำลอง Database ลูกค้าตามโจทย์ 3 Scenarios
MOCK_CUSTOMER_DB = {
    "CUST_001": {
        "plan": "Free",
        "region": "US",
        "months_active": 4,
        "previous_critical_incidents": 1
    },
    "CUST_002": {
        "plan": "Enterprise",
        "region": "Thailand",
        "seats": 45,
        "months_active": 8,
        "previous_critical_incidents": 0
    },
    "CUST_003": {
        "plan": "Pro",
        "region": "Sweden",
        "months_active": 5,
        "previous_critical_incidents": 2
    }
}

async def get_customer_profile(member_no: str) -> str:
    """
    Function สำหรับให้ AI เรียกใช้เพื่อดึงข้อมูลลูกค้าจาก member_no
    Return เป็น JSON string เพื่อให้ AI อ่านเข้าใจง่าย
    """
    customer = MOCK_CUSTOMER_DB.get(member_no)
    if customer:
        return json.dumps(customer)
    return json.dumps({"error": "Customer not found"})

# --- 2. Knowledge Base RAG Tool (Simulated for simplicity) ---
# In production, may be should connect with Postgres + pgvector (to do RAG)
# Mocak data and do Simulated Search.

MOCK_KB_DOCS = [
    # --- Category 1: Payment Issues ---
    {
        "id": 101,
        "content": "Refund Policy: Refunds are processed within 5-7 business days after approval. If a customer reports duplicate charges or failed upgrades (Free to Pro), escalate to Billing Team if there are more than 2 failed attempts or financial impact.",
        "keywords": ["refund", "money back", "duplicate charge", "payment failed", "upgrade error", "billing"]
    },
    {
        "id": 102,
        "content": "Subscription Renewal & Cancellation: Subscription renewal occurs automatically. To avoid being charged, users must cancel at least 24 hours before the billing date.",
        "keywords": ["cancel", "renewal", "subscription", "stop payment", "charge", "auto-renew"]
    },

    # --- Category 2: Authentication & Login ---
    {
        "id": 201,
        "content": "Login Issues & Password Reset: Password reset emails may take up to 5 minutes to arrive. Error 401 or 403 indicates authentication failure. If multiple login attempts fail across devices, check account lock status.",
        "keywords": ["login", "password reset", "email", "cant log in", "error 401", "error 403", "locked"]
    },
    {
        "id": 202,
        "content": "Enterprise SSO Failure: If an Enterprise user cannot log in via SSO, this is a High priority issue. Escalate immediately.",
        "keywords": ["sso", "enterprise login", "company login", "sign in"]
    },

    # --- Category 3: System Outage & Error 500 ---
    {
        "id": 301,
        "content": "System Error 500 & Outages: Error 500 indicates an internal server error. Check status.source.app first. If multiple users from the same region (e.g., Asia, Thailand) report an outage, classify as Critical. Enterprise customers receive SLA priority handling.",
        "keywords": ["error 500", "server error", "system down", "outage", "crash", "white screen"]
    },
    {
        "id": 302,
        "content": "Troubleshooting Steps for Outages: Before escalating, collect the following: Screenshot of the error, Timestamp of occurrence, and User Region.",
        "keywords": ["troubleshoot", "debug", "screenshot", "info needed", "check"]
    },

    # --- Category 4: Video Session & Therapist Issues ---
    {
        "id": 401,
        "content": "Video Call Troubleshooting: Ensure Microphone and Camera permissions are enabled. Latest Chrome or Safari browsers are recommended. If session fails due to unstable internet, suggest switching networks.",
        "keywords": ["video", "camera", "mic", "sound", "image", "browser", "chrome", "safari"]
    },
    {
        "id": 402,
        "content": "Therapist Unavailability: If a therapist is unavailable for a booked session, offer rebooking or credit compensation. Escalate if the session fails after 2 retry attempts.",
        "keywords": ["therapist", "doctor", "missing", "late", "rebook", "compensation", "credit"]
    },

    # --- Category 5: Feature Requests & Settings ---
    {
        "id": 501,
        "content": "Dark Mode Settings: Dark mode is available in Settings > Appearance (Pro plan and above only). Auto-scheduling for Dark Mode is not currently supported.",
        "keywords": ["dark mode", "theme", "appearance", "black screen", "schedule"]
    },
    {
        "id": 502,
        "content": "Notifications: Push notification preferences are configurable in Settings > Notifications.",
        "keywords": ["notification", "alert", "push", "settings"]
    },

    # --- Category 6: Privacy & Data ---
    {
        "id": 601,
        "content": "Data Privacy & Deletion: Users can request data export (GDPR compliance). Account deletion requests are processed within 7 days. Therapy notes are encrypted and NOT accessible by support agents.",
        "keywords": ["privacy", "gdpr", "delete account", "export data", "therapy notes", "confidential"]
    },
    {
        "id": 602,
        "content": "Data Breach Protocol: Escalate IMMEDIATELY if a user reports a suspected data breach.",
        "keywords": ["breach", "hacked", "leak", "security", "stolen data"]
    },

    # --- Category 7: SLA ---
    {
        "id": 701,
        "content": "SLA Response Times: Free plan: 24-48 hours. Pro plan: 12-24 hours. Enterprise plan: 1-4 hours. Critical incidents require immediate engineering notification.",
        "keywords": ["sla", "response time", "wait time", "how long", "urgent"]
    },

    # --- FAQ (Synthetic Questions) ---
    {
        "id": 901,
        "content": "FAQ: Why was I charged multiple times? Answer: This often happens during failed upgrades. Duplicate charges are usually pending pre-authorizations and will be reversed. If not, we can process a refund within 5-7 business days.",
        "keywords": ["charged twice", "double charge", "triple charge", "why charged"]
    },
    {
        "id": 902,
        "content": "FAQ: Can I schedule Dark Mode to turn on automatically? Answer: No, auto-scheduling is not currently supported. You can manually toggle it in Settings > Appearance if you are on a Pro plan.",
        "keywords": ["auto dark mode", "schedule theme", "night mode"]
    },
    {
        "id": 903,
        "content": "FAQ: My video session keeps disconnecting. Answer: Please check your internet connection and try using Chrome or Safari. Ensure camera/mic permissions are allowed.",
        "keywords": ["disconnect", "video lag", "cant see", "cant hear"]
    }
]

async def search_knowledge_base(query: str) -> str:
    """
    Function สำหรับค้นหา Knowledge Base (RAG)
    """
    # --- Mock up logic "Basic Keyword Matching") ---
    print(f"🔎 Agent is searching KB for: {query}")
    results = []
    query_lower = query.lower()
    
    # Simple algorithm: ค้นหาว่า keyword ใน doc ไปโผล่ใน query บ้างไหม
    # หรือ query บางส่วนไปโผล่ใน doc บ้างไหม
    for doc in MOCK_KB_DOCS:
        score = 0
        # Check matching keywords
        for k in doc["keywords"]:
            if k in query_lower:
                score += 1
        
        # Check context overlap
        if score > 0:
            results.append((score, doc["content"]))
    
    # Sort by relevance (score)
    results.sort(key=lambda x: x[0], reverse=True)
    
    # Return top 3 results
    top_results = [r[1] for r in results[:3]]

    if top_results:
        return "\n---\n".join(top_results)
    
    return "No relevant documentation found in Knowledge Base."

async def report_critical_incident(member_no: str, category: str, issue_summary: str, risk_level: str = None, kb_found: bool = False) -> str:
    """
    Logs a critical incident to a CSV file for audit trails.
    Use this when Urgency is identified as CRITICAL.
    """
    # Defensive coding: if AI didn't sent risk_level, default is "Critical"
    if not risk_level:
        risk_level = "Critical"
        
    filename = "./data_logs/critical_incidents_log.csv"
    
    # Check if file exists to write header
    file_exists = os.path.isfile(filename)
    
    try:
        # use 'a' (append) และ flush=True ensure for with open done and really save.
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write header if new file
            if not file_exists:
                writer.writerow(["Timestamp", "Member_No", "Risk_Level", "Category", "KB_Found", "Summary"])
            
            # Prepare row data
            timestamp = datetime.now().isoformat()
            row = [timestamp, member_no, risk_level, category, kb_found,issue_summary]
            
            # Write incident data
            writer.writerow(row)
            
            # Force write to disk
            file.flush()
            os.fsync(file.fileno())
            
        # Log to console
        print(f"\n[FILE WRITE SUCCESS] 📝 Logged to {filename}: {row}")
        return f"Critical incident logged successfully. Risk Level: {risk_level}, KB Found: {kb_found}"
        
    except Exception as e:
        print(f"[FILE WRITE ERROR] ❌ Failed to log: {str(e)}")
        return f"Failed to log incident: {str(e)}"

# --- Definition for OpenAI (Function Calling Schema) ---
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_customer_profile",
            "description": "Get customer subscription details, plan type, and history.",
            "parameters": {
                "type": "object",
                "properties": {
                    "member_no": {
                        "type": "string",
                        "description": "The customer member ID (e.g., CUST_001)"
                    }
                },
                "required": ["member_no"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search the internal FAQ and documentation for technical solutions, refund policies, SLAs, and troubleshooting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query based on the issue (e.g., 'refund policy', 'error 500', 'dark mode')"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "report_critical_incident",
            "description": "Log a critical incident to the system audit trail. MUST be called if the urgency is classified as CRITICAL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "member_no": {
                        "type": "string",
                        "description": "The customer member ID"
                    },
                    "category": {
                        "type": "string",
                        "description": "Grouping of issues"
                    },
                    "issue_summary": {
                        "type": "string",
                        "description": "Brief description of the critical issue"
                    },
                    "risk_level": {
                        "type": "string",
                        "enum": ["Critical", "High"],
                        "description": "The assessed risk level"
                    },
                    "kb_found": {
                        "type": "boolean",
                        "description": "Whether relevant information was found in the knowledge base (True/False)"
                    }
                },
                "required": ["member_no", "issue_summary", "risk_level", "kb_found"]
            }
        }
    }
]
