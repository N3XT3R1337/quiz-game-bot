from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.questions import CATEGORIES, DIFFICULTIES, Question


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎮 New Game", callback_data="new_game"),
        InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 My Stats", callback_data="my_stats"),
        InlineKeyboardButton(text="⚙️ Settings", callback_data="settings"),
    )
    builder.row(
        InlineKeyboardButton(text="❓ Help", callback_data="help"),
    )
    return builder.as_markup()


def get_category_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in CATEGORIES.items():
        builder.row(InlineKeyboardButton(text=label, callback_data=f"cat:{key}"))
    builder.row(InlineKeyboardButton(text="🎲 Mixed (All Categories)", callback_data="cat:mixed"))
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu"))
    return builder.as_markup()


def get_difficulty_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in DIFFICULTIES.items():
        builder.row(InlineKeyboardButton(text=label, callback_data=f"diff:{key}"))
    builder.row(InlineKeyboardButton(text="🎲 Mixed (All Difficulties)", callback_data="diff:mixed"))
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="back_to_category"))
    return builder.as_markup()


def get_answer_keyboard(question: Question, question_index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    labels = ["A", "B", "C", "D"]
    for i, option in enumerate(question.options):
        builder.row(
            InlineKeyboardButton(
                text=f"{labels[i]}. {option}",
                callback_data=f"ans:{question_index}:{i}",
            )
        )
    return builder.as_markup()


def get_join_game_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Join Game", callback_data=f"join:{chat_id}"),
        InlineKeyboardButton(text="▶️ Start Now", callback_data=f"start_now:{chat_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_game"),
    )
    return builder.as_markup()


def get_next_question_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏭ Next Question", callback_data="next_question"),
    )
    return builder.as_markup()


def get_play_again_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Play Again", callback_data="new_game"),
        InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard"),
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_menu"),
    )
    return builder.as_markup()


def get_leaderboard_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🌍 Global", callback_data="lb:global"),
        InlineKeyboardButton(text="📅 Weekly", callback_data="lb:weekly"),
    )
    for key, label in list(CATEGORIES.items())[:4]:
        builder.row(InlineKeyboardButton(text=f"🏅 {label}", callback_data=f"lb:{key}"))
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu"))
    return builder.as_markup()


def get_settings_keyboard(current_rounds: int, current_timeout: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"🔢 Rounds: {current_rounds}",
            callback_data="setting:rounds",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"⏱ Timeout: {current_timeout}s",
            callback_data="setting:timeout",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu"),
    )
    return builder.as_markup()


def get_rounds_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for count in [5, 10, 15, 20]:
        builder.add(
            InlineKeyboardButton(text=str(count), callback_data=f"rounds:{count}")
        )
    builder.adjust(4)
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="settings"))
    return builder.as_markup()


def get_timeout_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for seconds in [15, 20, 30, 45, 60]:
        builder.add(
            InlineKeyboardButton(text=f"{seconds}s", callback_data=f"timeout:{seconds}")
        )
    builder.adjust(5)
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="settings"))
    return builder.as_markup()
