from dynaconf import settings
from enum import Enum
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils import log


State = Enum('State', [
    # Menu state:
    'MAIN_MENU',
    'TOURNAMENTS',
    # Particular states:
    'ADDING_TOURNAMENT', 
])


def construct_main_menu() -> dict:
    log('construct_main_menu')
    text = 'What do you want to do?'
    keyboard = [[
        InlineKeyboardButton("Add Tournament", callback_data=State.ADDING_TOURNAMENT.name),
        InlineKeyboardButton("Show Tournaments", callback_data=State.TOURNAMENTS.name)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return {'text': text, 'reply_markup': reply_markup}
