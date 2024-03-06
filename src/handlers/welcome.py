# coding=UTF-8

from dynaconf import settings
import logging
from telegram import Update
from telegram.ext import ContextTypes, filters, MessageHandler

import utils


def create_handlers() -> list:
    """Creates handlers that process new users."""
    return [MessageHandler(
        filters.Chat(settings.CHAT_ID) & filters.StatusUpdate.NEW_CHAT_MEMBERS,
        welcome)]


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When new user enters the chat."""
    utils.log('welcome')
    for user in update.message.new_chat_members:
        utils.log(f'new user: {user.id} ({user.full_name})', logging.INFO)
        if user.is_bot:
            utils.log(f'new user is a bot')
            continue
        titled_mention = context.bot_data['players'][user.id]['nickname']
        title = context.bot_data['players'][user.id]['title']
        if title:
            titled_mention = title + ' ' + titled_mention
        if context.bot_data['players'][user.id]['introduced']:
            utils.log(f'user {user.id} already introduced themselves', logging.INFO)
            message = (
                'Вы только посмотрите, кто к нам вернулся! Аплодисменты!\n\n'
                f'Встречайте – {titled_mention} ({user.mention_markdown()})!')
            await context.bot.sendMessage(
                chat_id=update.message.chat.id, text=message,
                reply_to_message_id=update.message.id)
            continue
        handle = user.username if user.username else user.full_name
        message = (
            'В нашей большой семье AML пополнение!\n\n'
            f'Встречайте – {titled_mention} ({user.mention_markdown()})!\n\n'
            f'*Город:* {context.bot_data['players'][user.id]['city']}\n'
            f'*Клуб:* {context.bot_data['players'][user.id]['club']}\n'
            f'*Стаж:* {context.bot_data['players'][user.id]['experience']}')
        await context.bot.sendMessage(
            chat_id=update.message.chat.id, text=message,
            reply_to_message_id=update.message.id)
        context.bot_data['players'][user.id]['introduced'] = True
    return
