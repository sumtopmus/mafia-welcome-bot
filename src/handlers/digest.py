from datetime import datetime
from dynaconf import settings
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, filters, MessageHandler

from utils import log


def create_handlers() -> list:
    """Creates handlers that process `digest` command."""
    return [
        CommandHandler('digest', digest, filters.User(username=settings.ADMINS)),
        MessageHandler((filters.TEXT | filters.CAPTION) & ~filters.COMMAND & filters.Chat(settings.CHAT_ID), log_message),
    ]


async def log_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logs message sent to the chat."""
    log('log_message')
    if update.message.text:
        context.bot_data['messages'].append({
            'name': update.effective_user.full_name,
            'text': update.message.text
        })
    elif update.message.caption:
        context.bot_data['messages'].append({
            'name': update.effective_user.full_name,
            'text': update.message.caption
        })
    

async def digest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Basic admin digest command."""
    log('digest')
    latest_digest = datetime.fromisoformat(context.bot_data['latest_digest']['timestamp'])
    if (datetime.now() - latest_digest).total_seconds() < settings.SLOW_MODE:
        await update.message.reply_text(
            'Посмотри последний дайджест, он был не так давно.',
            reply_to_message_id=context.bot_data['latest_digest']['message_id'])
    else:
        message = 'Дайджест чата:\n\n' + '\n'.join(f"{m['name']}: {m['text']}" for m in context.bot_data['messages'][-10:]) \
            + '\n\n_#digest_'
        bot_message = await update.message.reply_text(message)
        context.bot_data['latest_digest']['timestamp'] = datetime.now().isoformat()
        context.bot_data['latest_digest']['message_id'] = bot_message.message_id
        context.bot_data['messages'] = []


async def daily_digest(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send morning message and add a new timer."""
    log('daily_digest')
    message = 'Ежедневный дайджест:\n\n' + '\n'.join(f"{m['name']}: {m['text']}" for m in context.bot_data['messages'][-10:]) \
        + '\n\n_#digest #daily_'
    await context.bot.sendMessage(chat_id=settings.DIGEST_CHAT_ID, text=message)
    context.bot_data['messages'] = []