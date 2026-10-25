import asyncio

from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent as langchain_create_agent
from clients.abstraction.IRabbitMqClient import IRabbitMqClient
from models.Message import Message
from models.ChatMessage import ChatMessage, ChatMessages
from services.abstraction.ILLMService import ILLMService
from services.abstraction.ILoggerService import ILoggerService
from services.abstraction.IPromptService import IPromptService
from models.MatchTransactionResponse import MatchTransactionResponse
from config.settings import get_settings


def validate_azure_openai_configuration() -> None:
  settings = get_settings()
  required = {
    "AZURE_OPENAI_ENDPOINT": settings.azure_openai_endpoint,
    "AZURE_OPENAI_DEPLOYMENT_NAME": settings.azure_openai_deployment_name,
    "AZURE_OPENAI_API_VERSION": settings.azure_openai_api_version,
  }
  missing = [name for name, value in required.items() if not value]
  if missing:
    raise ValueError("Azure OpenAI configuration is required. Missing: " + ", ".join(missing))
  if not (settings.azure_openai_api_key or settings.openai_api_key):
    raise ValueError("Azure OpenAI requires AZURE_OPENAI_API_KEY or OPENAI_API_KEY")


class LLMService(ILLMService):
  def __init__(
      self, 
      rabbitmq_client: IRabbitMqClient, 
      logger: ILoggerService, 
      prompt_service: IPromptService):
    self.rabbitmq_client = rabbitmq_client
    self.logger = logger
    self.prompt_service = prompt_service
    self.llm = self._create_llm()

  def _create_llm(self) -> AzureChatOpenAI:
    settings = get_settings()
    validate_azure_openai_configuration()
    api_key = settings.azure_openai_api_key or settings.openai_api_key
    assert api_key is not None

    endpoint = settings.azure_openai_endpoint
    deployment_name = settings.azure_openai_deployment_name
    api_version = settings.azure_openai_api_version
    assert endpoint is not None and deployment_name is not None

    return AzureChatOpenAI(
      azure_endpoint=endpoint.rstrip("/"),
      azure_deployment=deployment_name,
      api_version=api_version,
      api_key=api_key,
    )


  async def match_transactions(
      self, 
      correlation_id: str, 
      transaction_names: list[str],
      transaction_group_names: list[str],
      user_id: str,
      categorization_rules: list[dict[str, str]] | None = None,
    ) -> None:
    matching_prompt = ""
    try:
      matching_prompt = self.prompt_service.get_matched_transactions_prompt(
        transaction_names,
        transaction_group_names,
        categorization_rules,
      )

      matching_agent = langchain_create_agent(
        model=self.llm,
        tools=[],
        system_prompt=matching_prompt,
      )

      message = ChatMessages(
        messages=[
          ChatMessage(role="system", content=f"user_id: {user_id} correlation_id: {correlation_id}"),
        ]
      )

      message_dump = message.model_dump()
      expected_transactions = set(transaction_names)
      expected_groups = set(transaction_group_names)
      match_response = None
      for attempt in range(2):
        try:
          response = await matching_agent.ainvoke(message_dump)
          messages = response.get('messages', [])
          if not messages:
            raise ValueError("The LLM returned no messages")

          last_message = messages[-1]
          result = getattr(last_message, 'content', '')
          candidate = MatchTransactionResponse.model_validate_json(result)
          if set(candidate.transactions) != expected_transactions:
            raise ValueError("The LLM returned an incomplete or unexpected transaction set")
          if not set(candidate.transactions.values()).issubset(expected_groups):
            raise ValueError("The LLM returned a group that was not in the request")

          match_response = candidate
          break
        except Exception as error:
          if attempt == 0:
            self.logger.warning(
              "Transaction matching attempt failed; retrying once (%s)",
              type(error).__name__,
            )
            await asyncio.sleep(1)
            continue
          raise

      if match_response is None:
        raise ValueError("The LLM could not return a valid transaction match response")

      if match_response.transactions:
        self.logger.info("Matched %s transactions", len(match_response.transactions))

      message = Message[MatchTransactionResponse](
        correlation_id=correlation_id,
        success=True,
        user_id=user_id,
        prompt=matching_prompt,
        data=match_response,
      )

      message_json = message.model_dump(mode="json", exclude_none=True)
      result_queue = self.rabbitmq_client.rabbitmq_config.RabbitMqSettings.ResultQueue
      await self.rabbitmq_client.publish_to_queue_async(result_queue, message_json)
      self.logger.info(f"Successfully processed LLM request {correlation_id}")

    except Exception as e:
      error_message = Message[str](
        correlation_id=correlation_id,
        success=False,
        user_id=user_id,
        prompt=matching_prompt or "Transaction matching request",
        error="Transaction matching failed"
      )
      
      result_queue = self.rabbitmq_client.rabbitmq_config.RabbitMqSettings.ResultQueue
      await self.rabbitmq_client.publish_to_queue_async(
        result_queue,
        error_message.model_dump(mode="json", exclude_none=True),
      )
      cause = e.__cause__ or e.__context__
      self.logger.error(
        "Transaction matching failed (%s): %s; cause=%r",
        type(e).__name__,
        e,
        cause,
      )
