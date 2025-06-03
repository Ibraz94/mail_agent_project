from fastapi import FastAPI
import time

app = FastAPI()

# --- Placeholder Functions for External Integrations ---

def _fetch_emails_mock(query: str):
    """Simulates fetching emails from an email service."""
    print(f"[MOCK] Fetching emails related to: {query}")
    time.sleep(0.5) # Simulate network delay
    # Simulate finding relevant emails
    return [
        {"id": "email123", "sender": "jane@example.com", "subject": "Meeting Request", "body": "Hi, Can we meet on Monday?"},
        {"id": "email456", "sender": "boss@example.com", "subject": "Project Update", "body": "Please provide the latest status."}
    ]

def _call_llm_mock(prompt: str, tools: list | None = None):
    """Simulates calling a Large Language Model for processing or tool use."""
    print(f"[MOCK] Calling LLM with prompt: {prompt[:100]}...")
    time.sleep(1) # Simulate LLM processing time
    if "summarize" in prompt.lower():
        return {"type": "text_response", "content": "Mock summary: You have 2 unread emails. One from Jane about a meeting, one from Boss about a project update."}
    elif "draft reply" in prompt.lower() and "monday works" in prompt.lower():
        # Simulate LLM deciding to call the SendEmail tool after checking calendar (implicitly)
        return {
            "type": "tool_call_draft", # Indicate a draft requiring approval
            "tool_name": "SendEmail",
            "arguments": {
                "recipient": "jane@example.com",
                "subject": "Re: Meeting Request",
                "body": "Hi Jane, Monday works great for me. Thanks!"
            }
        }
    elif "check calendar" in prompt.lower():
         # Simulate LLM calling CheckCalendar tool
         return {
            "type": "tool_call",
            "tool_name": "CheckCalendar",
            "arguments": {"date": "Next Monday"}
         }
    else:
        return {"type": "text_response", "content": "Mock LLM response to the prompt."}

def _send_email_mock(recipient: str, subject: str, body: str):
    """Simulates using the SendEmail tool/API."""
    print(f"[MOCK] Sending email to {recipient} with subject 	'{subject}'")
    time.sleep(0.3)
    return {"status": "success", "message_id": "mock_msg_789"}

def _check_calendar_mock(date: str):
    """Simulates using the CheckCalendar tool."""
    print(f"[MOCK] Checking calendar availability for: {date}")
    time.sleep(0.2)
    return {"status": "success", "is_available": True, "details": "No conflicts found for next Monday."}

# --- Agent Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Mail Processing Agent is running."}

@app.post("/process_task")
def process_task(task: dict):
    print(f"Received task: {task}")
    task_type = task.get("type")
    details = task.get("details")
    final_result = None
    requires_approval = False

    if task_type == "check_email":
        # 1. Fetch emails (using mock)
        emails = _fetch_emails_mock(details)
        # 2. Ask LLM to summarize (using mock)
        prompt = f"Summarize the following emails: {emails}"
        llm_response = _call_llm_mock(prompt)
        final_result = llm_response.get("content", "Error summarizing emails.")

    elif task_type == "draft_reply":
        # 1. (Implicit) Fetch relevant email context if needed (skipped in mock)
        # 2. Ask LLM to draft reply (using mock)
        prompt = f"Draft reply to email based on user request: {details}"
        llm_response = _call_llm_mock(prompt)

        if llm_response.get("type") == "tool_call_draft":
            # LLM generated a draft that needs approval (e.g., SendEmail)
            final_result = llm_response # Pass the whole draft object back
            requires_approval = True
        else:
            # LLM generated a simple text response or an error
            final_result = llm_response.get("content", "Error drafting reply.")

    elif task_type == "execute_action": # New task type for executing approved actions
        action_details = task.get("action_details", {})
        tool_name = action_details.get("tool_name")
        arguments = action_details.get("arguments", {})
        if tool_name == "SendEmail":
            # Execute the SendEmail tool (using mock)
            result = _send_email_mock(**arguments)
            final_result = result
        else:
             final_result = {"status": "error", "message": f"Execution of tool '{tool_name}' not implemented yet."}
        requires_approval = False # Action is being executed after approval

    else:
        return {"status": "error", "message": "Unknown task type"}

    return {
        "status": "processed",
        "result": final_result,
        "requires_approval": requires_approval
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

