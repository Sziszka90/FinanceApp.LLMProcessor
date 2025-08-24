from typing import List
from fastapi import BackgroundTasks, Depends
import openai
import os
from clients import McpClient
from rabbitmq_publisher import publish_async
from tools import tools
from .abstraction.ILLMService import ILLMService
from clients.FinanceAppApiClient import FinanceAppApiClient

class LLMService(ILLMService):
  def __init__(
    self, 
    api_key: str = None, 
    finance_app_api_client: McpClient = None, 
  ):
    if not api_key:
      raise ValueError("API key is required")
    openai.api_key = api_key

    if not finance_app_api_client:
      raise ValueError("FinanceAppApiClient is required")
    self.finance_app_api_client = finance_app_api_client

  async def get_llm_response(self, prompt: str) -> str:
    response = openai.chat.completions.create(
      model="gpt-4",
      messages=[
        {
          "role": "user",
          "content": prompt
        }
      ]
    )
    return response.choices[0].message.content

  async def get_llm_response_with_tools(self, prompt: str, user_id: str) -> str:
    response = openai.chat.completions.create(
      model="gpt-4",
      messages=[
        {
          "role": "system",
          "content": f"Query all tools and respond for the following user_id: {user_id}."
        },
        {
          "role": "user",
          "content": prompt
        }
      ],
      function_call="auto",
      tools=tools,
    )
    return response.choices[0].message.content

  def get_matched_transactions_prompt(self, transaction_names: List[str], transaction_group_names: List[str]) -> str:
    return (
      f"""
      You are a financial assistant creating transaction groups for bank transactions.
      Your task is to analyse the provided transaction names and categorise them into appropriate groups based on their nature.
      Such as salary, groceries, utilities, car, home, travel, food, electronics, entertainment, etc.
      I will provide you with a list of available transaction groups, and you should match the most suitable group for each transaction name.
      Transaction groups: {", ".join(transaction_group_names)}.
      """
      + "Return the transaction groups in list with the following structure: "
      +
      '[{"Transaction Name 1": "Group Name 1"}, {"Transaction Name 2": "Group Name 2"}]'
      +
      f"""
      Only return the JSON response in a list without any additional text or explanation. Without line breaks or markdown code blocks.
      Do not return any other text, just the JSON response.
      Return transaction groups for the following transactions, 
      do not modify the transaction name, 
      do not remove any additional space: {'; '.join(transaction_names)}. They are divided by ;.
      """
    )
  
  async def handle_prompt(
    self,
    prompt: str, 
    correlation_id: str, 
    exchange: str, 
    user_id: str = None,
    routing_key: str = None):
    try:
      response = await self.get_llm_response(prompt)
      message = {
        "correlation_id": correlation_id,
        "success": True,
        "user_id": user_id,
        "prompt": prompt,
        "response": response
      }
      await publish_async(exchange, routing_key, message)

    except Exception as e:
      error_message = {
        "correlation_id": correlation_id,
        "success": False,
        "user_id": user_id,
        "prompt": prompt,
        "error": str(e)
      }
      await publish_async(exchange, routing_key, error_message)
      print(f"[ERROR] Failed to process LLM request {correlation_id}: {e}")

  def process_prompt(
    self,
    prompt: str,
    user_id: str,
    correlation_id: str,
    routing_key: str,
    exchange: str,
    background_tasks: BackgroundTasks):
    try:
      background_tasks.add_task(
        self.handle_prompt, 
        prompt, 
        correlation_id, 
        exchange,
        user_id, 
        routing_key,      
      )

      return {"status": "success", "correlation_id": correlation_id, "message": "Request received and will be processed"}
    except Exception as e:
      return {"status": "error", "message": str(e)}

  async def process_prompt_async(
    self,
    prompt: str,
    user_id: str,
    correlation_id: str):
    try:
      response = await self.get_llm_response_with_tools(prompt=prompt, user_id=user_id)

      if hasattr(response, "function_call") and response.function_call:
        api_result = await self.finance_app_api_client.get_top_transaction_groups(
          prompt=prompt,
          correlation_id=correlation_id,
          start_date="2024-01-01T00:00:00Z",
          end_date="2024-12-31T23:59:59Z",
          top=10,
          user_id=user_id
        )

        combined_prompt = (
          f"User prompt: {prompt}\n"
          f"Function result: {api_result}\n"
          "Please format the answer for the backend."
        )

        final_response = await self.get_llm_response(combined_prompt)

        return {"status": "success", "correlation_id": correlation_id, "message": final_response}

      return {"status": "success", "correlation_id": correlation_id, "message": response}
    except Exception as e:
      return {"status": "error", "message": str(e)}
