from typing import List
import openai
import os

from tools import tools

openai.api_key = os.getenv("LLM_API_KEY")

async def get_llm_response(prompt: str) -> str:
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

async def get_llm_response_with_tools(prompt: str, user_id: str) -> str:
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
        tools=tools,
    )
    return response.choices[0].message.content

def get_matched_transactions_prompt(transaction_names: List[str], transaction_group_names: List[str]) -> str:
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
