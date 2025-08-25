
import requests
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from tools.tools import get_top_transaction_groups_tool

class McpClient:
  def __init__(self, mcp_url: str):
    
    self.mcp_url = mcp_url
    self.llm = ChatOpenAI(model="GPT-4", temperature=0)

    self.agent = initialize_agent(
      tools=[get_top_transaction_groups_tool],
      llm=self.llm,
      agent_type=AgentType.OPENAI_FUNCTIONS
    )

  def run_query(self, query: str):
    return self.agent.run(query)