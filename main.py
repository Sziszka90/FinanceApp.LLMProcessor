from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.concurrency import asynccontextmanager
from di.dependencies import authorize_token, get_llm_service, get_prompt_service, get_rabbitmq_client
from models.PromptRequest import PromptRequest
from models.MatchTransactionRequest import MatchTransactionRequest
from services.LLMService import LLMService
from services.PromptService import PromptService
from fastapi import FastAPI, Request
from dependencies.global_exception_handler import global_exception_handler
from fastapi.responses import JSONResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
  rabbitmq_client = get_rabbitmq_client()
  await rabbitmq_client.initialize_async()
  yield

app = FastAPI(lifespan=lifespan)

app.add_exception_handler(Exception, global_exception_handler)

@app.post("/llmprocessor/match-transactions")
def match_transactions_endpoint(
  request: MatchTransactionRequest,
  background_tasks: BackgroundTasks,
  authorization: str = Depends(authorize_token),
  llm_service: LLMService = Depends(get_llm_service),
  rabbitmq_client = Depends(get_rabbitmq_client)
):
  return llm_service.match_transactions_async(
    transactions=request.transaction_names,
    transaction_groups=request.transaction_group_names,
    user_id=request.user_id,
    correlation_id=request.correlation_id,
    routing_key=rabbitmq_client.rabbitmq_config.RabbitMqSettings.RoutingKeys.TransactionsMatched.RoutingKey,
    exchange=rabbitmq_client.rabbitmq_config.RabbitMqSettings.RoutingKeys.TransactionsMatched.ExchangeName,
    background_tasks=background_tasks
  )
 
@app.post("/llmprocessor/prompt")
async def prompt_endpoint(
  request: PromptRequest,
  authorization: str = Depends(authorize_token),
  llm_service: LLMService = Depends(get_llm_service)
):
  result = await llm_service.send_prompt(request.prompt, request.user_id, request.correlation_id)
  if not result:
    return JSONResponse(status_code=500, content={"detail": "LLM returned no result"})
  messages = result.get('messages', [])
  last_message = messages[-1]
  last_message_content = getattr(last_message, 'content', '')
  return {"result": last_message_content}

@app.post("/wakeup")
async def wakeup():
  return JSONResponse(content={"status": "success", "message": "Service is up"})