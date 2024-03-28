from dynaconf import settings
from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, filters

from .menu import construct_main_menu, State
from .tournament import create_handlers as tournament_handlers
from .tournaments import create_handlers as tournaments_handlers
from utils import log


def create_handlers() -> list:
    """Creates handlers that shows admin commands."""
    return [ConversationHandler(
        entry_points=[
            CommandHandler('admin', admin_menu, filters.User(username=settings.ADMINS) & filters.ChatType.PRIVATE),
        ],
        states={
            State.MAIN_MENU: [
                CallbackQueryHandler(add_tournament_request, pattern="^" + State.ADDING_TOURNAMENT.name + "$"),
            ] + tournaments_handlers(),
            State.WAITING_FOR_TITLE: tournament_handlers(),
        },
        fallbacks=[
            CommandHandler('cancel', admin_menu),
            CommandHandler('exit', exit),
        ],
        allow_reentry=True,
        name="admin",
        persistent=True)]


async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """Shows admin menu."""
    log('admin_menu')
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(**construct_main_menu())
    else:
        await update.message.reply_text(**construct_main_menu())
    context.user_data['conversation'] = State.MAIN_MENU
    return State.MAIN_MENU


async def add_tournament_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """Adds a tournament."""
    log('add_tournament_request')
    await update.callback_query.answer()
    context.bot_data['tournament'] = ""
    context.bot_data.setdefault('tournaments', {})
    message = 'Please, enter the name of the tournament.'
    await update.callback_query.edit_message_text(message)
    return State.WAITING_FOR_TITLE


async def exit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exits the admin menu."""
    log('exit')
    message = (
        'You exited the admin menu. You can return to it at any time '
        'by typing or pressing the /admin command.')
    await update.message.reply_text(message)
    return ConversationHandler.END