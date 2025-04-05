import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",  # Define the log format
)

logger = logging.getLogger("gh-chess")  # Use a custom name for the logger


def set_debug_mode():
    logger.setLevel(logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)  # Update the root logger level
    logger.debug("Logging level set to DEBUG")