import logging
from logging.handlers import TimedRotatingFileHandler
import queue

class TkinterHandler(logging.Handler):

    def __init__(self):
        super().__init__()

    def emit(self, record):
        msg = self.format(record)
        log_queue.put(msg)

log_queue = queue.Queue()

logger = logging.getLogger("UL30")
logger.setLevel(logging.DEBUG)

tk_handler = TkinterHandler()
tk_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s - %(message)s",
    "%H:%M:%S"
)

tk_handler.setFormatter(formatter)

logger.addHandler(tk_handler)

file_handler = TimedRotatingFileHandler(
    "./Arquivos/Logs/ul30.log",
    when="midnight",
    interval=1,
    backupCount=90,   # mantém os últimos 90 dias
    encoding="utf-8"
)

file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)