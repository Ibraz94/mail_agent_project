from fastapi import FastAPI
import requests # Import the requests library
import json

app = FastAPI()

# Define the URL for the Mail Processing Agent
MAIL_PROCESSOR_URL = "http://localhost:8001/process_task"

@app.get("/")
def read_root():
    return {"message": "Front-End Orchestrator Agent is running."}

# Function to delegate tasks to the Mail Processing Agent
def delegate_to_mail_processor(task: dict):
    try:
        response = requests.post(MAIL_PROCESSOR_URL, json=task, timeout=10) # Send POST request
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Mail Processing Agent: {e}")
        return {"status": "error", "message": "Failed to connect to Mail Processing Agent"}
    except json.JSONDecodeError:
        print(f"Error decoding JSON response from Mail Processing Agent: {response.text}")
        return {"status": "error", "message": "Invalid response format from Mail Processing Agent"}

# Updated endpoint for handling user requests
@app.post("/process_request")
def process_request(user_input: dict):
    print(f"Received request: {user_input}")
    # TODO: Implement more sophisticated logic to determine the task type based on user input
    user_text = user_input.get("text", "")
    task_type = "check_email" # Default task for now
    if "reply to" in user_text.lower():
        task_type = "draft_reply"

    task = {"type": task_type, "details": user_text}

    print(f"Delegating task to Mail Processor: {task}")
    response_from_processor = delegate_to_mail_processor(task)

    print(f"Received response from Mail Processor: {response_from_processor}")
    # TODO: Implement logic to handle the response (e.g., display draft for approval)
    return {"status": "processed_by_orchestrator", "processor_response": response_from_processor}

if __name__ == "__main__":
    import uvicorn
    # Note: In a real deployment, use a proper ASGI server like uvicorn directly
    # For development, binding to 0.0.0.0 makes it accessible within the sandbox network
    uvicorn.run(app, host="0.0.0.0", port=8000)

