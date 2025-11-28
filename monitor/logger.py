import logging
from pathlib import Path

# Directory for log files
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Path to the main log file
LOG_FILE = LOG_DIR / "monitor.log"

# Central project logger
logger = logging.getLogger("monitor")
logger.setLevel(logging.INFO)

# Prevent duplicate handlers when module is imported multiple times
if not logger.handlers:
    # File logger
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console logger (stdout)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
