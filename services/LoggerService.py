import logging
from services.abstraction.ILoggerService import ILoggerService

class LoggerService(ILoggerService):
  def __init__(self, name=__name__):
    self.logger = logging.getLogger(name)
    if not self.logger.hasHandlers():
      logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s"
      )

  def info(self, msg, *args):
    self.logger.info(msg, *args)

  def error(self, msg, *args):
    self.logger.error(msg, *args)

  def warning(self, msg, *args):
    self.logger.warning(msg, *args)

  def debug(self, msg, *args):
    self.logger.debug(msg, *args)
