from warnings import filterwarnings
import logging
import os
import pytz
from telegram.constants import ParseMode
from telegram.ext import Application, Defaults, PicklePersistence
from telegram.warnings import PTBUserWarning

from config import settings
from init import add_handlers, post_init


def main() -> None:
    """Runs bot."""
    # Create directory tree structure.
    for path in [settings.DB_PATH, settings.LOG_PATH]:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

    # Set up logging and debugging.
    logging_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(filename=settings.LOG_PATH, level=logging_level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

    # Setup the bot.
    defaults = Defaults(parse_mode=ParseMode.MARKDOWN, tzinfo=pytz.timezone(settings.TIMEZONE))
    persistence = PicklePersistence(filepath=settings.DB_PATH, single_file=False)
    app = Application.builder().token(settings.TOKEN).defaults(defaults)\
        .persistence(persistence).arbitrary_callback_data(True)\
        .post_init(post_init).build()
    # Add handlers.
    add_handlers(app)
    # Start the bot.
    app.run_polling()


if __name__ == "__main__":
    main()