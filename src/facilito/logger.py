import logging

import colorlog


# --- Custom Console Handler ---
class CustomConsoleHandler(colorlog.StreamHandler):
    def emit(self, record):
        # clone the record to avoid modifying the original
        record_copy = logging.makeLogRecord(record.__dict__)
        # remove exc_info from the copy
        record_copy.exc_info = None
        record_copy.exc_text = None
        super().emit(record_copy)


# --- Logger ---
logger = colorlog.getLogger(__name__)
logger.setLevel("DEBUG")

# --- Console Handler ---
console_formatter = colorlog.ColoredFormatter(
    "{log_color}[{levelname}] {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
)
console_handler = CustomConsoleHandler()
console_handler.setLevel("INFO")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# --- File Handler ---
log_file = "facilito.log"
file_formatter = logging.Formatter(
    "{asctime} [{levelname}] [{filename}:{funcName}:{lineno}] - {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
)
file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
file_handler.setLevel("DEBUG")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
