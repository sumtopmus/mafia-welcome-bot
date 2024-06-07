from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler

from utils import log
from .menu import State, construct_main_menu, construct_back_button, construct_clubs_menu


def create_handlers() -> list:
    """Creates handlers that process all admin requests."""
    return [ConversationHandler(
        entry_points= [CommandHandler('admin', main_menu)],
        states={
            State.MAIN_MENU: [
                CallbackQueryHandler(register_club_request, pattern="^" + State.CLUB_ADDING.name + "$"),
                CallbackQueryHandler(clubs_menu, pattern="^" + State.CLUB_PICKING.name + "$"),
            ],
            State.CLUBS_MENU: [
                CallbackQueryHandler(main_menu, pattern="^" + State.MAIN_MENU.name + "$")
            ],
            State.CLUB_WAITING_FOR_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_club_name)
            ],
            State.BACK_BUTTON: [
                CallbackQueryHandler(main_menu, pattern="^" + State.MAIN_MENU.name + "$")
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel)
        ],
        allow_reentry=True,
        name="admin_main_menu",
        persistent=True)]


async def main_menu(update: Update, context: CallbackContext) -> State:
    """When a user goes to the main menu."""
    log('main_menu')
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(**construct_main_menu())
    else:
        await update.message.reply_text(**construct_main_menu())
    context.user_data['state'] = State.MAIN_MENU
    return State.MAIN_MENU


async def clubs_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    log('clubs_menu')
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(**construct_clubs_menu(context))
    else:
        await update.message.reply_text(**construct_clubs_menu(context))
    context.user_data['state'] = State.CLUBS_MENU
    return State.CLUBS_MENU


async def register_club_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user wants to register a club."""
    log('register_club_request')
    await update.callback_query.answer()
    message = 'Please, enter the name of the club you want to register.'
    await update.callback_query.edit_message_text(message)
    return State.CLUB_WAITING_FOR_NAME


async def set_club_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user enters the club name."""
    log('set_club_name')
    title = update.message.text
    if title in context.bot_data['clubs']:
        message = f"The club \"{title}\" is already registered."
    else:
        context.bot_data['clubs'][title] = {
            'id': get_next_club_id(context),
            'admins': [update.effective_user.id],
        }
        context.user_data.setdefault('admin', []).append(title)
        message = f"The club \"{title}\" was successfully registered."
    await update.message.reply_text(
        **construct_back_button(message, context, State.MAIN_MENU))
    return State.BACK_BUTTON


def get_next_club_id(context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns the next available club id."""
    log(context.bot_data['clubs'].items())
    max_club_id = max(
        [club['id'] for _, club in context.bot_data['clubs'].items()],
        default=-1)
    log(f'max club id: {max_club_id}')
    return max_club_id + 1


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user cancels the conversation."""
    log('cancel')
    message = 'Exiting the admin menu...'
    await update.message.reply_text(message)
    return ConversationHandler.END