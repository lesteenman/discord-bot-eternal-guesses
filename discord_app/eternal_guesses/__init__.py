import logging
import sys

LOG_FORMAT = "[%(name)s - %(levelname)s] %(message)s"
ROOT_LOG_LEVEL = logging.INFO
APPLICATION_LOG_LEVEL = logging.DEBUG


if len(logging.getLogger().handlers) > 0:
    # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
    # `.basicConfig` does not execute.
    root_logger = logging.getLogger()

    for log_handler in root_logger.handlers:
        root_logger.removeHandler(log_handler)

    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root_logger.addHandler(log_handler)
    root_logger.setLevel(ROOT_LOG_LEVEL)
else:
    logging.basicConfig(level=ROOT_LOG_LEVEL, format=LOG_FORMAT)
    root_logger = logging.getLogger()

root_logger.info(f"using {__name__} as the name for the app logger")
app_logger = logging.getLogger(__name__)
app_logger.setLevel(APPLICATION_LOG_LEVEL)
