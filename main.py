from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from config.settings import load_settings
from dependencies.global_exception_handler import global_exception_handler
from di.dependencies import get_rabbitmq_client
from services.MatchTransactionJobHandler import MatchTransactionJobHandler
from services.PdfImportJobHandler import PdfImportJobHandler
from services.PromptService import PromptService
from services.LLMService import validate_azure_openai_configuration


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    load_settings()
    validate_azure_openai_configuration()
    rabbitmq_client = get_rabbitmq_client()
    try:
        await rabbitmq_client.initialize_async()
        queue_name = rabbitmq_client.rabbitmq_config.RabbitMqSettings.RequestQueue
        job_handler = MatchTransactionJobHandler(rabbitmq_client)
        await rabbitmq_client.consume_async(queue_name, job_handler.handle)
        pdf_queue = rabbitmq_client.rabbitmq_config.RabbitMqSettings.PdfRequestQueue
        await rabbitmq_client.consume_async(
            pdf_queue,
            PdfImportJobHandler(rabbitmq_client, PromptService()).handle,
        )
        yield
    # SHUTDOWN
    finally:
        await rabbitmq_client.close_async()


app = FastAPI(lifespan=lifespan)
app.add_exception_handler(Exception, global_exception_handler)


@app.post("/wakeup")
async def wakeup() -> JSONResponse:
    return JSONResponse(content={"status": "success", "message": "Service is up"})
