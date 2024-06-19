import logging
from telegram import Update
from telegram.ext import ContextTypes, filters, MessageHandler

from config import settings
from utils import log


def create_handlers() -> list:
    """Creates handlers that process new users."""
    return [MessageHandler(
        filters.Chat(settings.CHAT_ID) & filters.StatusUpdate.NEW_CHAT_MEMBERS,
        welcome)]


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When new user enters the chat."""
    log('welcome')
    for user in update.message.new_chat_members:
        log(f'{user.id} ({user.full_name}) join the chat', logging.INFO)
        if user.is_bot:
            log(f'new user is a bot')
            continue
        if user.id not in context.bot_data['players']:
            log(f'no data for accepted user {user.id} ({user.full_name})', logging.INFO)
            continue
        titled_mention = context.bot_data['players'][user.id]['nickname']
        title = context.bot_data['players'][user.id]['title']
        if title:
            titled_mention = title + ' ' + titled_mention
        if context.bot_data['players'][user.id]['introduced']:
            log(f'user {user.id} already introduced themselves', logging.INFO)
            message = (
                'Вы только посмотрите, кто к нам вернулся! Аплодисменты!\n\n'
                f'Встречайте – {titled_mention} ({user.mention_markdown()})!')
            await context.bot.sendMessage(
                chat_id=update.message.chat.id, text=message,
                reply_to_message_id=update.message.id)
            continue
        message = (
            "В нашей большой семье AML пополнение!\n\n"
            f"Встречайте – {titled_mention} ({user.mention_markdown()})!\n\n"
            f"*Город:* {context.bot_data['players'][user.id]['city']}\n"
            f"*Клуб:* {context.bot_data['players'][user.id]['club']}\n"
            f"*Стаж:* {context.bot_data['players'][user.id]['experience']}\n\n"
            "_#about_")
        await context.bot.sendMessage(
            chat_id=update.message.chat.id, text=message,
            reply_to_message_id=update.message.id)
        context.bot_data['players'][user.id]['introduced'] = True
    return
