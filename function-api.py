import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define your AIProxy API URL and API key
AIPROXY_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
AIPROXY_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZHMzMDAwMDkwQGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.Z9TWR3dvVwBfx2BCRG6mrAPA7pyYe8tbB_nnXEJ8-WA"  # Replace with your actual API key

# Function to query AIProxy for GPT
async def query_gpt(user_input: str, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            AIPROXY_URL,
            headers={
                "Authorization": f"Bearer {AIPROXY_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": user_input}],
                "tools": tools,
                "tool_choice": "auto",
            },
        )
    
    # Check if the response was successful
    response.raise_for_status()
    
    # Log the raw response for debugging
    print("Raw response:", response.text)  # Log the raw response for debugging
    
    return response.json()

# Define tools for each functionality
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_ticket_status",
            "description": "Get the status of an IT support ticket",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer", "description": "ID of the support ticket"}
                },
                "required": ["ticket_id"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting",
            "description": "Schedule a meeting",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date of the meeting"},
                    "time": {"type": "string", "description": "Time of the meeting"},
                    "meeting_room": {"type": "string", "description": "Room for the meeting"},
                },
                "required": ["date", "time", "meeting_room"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_expense_balance",
            "description": "Retrieve expense reimbursement balance",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "Employee ID"},
                },
                "required": ["employee_id"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_performance_bonus",
            "description": "Calculate performance bonus for an employee",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "Employee ID"},
                    "current_year": {"type": "integer", "description": "Year for bonus calculation"},
                },
                "required": ["employee_id", "current_year"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "report_office_issue",
            "description": "Report an office issue",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_code": {"type": "integer", "description": "Issue code"},
                    "department": {"type": "string", "description": "Department reporting the issue"},
                },
                "required": ["issue_code", "department"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
]

# Endpoint to handle queries
@app.get("/execute")
async def execute(q: str):
    try:
        response = await query_gpt(q, TOOLS)

        # Log the entire response for debugging
        print("Response from GPT:", response)  # Log the full response
        
        # Access tool_calls directly
        tool_calls = response.get("choices", [])[0].get("message", {}).get("tool_calls", [])
        
        if tool_calls:
            tool_call = tool_calls[0]  # Assuming we want the first tool call
            function_name = tool_call.get("function", {}).get("name", "unknown_function")
            arguments = tool_call.get("function", {}).get("arguments", "{}")  # Default to empty JSON object
            
            return {
                "name": function_name,
                "arguments": arguments
            }
        
        raise HTTPException(status_code=404, detail="No tool calls found.")
    except Exception as e:
        # Log the error with details
        print("Error in execute:", str(e))  # Log the error for debugging
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Example embedding function using AIProxy
@app.post("/embed")
async def embed_text(text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://aiproxy.sanand.workers.dev/openai/v1/embeddings",
            headers={
                "Authorization": f"Bearer {AIPROXY_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"input": text}
        )    
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()