from telegram.ext import ContextTypes


def get_tournament(context: ContextTypes.DEFAULT_TYPE) -> dict:
    """Gets a tournament from the bot data."""
    title = context.user_data.get('tournament', None)
    if title is None:
        return None
    return context.bot_data['tournaments'][title]