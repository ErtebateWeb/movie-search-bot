import logging
import os
from datetime import datetime

LOG_FILE = os.path.join("storage", "crawler.log")

# Create logger
logger = logging.getLogger("crawler")
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Log format with timestamp
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log_info(msg: str):
    logger.info(msg)


def log_error(msg: str):
    logger.error(msg)