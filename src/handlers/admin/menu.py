from dynaconf import settings
from enum import Enum
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils import log


State = Enum('State', [
    # Menu state:
    'MAIN_MENU',
    'CLUBS_MENU',
    'BACK_BUTTON',
    # General states:
    'DELETING',
    # Prefix states:
    'CLUB',
    # Process states:
    'CLUB_ADDING',
    'CLUB_PICKING',
    'CLUB_WAITING_FOR_NAME',
    'CLUB_CHANGING_NAME',
])


def construct_main_menu() -> dict:
    log('construct_main_menu')
    text = 'What do you want to do?'
    keyboard = [
        [
            InlineKeyboardButton("Register a Club", callback_data=State.CLUB_ADDING.name),
            InlineKeyboardButton("Club Settings", callback_data=State.CLUB_PICKING.name),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return {'text': text, 'reply_markup': reply_markup}


def construct_clubs_menu(context: ContextTypes.DEFAULT_TYPE) -> dict:
    log('construct_clubs_menu')
    text = 'Please, pick a club:'
    clubs = context.user_data.get('admin', [])
    back_button = InlineKeyboardButton('« Back', callback_data=State.MAIN_MENU.name)
    if len(clubs) == 0:
        reply_markup = InlineKeyboardMarkup([[back_button]])
        return {'text': 'There are no clubs that you can manage.', 'reply_markup': reply_markup}
    keyboard = []
    row = []
    for index, title in enumerate(clubs):
        row.append(InlineKeyboardButton(title, callback_data=f'{State.CLUB.name}/{title}'))
        if len(row) == 2:
            keyboard.append(row.copy())
            row = []
        if index == 3:
            break
    row.append(back_button)
    keyboard.append(row)
    reply_markup = InlineKeyboardMarkup(keyboard)
    return {'text': text, 'reply_markup': reply_markup}


def construct_club_menu() -> dict:
    log('construct_club_menu')
    text = 'What do you want to do?'
    keyboard = [
        [
            InlineKeyboardButton("Change Name", callback_data=State.CLUB_CHANGING_NAME.name),
            InlineKeyboardButton("❌ Delete Club", callback_data=State.CLUB_DELETING.name),
        ],
        [
            InlineKeyboardButton("« Back", callback_data=State.MAIN_MENU.name),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return {'text': text, 'reply_markup': reply_markup}


def construct_deletion_menu(entity_name: str, reset_state: State) -> dict:
    log('construct_deletion_menu')
    text = f'Are you sure you want to delete {entity_name}?'
    keyboard = [[
        InlineKeyboardButton("Yes 🗑️", callback_data=State.DELETING.name),
        InlineKeyboardButton("No 🚫", callback_data=reset_state.name)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return {'text': text, 'reply_markup': reply_markup}


def construct_back_button(text: str, context: ContextTypes.DEFAULT_TYPE, state: State) -> dict:
    log('construct_back_button')
    keyboard = [[InlineKeyboardButton("« Back", callback_data=state.name)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return {'text': text, 'reply_markup': reply_markup}
