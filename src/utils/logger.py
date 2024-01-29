"""logger utils"""
import logging

FILE_LOGGING_LEVEL = logging.DEBUG
STREAM_LOGGING_LEVEL = logging.INFO

LOGGING_FILE = "log.log"
LOGGING_FORMAT = (
    "[%(asctime)s][%(levelname)s][%(filename)s][%(lineno)d][%(funcName)s]: %(message)s"
)
LOGGING_DATEFORMAT = "%H:%M:%S"


def _configure_logger():
    """Configure logger"""

    file = logging.FileHandler(LOGGING_FILE)
    file.setLevel(FILE_LOGGING_LEVEL)
    file_format = logging.Formatter(LOGGING_FORMAT)
    file_format.datefmt = LOGGING_DATEFORMAT
    file.setFormatter(file_format)

    stream = logging.StreamHandler()
    stream.setLevel(STREAM_LOGGING_LEVEL)
    stream_format = logging.Formatter(LOGGING_FORMAT)
    stream_format.datefmt = LOGGING_DATEFORMAT
    stream.setFormatter(stream_format)

    _logger = logging.getLogger(__name__)
    _logger.setLevel(FILE_LOGGING_LEVEL)
    _logger.addHandler(file)
    _logger.addHandler(stream)
    return _logger


# call configure_logger() to configure logger
logger = _configure_logger()
