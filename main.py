from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.concurrency import asynccontextmanager
from dependencies.auth import authorize_token
from di.dependencies import get_llm_service
from models import PromptRequest
from models.MatchTransactionRequest import MatchTransactionRequest
from rabbitmq_publisher import initialize_rabbitmq_async, rabbitmq_config
from injector import Injector
from modules import AppModule
from services.LLMService import LLMService

injector = Injector([AppModule()])

@asynccontextmanager
async def lifespan(app: FastAPI):
  await initialize_rabbitmq_async()
  yield

app = FastAPI(lifespan=lifespan)

@app.post("/llmprocessor/match-transactions")
def match_transactions_endpoint(
  request: MatchTransactionRequest,
  background_tasks: BackgroundTasks,
  authorization: str = Depends(authorize_token),
  llm_service: LLMService = Depends(get_llm_service)
):
  return llm_service.process_prompt(
    llm_service.get_matched_transactions_prompt(request.transaction_names, request.transaction_group_names), 
    user_id=request.user_id, 
    correlation_id=request.correlation_id,
    routing_key=rabbitmq_config.RabbitMqSettings.RoutingKeys.TransactionsMatched.RoutingKey,
    exchange_name=rabbitmq_config.RabbitMqSettings.RoutingKeys.TransactionsMatched.ExchangeName,
    background_tasks=background_tasks
  )

@app.post("/llmprocessor/prompt")
async def prompt_endpoint(
  request: PromptRequest,
  authorization: str = Depends(authorize_token),
  llm_service: LLMService = Depends(get_llm_service)
):
  result = await llm_service.get_llm_response(request.prompt)
  return {"result": result}