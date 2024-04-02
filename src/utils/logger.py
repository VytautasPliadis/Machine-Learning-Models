import logging
from logging import Logger


def setup_logger() -> Logger:
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Define the log format
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler()],  # Log to standard output (console)
    )

    return logging.getLogger()


logger = setup_logger()
