import os
import uuid
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.params import Header
from models import MatchTransactionRequest
from llm_service import get_llm_response, get_matched_transactions_prompt
from rabbitmq_publisher import publish_to_topic

app = FastAPI()

MATCH_TRANSACTION_ROUTING_KEY = os.getenv("MATCH_TRANSACTION_ROUTING_KEY", "financeapp.transaction-match")
API_TOKEN = os.getenv("API_TOKEN", "your-secret-token")

def validate_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    if token != API_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.post("/match-transactions")
async def process_prompt(
    request: MatchTransactionRequest, 
    background_tasks: BackgroundTasks,
    _: None = Depends(validate_token)):
    try:
        prompt = get_matched_transactions_prompt(
            transaction_names=request.transaction_names,
            transaction_group_names=request.transaction_group_names
        )
        correlation_id = str(uuid.uuid4())
        routing_key = MATCH_TRANSACTION_ROUTING_KEY
        background_tasks.add_task(handle_prompt, prompt, correlation_id, routing_key)

        return {"status": "success", "correlation_id": correlation_id, "message": "Request received and will be processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def handle_prompt(prompt: str, correlation_id: str, routing_key: str):
    try:
        response = await get_llm_response(prompt)
        message = {
            "id": correlation_id,
            "success": True,
            "prompt": prompt,
            "response": response
        }
        publish_to_topic(routing_key, message)
    except Exception as e:
        error_message = {
            "id": correlation_id,
            "success": False,
            "prompt": prompt,
            "error": str(e)
        }
        publish_to_topic(routing_key, error_message)
        print(f"[ERROR] Failed to process LLM request {correlation_id}: {e}")