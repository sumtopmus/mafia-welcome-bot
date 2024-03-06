from datetime import datetime
from dynaconf import settings
from enum import Enum
from telegram import  InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, ChatJoinRequestHandler, CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler

from utils import log


Action = Enum('Action', [
    # Button action:
    'SKIP',
    'MR',
    'MS'
])


State = Enum('State', [
    # Particular states:
    'WAITING_FOR_NICKNAME',
    'WAITING_FOR_TITLE',
    'WAITING_FOR_CITY',
    'WAITING_FOR_CLUB',
    'WAITING_FOR_EXPERIENCE'
])


def create_handlers() -> list:
    """Creates handlers that process join requests."""
    return [ConversationHandler(
        entry_points=[ChatJoinRequestHandler(join_request, chat_id=settings.CHAT_ID)],
        states={
            State.WAITING_FOR_NICKNAME: [MessageHandler(filters.ALL, set_nickname)],
            State.WAITING_FOR_TITLE: [CallbackQueryHandler(set_title)],
            State.WAITING_FOR_CITY: [MessageHandler(filters.ALL, set_city)],
            State.WAITING_FOR_CLUB: [MessageHandler(filters.ALL, set_club)],
            State.WAITING_FOR_EXPERIENCE: [MessageHandler(filters.ALL, set_experience)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
        ],
        name="welcome",
        per_chat=False,
        persistent=True)]


async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a join request is sent."""
    log('join_request')
    user = update.chat_join_request.from_user
    if user.id in context.bot_data['players'] and context.bot_data['players'][user.id]['introduced']:
        await user.approve_join_request(settings.CHAT_ID)
        return ConversationHandler.END
    context.bot_data['players'].setdefault(user.id, {'first_join_timestamp': datetime.now().isoformat()})
    context.bot_data['players'][user.id]['introduced'] = False
    message = (f'Доброе утро, {user.full_name}! American Mafia League приветствует тебя! '
        'Подписывайся на наш канал, чтобы следить за событиями в AML.\n\n'
        'Чтобы попасть в наш чат, тебе придётся заполнить небольшую анкету.\n\n'
        'Начнём с простого: твой игровой ник?')
    channel = await context.bot.get_chat(settings.CHANNEL_USERNAME)
    keyboard = [[InlineKeyboardButton(text='Подписаться на канал', url=channel.link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.chat_join_request.from_user.send_message(message, reply_markup=reply_markup)
    return State.WAITING_FOR_NICKNAME


async def set_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When the nickname is submitted."""
    log('set_nickname')
    user = update.message.from_user
    nickname = update.message.text
    context.bot_data['players'][user.id]['nickname'] = nickname
    message = (f'Какое обращение ты предпочитаешь?')
    keyboard = [
        [
            InlineKeyboardButton("Г-н", callback_data=Action.MR.name),
            InlineKeyboardButton("Г-жа", callback_data=Action.MS.name),
        ],
        [
            InlineKeyboardButton("Пропустить", callback_data=Action.SKIP.name)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)
    return State.WAITING_FOR_TITLE


async def set_title(update: Update, context: CallbackContext) -> State:
    """When the title is submitted."""
    log('set_title')
    user = update.callback_query.from_user
    await update.callback_query.answer()
    if update.callback_query.data == Action.MR.name:
        context.bot_data['players'][user.id]['title'] = 'г-н'        
    elif update.callback_query.data == Action.MS.name:
        context.bot_data['players'][user.id]['title'] = 'г-жа'
    else:
        context.bot_data['players'][user.id]['title'] = None
    message = (f'Из какого ты города?')
    await update.callback_query.edit_message_text(message)
    return State.WAITING_FOR_CITY


async def set_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When the city is submitted."""
    log('set_city')
    user = update.message.from_user
    context.bot_data['players'][user.id]['city'] = update.message.text
    message = (f'В каком клубе ты играешь?')
    await update.message.reply_text(message)
    return State.WAITING_FOR_CLUB


async def set_club(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When the club is submitted."""
    log('set_club')
    user = update.message.from_user
    context.bot_data['players'][user.id]['club'] = update.message.text
    message = (f'Как давно ты играешь в спортивную мафию?')
    await update.message.reply_text(message)
    return State.WAITING_FOR_EXPERIENCE


async def set_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When the experience is submitted."""
    log('set_experience')
    user = update.message.from_user
    context.bot_data['players'][user.id]['experience'] = update.message.text
    await user.approve_join_request(settings.CHAT_ID)
    message = (f'Спасибо за анкету! Теперь ты можешь пользоваться нашим чатом.')
    keyboard = [[InlineKeyboardButton(text='Перейти к чату', url=settings.CHAT_INVITE_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When a user cancels the process."""
    log('cancel')
    message = 'Ты можешь попробовать снова позже.'
    await update.message.reply_text(message)
    await update.chat_join_request.from_user.decline_join_request(
        update.chat_join_request.chat.id)
    return ConversationHandler.END