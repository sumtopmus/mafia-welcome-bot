from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler

from .menu import State, construct_main_menu, construct_tournaments_menu
from .tournament import create_handlers as tournament_handlers
from utils import log


def create_handlers() -> list:
    """Creates handlers that show the list of tournaments."""
    return [ConversationHandler(
        entry_points=[
            CallbackQueryHandler(show, pattern="^" + State.TOURNAMENTS.name + "$")
        ],
        states={
            State.TOURNAMENTS: [
                CallbackQueryHandler(find_tournament, pattern="^" + State.FINDING_TOURNAMENT.name + "$"),
                CallbackQueryHandler(back, pattern="^" + State.MAIN_MENU.name + "$"),
            ] + tournament_handlers(),
            State.FINDING_TOURNAMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, show_by_pattern),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', show),
        ],
        allow_reentry=True,
        map_to_parent={
            State.MAIN_MENU: State.MAIN_MENU
        },
        name="tournaments",
        persistent=True)]


async def show(update: Update, context: CallbackContext) -> None:
    """Processes show command."""
    log('show')    
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(**construct_tournaments_menu(context))
    context.user_data['conversation'] = State.TOURNAMENTS
    return State.TOURNAMENTS


async def find_tournament(update: Update, context: CallbackContext) -> None:
    """Processes find_tournament command."""
    log('find_tournament')
    await update.callback_query.answer()
    message = 'Please, enter the name of the tournament.'
    await update.callback_query.edit_message_text(message)
    return State.FINDING_TOURNAMENT


async def show_by_pattern(update: Update, context: CallbackContext) -> None:
    """Displays tournaments that match the entered pattern."""
    log('show_by_pattern')
    title_pattern = update.message.text
    await update.message.reply_text(**construct_tournaments_menu(context, title_pattern))
    return State.TOURNAMENTS


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user presses the back button."""
    log('back')
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(**construct_main_menu())
    return State.MAIN_MENU
