from dynaconf import settings
from enum import Enum
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils import log


State = Enum('State', [
    # Menu state:
    'MAIN_MENU',
    'BACK_BUTTON',
    # Process states:
    'ADDING_CLUB',
    'WAITING_FOR_CLUB_NAME',
])


def construct_main_menu() -> dict:
    log('construct_main_menu')
    text = 'What do you want to do?'
    keyboard = [[
        InlineKeyboardButton("Register a club", callback_data=State.ADDING_CLUB.name)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return {'text': text, 'reply_markup': reply_markup}


def construct_back_button(text: str, context: ContextTypes.DEFAULT_TYPE, state: State) -> dict:
    log('construct_back_button')
    keyboard = [[InlineKeyboardButton("« Back", callback_data=state.name)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return {'text': text, 'reply_markup': reply_markup}
