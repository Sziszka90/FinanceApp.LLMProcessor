import os
import uuid
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.params import Header
from llm_service import get_matched_transactions_prompt
from models import MatchTransactionRequest
from prompt_tasks import process_prompt

app = FastAPI()

API_TOKEN = os.getenv("API_TOKEN", "your-secret-token")

def validate_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    if token != API_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.post("/match-transactions")
async def match_transactions_endpoint(
    request: MatchTransactionRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Depends(validate_token)
):
    return await process_prompt(
        get_matched_transactions_prompt(request.transaction_names, request.transaction_group_names), 
        request.user_id, 
        str(uuid.uuid4()),
        "financeapp.transactions.matched",
        "financeapp.llm.topic",
        background_tasks)
