from abc import ABC, abstractmethod

class ILoggerService(ABC):
  @abstractmethod
  def info(self, msg: str):
    """
    Log an informational message.
    """
    pass

  @abstractmethod
  def error(self, msg: str):
    """
    Log an error message.
    """
    pass

  @abstractmethod
  def warning(self, msg: str):
    """
    Log a warning message.
    """
    pass

  @abstractmethod
  def debug(self, msg: str):
    """
    Log a debug message.
    """
    pass
