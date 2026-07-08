import logging
import sys

from loguru import logger


# loguru levels, ordered low -> high
LOG_LEVELS = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]

class _InterceptHandler(logging.Handler):
    """Route standard logging calls through loguru."""
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

_NOISY_LOGGERS = ("matplotlib", "urllib3")

def configure_logging(level: str = "INFO") -> None:
    """Reset loguru to log to stderr at the given level.
    
    # example usage:
    from quantaq_py.concat import concat_files
    from quantaq_py.log import configure_logging

    configure_logging("DEBUG")
    df = concat_files(my_files)
    """
    logger.remove()
    logger.add(sys.stderr, level=level.upper())
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
        