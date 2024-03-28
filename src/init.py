from datetime import datetime, time
from dynaconf import settings
from telegram.ext import Application

import utils
from handlers import error
from handlers import debug, info
from handlers import digest, request, schedule, welcome


async def post_init(app: Application) -> None:
    """Initializes bot with data and its tasks."""
    utils.log('intializing')
    app.bot_data.setdefault('players', {})    
    app.bot_data.setdefault('schedule', {})
    app.bot_data.setdefault('messages', [])
    app.bot_data['messages'] = []
    app.bot_data.setdefault('latest_digest', {})
    app.bot_data['latest_digest'].setdefault('timestamp', datetime.now().isoformat())
    app.bot_data['latest_digest'].setdefault('message_id', None)
    app.job_queue.run_daily(
        digest.daily_digest,
        time.fromisoformat(settings.DAILY_DIGEST_TIME),
        name='DAILY_DIGEST')


def add_handlers(app: Application) -> None:
    """Adds handlers to the bot."""
    # Error handler.
    app.add_error_handler(error.handler)
    # Debug commands.
    for module in [debug, info]:
        app.add_handlers(module.create_handlers())
    # General chat handling.
    for module in [digest, request, schedule, welcome]:
        app.add_handlers(module.create_handlers())