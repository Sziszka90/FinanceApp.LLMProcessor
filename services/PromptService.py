from models import MatchTransactionResponse
from services.abstraction.IPromptService import IPromptService
from langchain.output_parsers import PydanticOutputParser

class PromptService(IPromptService):
  def get_matched_transactions_prompt(self, transaction_names: list[str], transaction_group_names: list[str]) -> str:
    parser = PydanticOutputParser(pydantic_object=MatchTransactionResponse)
    return (
      f"""
      You are a financial assistant creating transaction groups for bank transactions.
      Your task is to analyse the provided transaction names and categorise them into appropriate groups based on their nature.
      Such as salary, groceries, utilities, car, home, travel, food, electronics, entertainment, etc.
      I will provide you with a list of available transaction groups, and you should match the most suitable group for each transaction name.
      Transaction groups: {', '.join(transaction_group_names)}.
      When you respond, use the following format: {parser.get_format_instructions()}
      Return transaction groups for the following transactions, 
      do not modify the transaction name, 
      do not remove any additional space: {'; '.join(transaction_names)}. They are divided by ;.
      """
    )


