from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.game_kb import get_main_menu_keyboard
from bot.services.score_service import score_service
from bot.states import GameStates

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await score_service.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    welcome_text = (
        "🎮 Welcome to Quiz Game Bot!\n\n"
        "Challenge your friends in multiplayer quiz battles!\n\n"
        "🔬 8 Categories | 🎯 3 Difficulty Levels\n"
        "🏆 Leaderboards | ⚡ Timed Questions\n\n"
        "Choose an option below to get started:"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "❓ Quiz Game Bot Help\n\n"
        "Commands:\n"
        "/start - Main menu\n"
        "/help - Show this help\n"
        "/stats - View your statistics\n"
        "/leaderboard - View leaderboards\n"
        "/cancel - Cancel current game\n\n"
        "How to play:\n"
        "1. Start a new game from the menu\n"
        "2. Select a category and difficulty\n"
        "3. Wait for players to join (or start solo)\n"
        "4. Answer questions before time runs out\n"
        "5. Earn points for correct and fast answers\n"
        "6. Build streaks for bonus points!\n\n"
        "Scoring:\n"
        "🟢 Easy: 10 pts | 🟡 Medium: 20 pts | 🔴 Hard: 30 pts\n"
        "⚡ Speed bonus: up to 5 extra pts\n"
        "🔥 Streak bonus: 2 × streak length"
    )
    await message.answer(help_text)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    stats = await score_service.get_user_stats(message.from_user.id)
    if not stats:
        await message.answer("📊 No stats yet. Play a game first!")
        return
    await message.answer(score_service.format_stats(stats))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    from bot.services.quiz_service import quiz_service
    quiz_service.cancel_game(message.chat.id)
    await state.clear()
    await message.answer(
        "❌ Game cancelled.\n\nUse /start to return to the main menu.",
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🎮 Quiz Game Bot\n\nChoose an option:",
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    help_text = (
        "❓ How to Play\n\n"
        "1. Tap 🎮 New Game\n"
        "2. Pick a category & difficulty\n"
        "3. Invite friends to join\n"
        "4. Answer questions fast!\n"
        "5. Check the 🏆 Leaderboard\n\n"
        "Points: Easy 10 | Medium 20 | Hard 30\n"
        "Speed & streak bonuses available!"
    )
    await callback.message.edit_text(
        help_text,
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "my_stats")
async def stats_callback(callback: CallbackQuery):
    stats = await score_service.get_user_stats(callback.from_user.id)
    if not stats:
        await callback.message.edit_text(
            "📊 No stats yet. Play a game first!",
            reply_markup=get_main_menu_keyboard(),
        )
        await callback.answer()
        return
    await callback.message.edit_text(
        score_service.format_stats(stats),
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "settings")
async def settings_callback(callback: CallbackQuery, state: FSMContext):
    from bot.keyboards.game_kb import get_settings_keyboard
    data = await state.get_data()
    rounds = data.get("rounds", 10)
    timeout = data.get("timeout", 30)
    await callback.message.edit_text(
        "⚙️ Game Settings\n\nAdjust settings for your next game:",
        reply_markup=get_settings_keyboard(rounds, timeout),
    )
    await callback.answer()


@router.callback_query(F.data == "setting:rounds")
async def setting_rounds(callback: CallbackQuery):
    from bot.keyboards.game_kb import get_rounds_keyboard
    await callback.message.edit_text(
        "🔢 Select number of rounds:",
        reply_markup=get_rounds_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "setting:timeout")
async def setting_timeout(callback: CallbackQuery):
    from bot.keyboards.game_kb import get_timeout_keyboard
    await callback.message.edit_text(
        "⏱ Select answer timeout:",
        reply_markup=get_timeout_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("rounds:"))
async def set_rounds(callback: CallbackQuery, state: FSMContext):
    from bot.keyboards.game_kb import get_settings_keyboard
    rounds = int(callback.data.split(":")[1])
    await state.update_data(rounds=rounds)
    data = await state.get_data()
    timeout = data.get("timeout", 30)
    await callback.message.edit_text(
        f"⚙️ Game Settings\n\n✅ Rounds set to {rounds}",
        reply_markup=get_settings_keyboard(rounds, timeout),
    )
    await callback.answer(f"Rounds set to {rounds}")


@router.callback_query(F.data.startswith("timeout:"))
async def set_timeout(callback: CallbackQuery, state: FSMContext):
    from bot.keyboards.game_kb import get_settings_keyboard
    timeout = int(callback.data.split(":")[1])
    await state.update_data(timeout=timeout)
    data = await state.get_data()
    rounds = data.get("rounds", 10)
    await callback.message.edit_text(
        f"⚙️ Game Settings\n\n✅ Timeout set to {timeout}s",
        reply_markup=get_settings_keyboard(rounds, timeout),
    )
    await callback.answer(f"Timeout set to {timeout}s")
