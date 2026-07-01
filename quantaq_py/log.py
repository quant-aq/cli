import sys
from loguru import logger


# loguru levels, ordered low -> high
LOG_LEVELS = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]

def configure_logging(level: str = "INFO") -> None:
    """Reset loguru to log to stderr at the given level.
    
    # example usage:
    from quantaq.concat import concat_files
    from quantaq.log import configure_logging

    configure_logging("DEBUG")
    df = concat_files(my_files)
    """
    logger.remove()
    logger.add(sys.stderr, level=level.upper())
    