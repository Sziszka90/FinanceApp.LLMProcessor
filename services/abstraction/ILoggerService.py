from abc import ABC, abstractmethod

class ILoggerService(ABC):
  @abstractmethod
  def info(self, msg: str, *args: object):
    """
    Log an informational message.
    """
    pass

  @abstractmethod
  def error(self, msg: str, *args: object):
    """
    Log an error message.
    """
    pass

  @abstractmethod
  def warning(self, msg: str, *args: object):
    """
    Log a warning message.
    """
    pass

  @abstractmethod
  def debug(self, msg: str, *args: object):
    """
    Log a debug message.
    """
    pass
