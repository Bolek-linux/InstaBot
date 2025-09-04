# logging_config.py
import logging
import colorlog


def setup_logging():
    """
    Configures an advanced, multi-target logging system for the application.

    This function sets up a hierarchical logging structure:
    1.  Root Logger: Catches all logs.
        - A console handler outputs all DEBUG level logs and above with colored formatting.
        - A general file handler saves WARNING level logs and above from the application's
          own modules (e.g., main, telegram_bot) to 'app_warnings.log'.

    2.  Dedicated Library Loggers:
        - A specific handler for 'instagrapi' saves its WARNING and ERROR logs to 'insta_errors.log'.
        - A specific handler for 'pyrogram' saves its WARNING and ERROR logs to 'pyro_errors.log'.

    3.  Specific API Call Logger:
        - A shared handler for 'instagrapi.private_request' and 'instagrapi.public_request'
          saves all INFO logs (i.e., every API call) to 'insta_api_calls.log' for debugging
          and auditing purposes.

    To prevent duplicate entries and keep the console clean, propagation is disabled for all
    dedicated loggers.
    """
    # --- 1. Root Logger Configuration (for console and general app file) ---
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set the lowest level to capture everything.

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # --- Console Handler (shows everything from DEBUG up) ---
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = colorlog.ColoredFormatter(
        '%(white)s%(asctime)s%(reset)s%(log_color)s - %(levelname)-8s -> %(name)s - %(message)s%(reset)s',
        datefmt='%d-%m-%Y %H:%M:%S',
        log_colors={'DEBUG': 'cyan', 'INFO': 'green', 'WARNING': 'yellow', 'ERROR': 'red', 'CRITICAL': 'red,bg_white'}
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # --- General File Handler (for app-specific warnings) ---
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                       datefmt='%d-%m-%Y %H:%M:%S')
    app_file_handler = logging.FileHandler('app_warnings.log', mode='a', encoding='utf-8')
    app_file_handler.setLevel(logging.WARNING)
    app_file_handler.setFormatter(file_formatter)
    root_logger.addHandler(app_file_handler)

    # --- 2. Dedicated Logger for Instagrapi Errors ---
    insta_logger = logging.getLogger("instagrapi")
    insta_logger.setLevel(logging.WARNING)
    insta_error_handler = logging.FileHandler('insta_errors.log', mode='a', encoding='utf-8')
    insta_error_handler.setFormatter(file_formatter)
    insta_logger.addHandler(insta_error_handler)
    insta_logger.propagate = False

    # --- 3. Dedicated Logger for Pyrogram Errors ---
    pyro_logger = logging.getLogger("pyrogram")
    pyro_logger.setLevel(logging.WARNING)
    pyro_error_handler = logging.FileHandler('pyro_errors.log', mode='a', encoding='utf-8')
    pyro_error_handler.setFormatter(file_formatter)
    pyro_logger.addHandler(pyro_error_handler)
    pyro_logger.propagate = False

    # --- 4. Silencing other verbose loggers ---
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # --- 5. Dedicated Logger for Instagrapi API Calls (your new idea) ---
    # This handler will be shared by both private and public request loggers.
    api_calls_handler = logging.FileHandler('insta_api_calls.log', mode='a', encoding='utf-8')
    api_calls_handler.setLevel(logging.INFO)  # We want to log INFO-level messages about API calls.
    api_calls_handler.setFormatter(file_formatter)

    # Get the specific loggers for API requests.
    private_req_logger = logging.getLogger("private_request")
    public_req_logger = logging.getLogger("public_request")

    # Set their level to INFO to capture the logs.
    private_req_logger.setLevel(logging.INFO)
    public_req_logger.setLevel(logging.INFO)

    # Add the shared handler to both.
    private_req_logger.addHandler(api_calls_handler)
    public_req_logger.addHandler(api_calls_handler)

    # CRITICAL STEP: Prevent these INFO logs from bubbling up to the console.
    private_req_logger.propagate = False
    public_req_logger.propagate = False