from abc import ABC, abstractmethod

class IMcpTool(ABC):
  @abstractmethod
  def run(self, *args, **kwargs):
    """
    Execute the MCP tool logic with the provided arguments.
    Args:
      *args: Positional arguments for the tool.
      **kwargs: Keyword arguments for the tool.
    Returns:
      Any: The result of the tool execution.
    """
    pass
