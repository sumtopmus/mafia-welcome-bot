from datetime import datetime
from config import settings
import logging


def log(msg: str, level=logging.DEBUG, exc_info=None) -> None:
    """Logging/debugging helper."""
    logging.getLogger(__name__).log(level, msg, exc_info=exc_info)
    if settings.DEBUG:
        printed_msg = f'⌚️ {datetime.now().strftime(settings.DATETIME_FORMAT)}: '
        if level == logging.ERROR:
            printed_msg += '❌ ERROR - '
        printed_msg += str(msg)
        print(printed_msg)
