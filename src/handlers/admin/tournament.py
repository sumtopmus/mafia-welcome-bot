from datetime import datetime
from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler
from telegram.helpers import escape_markdown

from .common import get_tournament
from .menu import State, construct_main_menu, construct_tournament_menu, construct_tournaments_menu, construct_deletion_menu
from utils import log


def create_handlers() -> list:
    """Creates handlers that edit a tournament."""
    return [ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & ~filters.COMMAND, set_title),
            CallbackQueryHandler(pick_tournament, pattern="^" + State.TOURNAMENT.name + "/")
        ],
        states={
            State.TOURNAMENT: [
                CallbackQueryHandler(title_edit_request, pattern="^" + State.EDITING_TITLE.name + "$"),
                CallbackQueryHandler(registration_change, pattern="^" + State.REGISTRATION.name + "$"),
                CallbackQueryHandler(delete_request, pattern="^" + State.DELETING_TOURNAMENT.name + "$"),
                CallbackQueryHandler(back, pattern="^" + State.TOURNAMENTS.name + "$"),
                CallbackQueryHandler(back_to_main_menu, pattern="^" + State.MAIN_MENU.name + "$"),                
            ],
            State.EDITING_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, title_edit)
            ],
            State.DELETING_TOURNAMENT: [
                CallbackQueryHandler(delete, pattern="^" + State.DELETING_TOURNAMENT.name + "$"),
                CallbackQueryHandler(tournament_menu, pattern="^" + State.TOURNAMENT.name + "$")
            ]
        },
        fallbacks=[
            CommandHandler('cancel', tournament_menu)
        ],
        map_to_parent={
            State.MAIN_MENU: State.MAIN_MENU,
            State.TOURNAMENTS: State.TOURNAMENTS
        },
        name="edit_tournament_conversation",
        persistent=True)]


async def tournament_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When user presses the tournament button."""
    log('tournament_menu')
    menu = construct_tournament_menu(context)
    if update.callback_query:
        await update.callback_query.edit_message_text(**menu)
    else:
        await update.message.reply_text(**menu)
    return State.TOURNAMENT


async def pick_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When user presses a tournament button."""
    log('pick_tournament')
    await update.callback_query.answer()
    title = update.callback_query.data.split('/')[1]
    context.user_data['tournament'] = title
    await tournament_menu(update, context)
    return State.TOURNAMENT


async def set_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user adds a title."""
    log('set_title')
    title = update.message.text
    context.user_data['tournament'] = title
    context.bot_data['tournaments'].setdefault(title, {})
    tournament = get_tournament(context)
    tournament['title'] = title
    tournament['timestamp'] = datetime.now().isoformat()
    await tournament_menu(update, context)
    return State.TOURNAMENT


async def title_edit_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user requests to edit a title."""
    log('edit_title')
    message = 'Please, enter the new title of the tournament.'
    await update.callback_query.edit_message_text(message)
    return State.EDITING_TITLE


async def title_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When user edits a title."""
    log('delete')
    old_title = context.user_data['tournament']
    new_title = update.message.text
    if new_title != old_title:
        context.bot_data['tournaments'][new_title] = context.bot_data['tournaments'][old_title].copy()
        context.bot_data['tournaments'][new_title]['title'] = new_title
        del context.bot_data['tournaments'][old_title]
        context.user_data['tournament'] = new_title
    await tournament_menu(update, context)
    return State.TOURNAMENT


async def registration_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user presses on a registration button."""
    log('registration_change')
    tournament = get_tournament(context)
    tournament['registration'] = not tournament.get('registration', False)
    await tournament_menu(update, context)
    return State.TOURNAMENT


async def delete_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When user tries to delete the tournament."""
    log('delete_request')
    await update.callback_query.answer()
    menu = construct_deletion_menu(context.user_data['tournament'])
    await update.callback_query.edit_message_text(**menu)
    return State.DELETING_TOURNAMENT


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When user tries to delete the tournament."""
    log('delete')
    title = context.user_data['tournament']
    await update.callback_query.answer(f'{title} was successfully deleted.')
    del context.bot_data['tournaments'][title]
    menu = construct_main_menu()
    await update.callback_query.edit_message_text(**menu)
    context.user_data['conversation'] = State.MAIN_MENU    
    return State.MAIN_MENU


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user presses the back button."""
    log('back')
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(**construct_tournaments_menu(context))
    return State.TOURNAMENTS


async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user presses the back button (to main menu)."""
    log('back_to_main_menu')
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(**construct_main_menu())
    context.user_data['conversation'] = State.MAIN_MENU    
    return State.MAIN_MENU
