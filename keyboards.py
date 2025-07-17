from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from config import MAJOR_CITIES
from utils import _

def settings_keyboard(lang: str, is_muted: bool) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(_("toggle_mute_on" if is_muted else "toggle_mute_off", lang), callback_data="toggle_mute")],
        [InlineKeyboardButton(_("change_city", lang), callback_data="choose_city")],
        [InlineKeyboardButton("English" if lang == "ar" else "العربية", callback_data="toggle_lang")],
        [InlineKeyboardButton(_("close", lang), callback_data="close")],
    ])

def main_menu_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[_("today", lang), _("settings", lang)]],
        resize_keyboard=True,
        input_field_placeholder=_("choose_from_menu", lang)
    )

def city_selection_keyboard(lang: str) -> InlineKeyboardMarkup:
    flat = MAJOR_CITIES.get(lang, MAJOR_CITIES["ar"])
    buttons = [
        [InlineKeyboardButton(city, callback_data=f"city_{city}") for city in flat[i : i + 2]]
        for i in range(0, len(flat), 2)
    ]
    buttons.append([InlineKeyboardButton(_("enter_city", lang), callback_data="enter_city")])
    buttons.append([InlineKeyboardButton(_("back", lang), callback_data="settings")])
    return InlineKeyboardMarkup(buttons)

def language_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("العربية", callback_data="set_lang_ar")],
        [InlineKeyboardButton("English", callback_data="set_lang_en")],
        [InlineKeyboardButton(_("back", lang), callback_data="settings")],
    ])

def after_city_selection_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(_("refresh", lang), callback_data="refresh")],
        [InlineKeyboardButton(_("settings", lang), callback_data="settings")],
    ])