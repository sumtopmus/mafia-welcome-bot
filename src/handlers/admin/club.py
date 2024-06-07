from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler

from utils import log
from .menu import State, construct_back_button, construct_club_menu, construct_main_menu, construct_deletion_menu


def create_handlers() -> list:
    """Creates handlers that process all club settings."""
    return [ConversationHandler(
        entry_points= [
            CallbackQueryHandler(club_menu, pattern="^" + State.CLUB_MENU.name + "$")],
        states={
            State.CLUB_MENU: [
                CallbackQueryHandler(change_name_request, pattern="^" + State.CLUB_CHANGING_NAME.name + "$"),
                CallbackQueryHandler(delete_request, pattern="^" + State.DELETING.name + "$"),
                CallbackQueryHandler(back, pattern="^" + State.MAIN_MENU.name + "$"),
            ],
            State.CLUB_CHANGING_NAME: [
            ],
            State.DELETING: [
                CallbackQueryHandler(delete, pattern="^" + State.DELETING.name + "$"),
                CallbackQueryHandler(club_menu, pattern="^" + State.CLUB_MENU.name + "$")                
            ],
            State.BACK_BUTTON: [
                CallbackQueryHandler(club_menu, pattern="^" + State.CLUB_MENU.name + "$")
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel)
        ],
        allow_reentry=True,
        name="admin_club_menu",
        persistent=True)]


async def club_menu(update: Update, context: CallbackContext) -> State:
    """When an admin goes to the club menu."""
    log('main_menu')
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(**construct_club_menu(context))
    else:
        await update.message.reply_text(**construct_club_menu(context))
    context.user_data['state'] = State.CLUB_MENU
    return State.CLUB_MENU


async def change_name_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When user tries to change the club name."""
    log('change_name_request')
    await update.callback_query.answer()
    # TODO: implement
    return State.CLUB_MENU


async def delete_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When user tries to delete the tournament."""
    log('delete_request')
    await update.callback_query.answer()
    club_name = context.user_data['club']
    menu = construct_deletion_menu(club_name, State.CLUB_MENU)
    await update.callback_query.edit_message_text(**menu)
    return State.DELETING


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When user tries to delete the tournament."""
    log('delete')
    await update.callback_query.answer()
    club_name = context.user_data['club']
    del context.bot_data['clubs'][club_name]
    context.user_data['admin'].remove(club_name)
    message = f'{club_name} was successfully deleted.'
    menu = construct_back_button(message, context, State.MAIN_MENU)
    await update.callback_query.edit_message_text(**menu)
    context.user_data['conversation'] = State.MAIN_MENU    
    return State.MAIN_MENU


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user presses a back button."""
    log('back')
    await update.callback_query.answer()
    menu = construct_main_menu(context)
    await update.callback_query.edit_message_text(**menu)
    return State.MAIN_MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user cancels the conversation."""
    log('cancel')
    message = 'Exiting the admin menu...'
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(message)
    else:
        await update.message.reply_text(message)
    return ConversationHandler.END