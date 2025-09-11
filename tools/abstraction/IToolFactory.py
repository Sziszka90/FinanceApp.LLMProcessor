from abc import ABC, abstractmethod

class IToolFactory(ABC):
  @abstractmethod
  def create_tools(self):
    """
    Ensures that all MCP tools are created and registered.
    This method should be called during the application startup to initialize the tool registry.
    """
    pass
