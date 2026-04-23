import logging
import os
from datetime import datetime

def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Log filename with timestamp
    log_filename = os.path.join(log_dir, f"trading_bot_{datetime.now().strftime('%Y%m%d')}.log")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger("trading_bot")
    return logger
