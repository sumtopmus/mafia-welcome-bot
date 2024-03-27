from datetime import datetime
from dynaconf import settings
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, filters

from utils import log


def create_handlers() -> list:
    """Creates handlers that process `schedule` command."""
    return [CommandHandler('schedule', schedule)]


async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """When user uses the `schedule` command."""
    log('schedule')
    message = ''
    dow = datetime.now().weekday()
    if dow == 0:
        message = 'Сегодня у нас дружеский стёб 🌚'
    elif dow == 1:
        message = 'Обсуждаем игры в инетке'
    elif dow == 2:
        message = 'Да будет Срач!!!'
    elif dow == 3:
        message = 'Рабочий день'
    elif dow == 4:
        message = 'Обсуждение философских вопросов'
    elif dow == 5:
        message = 'Пьём Маргариту и играем в баланс'
    elif dow == 6:
        message = 'Жива или мертва американская мафия?\n\nКто едет в Сакраменто?'
    await update.effective_chat.send_photo(settings.SCHEDULE_ID, caption=message)