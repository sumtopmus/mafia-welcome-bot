from telegram.ext import Application

from utils import log
from handlers import error
from handlers import debug, info
from handlers import admin, request, schedule, welcome


async def post_init(app: Application) -> None:
    """Initializes bot with data and its tasks."""
    log('post_init')
    log(app.bot_data)
    app.bot_data.setdefault('clubs', {})
    app.bot_data.setdefault('players', {})
    app.bot_data.setdefault('schedule', {})


def add_handlers(app: Application) -> None:
    """Adds handlers to the bot."""
    # Error handler.
    app.add_error_handler(error.handler)
    # Debug commands.
    for module in [debug, info]:
        app.add_handlers(module.create_handlers())
    # General chat handling.
    for module in [admin, request, schedule, welcome]:
        app.add_handlers(module.create_handlers())