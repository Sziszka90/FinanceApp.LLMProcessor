from abc import ABC, abstractmethod

class IMcpTool(ABC):
  @abstractmethod
  def run(self, *args, **kwargs):
    pass
