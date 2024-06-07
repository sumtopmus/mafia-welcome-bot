from datetime import datetime
from enum import Enum
from telegram import  InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, ChatJoinRequestHandler, CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler, TypeHandler
from telegram.error import TelegramError

from config import settings
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
        entry_points=[
            ChatJoinRequestHandler(join_request, chat_id=settings.CHAT_ID),
            CommandHandler('join', join_request, ~filters.Chat(settings.CHAT_ID)),
        ],
        states={
            State.WAITING_FOR_NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_nickname)],
            State.WAITING_FOR_TITLE: [CallbackQueryHandler(set_title)],
            State.WAITING_FOR_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_city)],
            State.WAITING_FOR_CLUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_club)],
            State.WAITING_FOR_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_experience)],
            ConversationHandler.TIMEOUT: [TypeHandler(Update, timeout)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel, ~filters.Chat(settings.CHAT_ID)),
        ],
        allow_reentry=True,
        conversation_timeout=settings.CONVERSATION_TIMEOUT,
        name="welcome",
        per_chat=False,
        persistent=True)]


async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a join request is sent."""
    log('join_request')
    user = update.effective_user
    # TODO: temporary solution, should be removed after all the user data is updated
    if user.id in context.bot_data['players'] and context.bot_data['players'][user.id]['introduced']:
        context.bot_data['players'][user.id]['answered'] = True
    else:
        context.bot_data['players'][user.id]['answered'] = False
    # END
    if user.id in context.bot_data['players'] and context.bot_data['players'][user.id]['answered']:
        await user.approve_join_request(settings.CHAT_ID)
        return ConversationHandler.END
    context.bot_data['players'].setdefault(user.id, {'first_join_timestamp': datetime.now().isoformat()})
    context.bot_data['players'][user.id]['answered'] = False
    context.bot_data['players'][user.id]['introduced'] = False
    message = (f'Доброе утро, {user.full_name}! American Mafia League приветствует вас! '
        'Подписывайтесь на наш канал, чтобы следить за событиями в AML.\n\n'
        'Чтобы попасть в наш чат, вам придётся заполнить небольшую анкету.\n\n'
        'Начнём с самого важного: ваш игровой ник?')
    channel = await context.bot.get_chat(settings.CHANNEL_USERNAME)
    keyboard = [[InlineKeyboardButton(text='Подписаться на канал', url=channel.link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await user.send_message(message, reply_markup=reply_markup)
    return State.WAITING_FOR_NICKNAME


async def set_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When the nickname is submitted."""
    log('set_nickname')
    nickname = update.message.text
    context.bot_data['players'][update.effective_user.id]['nickname'] = nickname
    message = (f'Какое обращение вы предпочитаете?')
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
    await update.callback_query.answer()
    if update.callback_query.data == Action.MR.name:
        context.bot_data['players'][update.effective_user.id]['title'] = 'г-н'
    elif update.callback_query.data == Action.MS.name:
        context.bot_data['players'][update.effective_user.id]['title'] = 'г-жа'
    else:
        context.bot_data['players'][update.effective_user.id]['title'] = None
    message = (f'В каком городе вы проживаете?')
    await update.callback_query.edit_message_text(message)
    return State.WAITING_FOR_CITY


async def set_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When the city is submitted."""
    log('set_city')
    context.bot_data['players'][update.effective_user.id]['city'] = update.message.text
    message = (f'В каком клубе вы играете?')
    await update.message.reply_text(message)
    return State.WAITING_FOR_CLUB


async def set_club(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When the club is submitted."""
    log('set_club')
    context.bot_data['players'][update.effective_user.id]['club'] = update.message.text
    message = (f'Как давно вы играете в спортивную мафию?')
    await update.message.reply_text(message)
    return State.WAITING_FOR_EXPERIENCE


async def set_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When the experience is submitted."""
    log('set_experience')
    context.bot_data['players'][update.effective_user.id]['experience'] = update.message.text
    context.bot_data['players'][update.effective_user.id]['answered'] = True
    try:
        await update.effective_user.approve_join_request(settings.CHAT_ID)
    except TelegramError as e:
        log(f'No join requests found: {e}')
    message = (f'Спасибо за анкету! Теперь вы можете пользоваться нашим чатом.')
    keyboard = [[InlineKeyboardButton(text='Перейти к чату', url=settings.CHAT_INVITE_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)
    return ConversationHandler.END


async def timeout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When the conversation timepout is exceeded."""
    log('timeout')
    message = (
        'Уже прошли сутки, а вы всё ещё не заполнили анкету. '
        'Мы отклоняем вашу заявку, но вы всегда можете податься '
        'снова, нажав /join.')
    await update.effective_user.send_message(message)
    await update.effective_user.decline_join_request(settings.CHAT_ID)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When a user cancels the process."""
    log('cancel')
    message = 'Вы можете заполнить анкету снова, нажав /join.'
    await update.message.reply_text(message)
    if update.chat_join_request:
        await update.chat_join_request.from_user.decline_join_request(
            update.chat_join_request.chat.id)
    return ConversationHandler.END