from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.keyboards.game_kb import get_leaderboard_keyboard, get_main_menu_keyboard
from bot.questions import CATEGORIES
from bot.services.score_service import score_service

router = Router()


@router.message(Command("leaderboard"))
async def cmd_leaderboard(message: Message):
    await message.answer(
        "🏆 Leaderboards\n\nSelect a leaderboard to view:",
        reply_markup=get_leaderboard_keyboard(),
    )


@router.callback_query(F.data == "leaderboard")
async def leaderboard_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏆 Leaderboards\n\nSelect a leaderboard to view:",
        reply_markup=get_leaderboard_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lb:"))
async def show_leaderboard(callback: CallbackQuery):
    lb_type = callback.data.split(":")[1]

    if lb_type == "global":
        entries = await score_service.get_global_leaderboard()
        title = "🌍 Global Leaderboard"
    elif lb_type == "weekly":
        entries = await score_service.get_global_leaderboard(limit=10)
        title = "📅 Weekly Leaderboard"
    else:
        entries = await score_service.get_category_leaderboard(lb_type)
        category_name = CATEGORIES.get(lb_type, lb_type)
        title = f"🏅 {category_name} Leaderboard"

    text = score_service.format_leaderboard(entries, title)
    await callback.message.edit_text(
        text,
        reply_markup=get_leaderboard_keyboard(),
    )
    await callback.answer()
