import logging

class LoggerService:
  def __init__(self, name=__name__):
    self.logger = logging.getLogger(name)
    if not self.logger.hasHandlers():
      logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s"
      )

  def info(self, msg):
    self.logger.info(msg)

  def error(self, msg):
    self.logger.error(msg)

  def debug(self, msg):
    self.logger.debug(msg)