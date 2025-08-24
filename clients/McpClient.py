import requests
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI

# MCP Tool: Call .NET API
def get_total_spending(month: str):
    payload = {"name": "get_total_spending", "arguments": {"month": month}}
    response = requests.post("http://localhost:5000/mcp", json=payload)
    return response.json()

# Register as LangChain Tool
spending_tool = StructuredTool.from_function(
    func=get_total_spending,
    name="get_total_spending",
    description="Fetches total spending for a given month"
)

llm = ChatOpenAI(model="gpt-4", temperature=0)

# Agent with MCP tool
from langchain.agents import initialize_agent, AgentType

agent = initialize_agent(
    tools=[spending_tool],
    llm=llm,
    agent_type=AgentType.OPENAI_FUNCTIONS
)

# User Query
print(agent.run("What is my total spending for August?"))
