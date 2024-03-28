from telegram.ext import Application

import utils
from handlers import error
from handlers import admin, request, schedule, welcome


async def post_init(app: Application) -> None:
    """Initializes bot with data and its tasks."""
    utils.log('intializing_players')
    app.bot_data.setdefault('players', {})
    app.bot_data.setdefault('schedule', {})
    app.bot_data.setdefault('tournaments', {})


def add_handlers(app: Application) -> None:
    """Adds handlers to the bot."""
    # Error handler.
    app.add_error_handler(error.handler)
    # General chat handling.
    for module in [admin, request, schedule, welcome]:
        app.add_handlers(module.create_handlers())