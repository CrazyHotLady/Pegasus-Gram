import logging
import os

LOG_FILE = 'errors_log.txt'

def setup_logging():
    """Configures the logging module to log errors and critical messages to a file."""
    # Ensure the log directory exists (if specified)
    # log_dir = os.path.dirname(LOG_FILE)
    # if log_dir and not os.path.exists(log_dir):
    #     os.makedirs(log_dir)

    # Get the root logger
    logger = logging.getLogger()
    # Set the minimum level to capture (e.g., WARNING, ERROR, CRITICAL)
    # Use INFO for more detailed operational logs if needed later
    logger.setLevel(logging.WARNING)

    # Create a file handler
    # Use 'a' for append mode
    file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.WARNING) # Log WARNING and above to the file

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handler to the root logger
    # Avoid adding handlers multiple times if setup_logging is called more than once
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == os.path.abspath(LOG_FILE) for h in logger.handlers):
        logger.addHandler(file_handler)
        print(f"Logging configured. Errors will be saved to {LOG_FILE}")
    else:
        print("File logger already configured.")

# Example of getting a logger instance for a specific module
# logger = logging.getLogger(__name__)
# logger.warning("This is a warning message.")
# logger.error("This is an error message.") 