from dynaconf import settings
import logging
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, filters

from .menu import construct_main_menu, State
from utils import log


def create_handlers() -> list:
    """Creates handlers that shows admin commands."""
    return [ConversationHandler(
        entry_points=[
            CommandHandler('admin', admin, filters.User(username=settings.ADMINS) & filters.ChatType.PRIVATE),
        ],
        states={
            State.MAIN_MENU: [],
        },
        fallbacks=[
            CommandHandler('cancel', cancel, ~filters.Chat(settings.CHAT_ID)),
        ],
        allow_reentry=True,
        conversation_timeout=settings.CONVERSATION_TIMEOUT,
        name="admin",
        persistent=True)]


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows admin menu."""
    log('admin')
    menu = construct_main_menu()
    await update.message.reply_text(**menu)
    return State.MAIN_MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Exits admin menu."""
    log('cancel')
    return ConversationHandler.END