# logging_config.py
import logging
import colorlog

def setup_logging():
    """
    Configures the logging system for the entire application.

    This function sets up two handlers for the root logger:
    - A console handler that outputs DEBUG level logs and above with colored
      formatting for better readability in a terminal.
    - A file handler that saves INFO level logs and above to a file named
      'app_warnings.log', which is useful for auditing and debugging
      production environments.
    """
    # Get the root logger. Configuring it will affect all descendant loggers.
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set the lowest level; handlers will filter messages.

    # Clear any existing handlers to prevent duplicate log messages.
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # --- Console Handler ---
    # This handler is for displaying logs in the console with colors.
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    console_formatter = colorlog.ColoredFormatter(
        '%(white)s%(asctime)s%(reset)s%(log_color)s - %(levelname)-8s -> %(name)s - %(message)s%(reset)s',
        datefmt='%d-%m-%Y %H:%M:%S',
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # --- File Handler ---
    # This handler writes logs to a file.
    file_handler = logging.FileHandler('app_warnings.log', mode='a', encoding='utf-8')
    file_handler.setLevel(logging.WARNING) # Only logs WARNING and higher levels.

    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)