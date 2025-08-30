from abc import ABC, abstractmethod

class IToolFactory(ABC):
  @abstractmethod
  def create_tools(self):
    pass
