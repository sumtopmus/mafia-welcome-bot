from dynaconf import settings
from enum import Enum
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .common import get_tournament
from utils import log


State = Enum('State', [
    # Menu state:
    'MAIN_MENU',
    'TOURNAMENTS',
    'TOURNAMENT',
    # Particular states:
    'ADDING_TOURNAMENT',
    'WAITING_FOR_TITLE',
    'FINDING_TOURNAMENT',
    'EDITING_TITLE',
    'REGISTRATION',
    'DELETING_TOURNAMENT',
])


def construct_main_menu() -> dict:
    log('construct_main_menu')
    text = 'What do you want to do?'
    keyboard = [[
        InlineKeyboardButton("Add Tournament", callback_data=State.ADDING_TOURNAMENT.name),
        InlineKeyboardButton("Show Tournaments", callback_data=State.TOURNAMENTS.name)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return {'text': text, 'reply_markup': reply_markup}


def construct_tournaments_menu(context: ContextTypes.DEFAULT_TYPE, pattern=None) -> dict:
    log('construct_tournaments_menu')
    text = 'Please, pick a tournament:'
    tournaments = context.bot_data.get('tournaments', {})
    titles = sorted(tournaments, key=lambda x: tournaments[x]['timestamp'], reverse=True)
    previous_state = State.MAIN_MENU
    if pattern:
        regex = re.compile(pattern, re.IGNORECASE)
        titles = [title for title in titles if regex.search(title)]
        previous_state = State.TOURNAMENTS
    back_button = InlineKeyboardButton('« Back', callback_data=previous_state.name)
    if len(titles) == 0:
        reply_markup = InlineKeyboardMarkup([[back_button]])
        return {'text': 'No tournaments found.', 'reply_markup': reply_markup}
    keyboard, row = [], []
    for index, title in enumerate(titles):
        row.append(InlineKeyboardButton(title, callback_data=f'{State.TOURNAMENT.name}/{title}'))
        if len(row) == 2:
            keyboard.append(row.copy())
            row = []
        if index == 4:
            break
    row.append(InlineKeyboardButton('Find by name', callback_data=State.FINDING_TOURNAMENT.name))
    if len(row) == 2:
        keyboard.append(row.copy())
        row = []
    row.append(back_button)
    keyboard.append(row)
    reply_markup = InlineKeyboardMarkup(keyboard)
    return {'text': text, 'reply_markup': reply_markup}


def construct_tournament_menu(context: ContextTypes.DEFAULT_TYPE) -> dict:
    log('construct_tournament_menu')
    tournament = get_tournament(context)
    state = State(context.user_data['conversation'])
    text = f'What do you want to do with *{tournament['title']}*?'
    registration_button_text = 'Registration: ' + ('Open ✅' if tournament.get('registration', False) else 'Closed ❌')
    keyboard = [
        [
            InlineKeyboardButton("Edit Title", callback_data=State.EDITING_TITLE.name),
            InlineKeyboardButton(registration_button_text, callback_data=State.REGISTRATION.name),
        ],
        [
            InlineKeyboardButton("Delete ❌", callback_data=State.DELETING_TOURNAMENT.name),
            InlineKeyboardButton("« Back", callback_data=state.name)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return {'text': text, 'reply_markup': reply_markup}


def construct_deletion_menu(title) -> dict:
    log('construct_deletion_menu')
    text = f'Are you sure you want to delete {title}?'
    keyboard = [[
        InlineKeyboardButton("Yes 🗑️", callback_data=State.DELETING_TOURNAMENT.name),
        InlineKeyboardButton("No 🚫", callback_data=State.TOURNAMENT.name)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return {'text': text, 'reply_markup': reply_markup}