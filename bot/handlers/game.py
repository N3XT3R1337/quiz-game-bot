import asyncio

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.game_kb import (
    get_category_keyboard,
    get_difficulty_keyboard,
    get_answer_keyboard,
    get_join_game_keyboard,
    get_next_question_keyboard,
    get_play_again_keyboard,
    get_main_menu_keyboard,
)
from bot.services.quiz_service import quiz_service
from bot.services.score_service import score_service
from bot.states import GameStates

router = Router()


@router.callback_query(F.data == "new_game")
async def new_game(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GameStates.selecting_category)
    await callback.message.edit_text(
        "📚 Select a quiz category:",
        reply_markup=get_category_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"), GameStates.selecting_category)
async def select_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":")[1]
    await state.update_data(category=category)
    await state.set_state(GameStates.selecting_difficulty)
    await callback.message.edit_text(
        "🎯 Select difficulty level:",
        reply_markup=get_difficulty_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_category")
async def back_to_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GameStates.selecting_category)
    await callback.message.edit_text(
        "📚 Select a quiz category:",
        reply_markup=get_category_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("diff:"), GameStates.selecting_difficulty)
async def select_difficulty(callback: CallbackQuery, state: FSMContext):
    difficulty = callback.data.split(":")[1]
    data = await state.get_data()
    category = data.get("category", "mixed")
    rounds = data.get("rounds", 10)
    timeout = data.get("timeout", 30)

    game = quiz_service.create_game(
        chat_id=callback.message.chat.id,
        category=category,
        difficulty=difficulty,
        round_count=rounds,
        timeout=timeout,
    )

    username = callback.from_user.username or callback.from_user.first_name
    quiz_service.add_player(callback.message.chat.id, callback.from_user.id, username)

    await state.set_state(GameStates.waiting_for_players)
    await state.update_data(difficulty=difficulty)

    await callback.message.edit_text(
        f"🎮 New Quiz Game!\n\n"
        f"Category: {game.category_display}\n"
        f"Difficulty: {difficulty}\n"
        f"Questions: {game.total_questions}\n"
        f"Timeout: {timeout}s\n\n"
        f"👥 Players (1/{10}):\n"
        f"  • {username}\n\n"
        f"Waiting for players to join...",
        reply_markup=get_join_game_keyboard(callback.message.chat.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("join:"))
async def join_game(callback: CallbackQuery, state: FSMContext):
    chat_id = int(callback.data.split(":")[1])
    username = callback.from_user.username or callback.from_user.first_name
    game = quiz_service.get_game(chat_id)

    if not game:
        await callback.answer("No active game found!", show_alert=True)
        return

    if callback.from_user.id in game.players:
        await callback.answer("You already joined!", show_alert=True)
        return

    added = quiz_service.add_player(chat_id, callback.from_user.id, username)
    if not added:
        await callback.answer("Game is full!", show_alert=True)
        return

    await score_service.get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
    )

    player_list = "\n".join(f"  • {p.username}" for p in game.players.values())
    await callback.message.edit_text(
        f"🎮 New Quiz Game!\n\n"
        f"Category: {game.category_display}\n"
        f"Difficulty: {game.difficulty}\n"
        f"Questions: {game.total_questions}\n\n"
        f"👥 Players ({len(game.players)}/{10}):\n"
        f"{player_list}\n\n"
        f"Waiting for players to join...",
        reply_markup=get_join_game_keyboard(chat_id),
    )
    await callback.answer(f"Welcome, {username}!")


@router.callback_query(F.data.startswith("start_now:"))
async def start_game_now(callback: CallbackQuery, state: FSMContext, bot: Bot):
    chat_id = int(callback.data.split(":")[1])
    game = quiz_service.get_game(chat_id)

    if not game:
        await callback.answer("No active game found!", show_alert=True)
        return

    if callback.from_user.id not in game.players:
        await callback.answer("Only players can start the game!", show_alert=True)
        return

    await state.set_state(GameStates.playing)
    await callback.message.edit_text("🚀 Game starting in 3 seconds...")
    await callback.answer()

    await asyncio.sleep(1)
    await send_question(callback.message.chat.id, bot, state)


@router.callback_query(F.data == "cancel_game")
async def cancel_game(callback: CallbackQuery, state: FSMContext):
    quiz_service.cancel_game(callback.message.chat.id)
    await state.clear()
    await callback.message.edit_text(
        "❌ Game cancelled.\n\nUse the menu to start a new game:",
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer("Game cancelled")


async def send_question(chat_id: int, bot: Bot, state: FSMContext):
    game = quiz_service.get_game(chat_id)
    if not game:
        return

    question = quiz_service.start_question(chat_id)
    if not question:
        await finish_game(chat_id, bot, state)
        return

    difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(
        question.difficulty, "⚪"
    )

    question_text = (
        f"📝 {game.progress_text}\n\n"
        f"{difficulty_emoji} {question.difficulty.upper()} | "
        f"⏱ {game.timeout}s\n\n"
        f"❓ {question.text}"
    )

    await bot.send_message(
        chat_id=chat_id,
        text=question_text,
        reply_markup=get_answer_keyboard(question, game.current_index),
    )

    asyncio.create_task(question_timeout(chat_id, game.current_index, game.timeout, bot, state))


async def question_timeout(
    chat_id: int,
    question_index: int,
    timeout: int,
    bot: Bot,
    state: FSMContext,
):
    await asyncio.sleep(timeout)
    game = quiz_service.get_game(chat_id)

    if not game or not game.is_active:
        return

    if game.current_index != question_index:
        return

    question = game.current_question
    if not question:
        return

    unanswered = [
        p.username for uid, p in game.players.items()
        if uid not in game.answered_current
    ]

    timeout_text = (
        f"⏱ Time's up!\n\n"
        f"✅ Correct answer: {question.correct_answer}\n"
    )

    if unanswered:
        timeout_text += f"\n⚠️ Didn't answer: {', '.join(unanswered)}"

    scoreboard = quiz_service.format_scoreboard(chat_id)
    timeout_text += f"\n\n{scoreboard}"

    if game.is_last_question:
        await bot.send_message(chat_id=chat_id, text=timeout_text)
        await finish_game(chat_id, bot, state)
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=timeout_text,
            reply_markup=get_next_question_keyboard(),
        )


@router.callback_query(F.data.startswith("ans:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    parts = callback.data.split(":")
    question_index = int(parts[1])
    answer_index = int(parts[2])

    game = quiz_service.get_game(callback.message.chat.id)
    if not game or not game.is_active:
        await callback.answer("No active game!", show_alert=True)
        return

    if game.current_index != question_index:
        await callback.answer("This question has expired!", show_alert=True)
        return

    result = quiz_service.process_answer(
        chat_id=callback.message.chat.id,
        user_id=callback.from_user.id,
        answer_index=answer_index,
    )

    if result is None:
        await callback.answer("You already answered!", show_alert=True)
        return

    question = game.questions[question_index]

    await score_service.save_answer(
        telegram_id=callback.from_user.id,
        chat_id=callback.message.chat.id,
        question_text=question.text,
        selected_answer=question.options[answer_index],
        correct_answer=question.correct_answer,
        is_correct=result["is_correct"],
        response_time=result["response_time"],
        points_earned=result["points"],
    )

    username = callback.from_user.username or callback.from_user.first_name

    if result["is_correct"]:
        streak_text = ""
        if result["streak"] >= 3:
            streak_text = f" 🔥 Streak: {result['streak']}!"
        answer_text = (
            f"✅ {username} answered correctly!\n"
            f"+{result['points']} points (⏱ {result['response_time']}s)"
            f"{streak_text}"
        )
    else:
        answer_text = (
            f"❌ {username} answered wrong!\n"
            f"Correct answer: {result['correct_answer']}"
        )

    await callback.answer(
        "✅ Correct!" if result["is_correct"] else f"❌ Wrong! Answer: {result['correct_answer']}",
        show_alert=False,
    )

    if result["all_answered"]:
        scoreboard = quiz_service.format_scoreboard(callback.message.chat.id)
        summary = f"{answer_text}\n\n{scoreboard}"

        if game.is_last_question:
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text=summary,
            )
            await finish_game(callback.message.chat.id, bot, state)
        else:
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text=summary,
                reply_markup=get_next_question_keyboard(),
            )
    else:
        status = quiz_service.get_question_status(callback.message.chat.id)
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"{answer_text}\n\n{status}",
        )


@router.callback_query(F.data == "next_question")
async def next_question(callback: CallbackQuery, state: FSMContext, bot: Bot):
    game = quiz_service.get_game(callback.message.chat.id)
    if not game:
        await callback.answer("No active game!", show_alert=True)
        return

    has_next = quiz_service.next_question(callback.message.chat.id)
    if not has_next:
        await finish_game(callback.message.chat.id, bot, state)
        await callback.answer()
        return

    await callback.answer()
    await send_question(callback.message.chat.id, bot, state)


async def finish_game(chat_id: int, bot: Bot, state: FSMContext):
    results = quiz_service.end_game(chat_id)
    if not results:
        return

    await score_service.save_game_results(results, chat_id)

    results_text = quiz_service.format_results(results)
    await bot.send_message(
        chat_id=chat_id,
        text=results_text,
        reply_markup=get_play_again_keyboard(),
    )

    await state.clear()
