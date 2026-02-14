from openai import AsyncOpenAI
import json
import os
from dotenv import load_dotenv
from app.models import TicketInput, TriageResult
from app.services.tools import TOOLS_SCHEMA, get_customer_profile, search_knowledge_base, report_critical_incident

load_dotenv()
open_api_key = os.getenv("OPENAI_API_KEY")
open_api_modl = os.getenv("OPENAI_API_MODEL")
client = AsyncOpenAI(api_key=open_api_key)

SYSTEM_PROMPT = """
You are an expert Customer Support Triage AI.
Your goal is to analyze support tickets, use tools to gather context, and decide the next action.

# STRICT EXECUTION PROTOCOL (Follow in Order):

1. **GATHER CONTEXT**:
   - ALWAYS call `get_customer_profile` first.
   - Call `search_knowledge_base` to find solutions.

2. **EVALUATE URGENCY**:
   - Analyze Customer Plan (Enterprise/Pro/Free) + Issue Severity.
   - **CRITICAL CONDITIONS**:
     - Enterprise Customer + System Outage/Error 500.
     - Data Breach / Security issues.
     - Revenue risking incidents (e.g., "deal will be lost").

3. **MANDATORY CRITICAL ACTION (Crucial Step)**:
   - **IF** the issue is evaluated as **CRITICAL**:
     - You **MUST** call the tool `report_critical_incident` **IMMEDIATELY**.
     - **DO NOT** generate the final JSON output until you have successfully called this tool and received a confirmation.
     - If `kb_found=False`, you should decide escalate to Human Agent **IMMEDIATELY**. DO NOT predict.
     - If you haven't called it yet, do it NOW.

4. **FINAL OUTPUT**:
   - Only after all necessary tools are called, return the final answer as a structured JSON.

# OUTPUT JSON FORMAT:
{
  "urgency": "Critical" | "High" | "Medium" | "Low",
  "sentiment": "string",
  "category": "Billing" | "Technical" | "Feature Request" | "General",
  "summary": "string",
  "suggested_action": "Auto-respond" | "Route to Specialist" | "Escalate to Human",
  "draft_response": "string"
}
"""

async def process_ticket(ticket: TicketInput) -> TriageResult:
    # 1. Prepare Messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Ticket from Member: {ticket.member_no}\nMessages: {ticket.messages}"}
    ]

    # For loop for AI calling Tool multiple times (Max 4 turns to defend infinite loop)
    for _ in range(4):
        # 2. Call AI
        response = await client.chat.completions.create(
            model=open_api_modl,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # 3. If AI decide to calling Tool
        if tool_calls:
            messages.append(response_message)  # Append AI responded to history

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    function_args = {}
                
                tool_output = ""
                print(f"⚙️ Calling Tool: {function_name}")
                
                # Router for Calling Python Function Tools
                if function_name == "get_customer_profile":
                    tool_output = await get_customer_profile(
                        member_no=function_args.get("member_no")
                    )
                elif function_name == "search_knowledge_base":
                    tool_output = await search_knowledge_base(
                        query=function_args.get("query", "")
                    )
                elif function_name == "report_critical_incident":
                    tool_output = await report_critical_incident(
                        member_no=function_args.get("member_no"),
                        category=function_args.get("category"),
                        issue_summary=function_args.get("issue_summary"),
                        risk_level=function_args.get("risk_level"),
                        kb_found=function_args.get("kb_found")
                    )
                
                # Return Tool result back to AI
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(tool_output),
                })
            
            # Back Loop to AI (for support to call report_critical_incident or summary)
            continue

        else:
            # 4. Else AI not calling Tool anymore (or Tool Calls is None) -> Done and return JSON
            # Enforce JSON Mode in final loop
            if not response_message.content:
                 return TriageResult(
                    urgency="Low", sentiment="Neutral", category="General",
                    summary="No content generated", suggested_action="Escalate to Human",
                    draft_response="Error in AI generation"
                 )
            
            try:
                # if return as JSON string
                return TriageResult.model_validate_json(response_message.content)
            except:
                # If isn't not JSON -> Call it again to force to JSON string
                final_json_response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    response_format={"type": "json_object"}
                )
                final_content = final_json_response.choices[0].message.content
                return TriageResult.model_validate_json(final_content)

    # Fallback If end of Loop, but isn't end
    return TriageResult(
        urgency="High", 
        sentiment="Unknown", 
        category="General", 
        summary="Process timed out or loop limit reached", 
        suggested_action="Escalate to Human", 
        draft_response="Error: Processing Limit Reached"
    )
