import os
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.concurrency import asynccontextmanager
from fastapi.params import Header
from models import PromptRequest
from services.llm_service import get_matched_transactions_prompt
from models.MatchTransactionRequest import MatchTransactionRequest
from tasks.prompt_tasks import handle_prompt, process_prompt, process_prompt_async
from rabbitmq_publisher import initialize_rabbitmq_async, rabbitmq_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_rabbitmq_async()
    yield

app = FastAPI(lifespan=lifespan)

API_TOKEN = os.getenv("API_TOKEN", "your-secret-token")

def validate_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    if token != API_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.post("/llmprocessor/match-transactions")
async def match_transactions_endpoint(
    request: MatchTransactionRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Depends(validate_token)
):
    return await process_prompt_async(
        get_matched_transactions_prompt(request.transaction_names, request.transaction_group_names), 
        user_id=request.user_id, 
        correlation_id=request.correlation_id,
        routing_key=rabbitmq_config.RabbitMqSettings.RoutingKeys.TransactionsMatched.RoutingKey,
        exchange_name=rabbitmq_config.RabbitMqSettings.RoutingKeys.TransactionsMatched.ExchangeName,
        background_tasks=background_tasks)

@app.post("/llmprocessor/prompt")
async def prompt_endpoint(
    request: PromptRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Depends(validate_token)
):
    return await process_prompt(
        prompt=request.prompt, 
        user_id=request.user_id, 
        correlation_id=request.correlation_id,
        background_tasks=background_tasks)