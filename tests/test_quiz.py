import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock

from bot.questions import (
    Question,
    get_filtered_questions,
    get_questions_by_category,
    get_questions_by_difficulty,
    get_questions,
    CATEGORIES,
    DIFFICULTIES,
    QUESTIONS_DB,
)
from bot.services.quiz_service import QuizService, GameState, PlayerState
from bot.config import Settings


class TestQuestions:
    def test_question_correct_answer(self):
        q = Question(
            text="Test?",
            options=["A", "B", "C", "D"],
            correct_index=2,
            category="science",
            difficulty="easy",
        )
        assert q.correct_answer == "C"

    def test_get_filtered_questions_by_category(self):
        results = get_filtered_questions(category="science")
        assert len(results) > 0
        assert all(q.category == "science" for q in results)

    def test_get_filtered_questions_by_difficulty(self):
        results = get_filtered_questions(difficulty="easy")
        assert len(results) > 0
        assert all(q.difficulty == "easy" for q in results)

    def test_get_filtered_questions_mixed(self):
        results = get_filtered_questions(category="mixed", difficulty="mixed")
        assert len(results) == len(QUESTIONS_DB)

    def test_get_filtered_questions_both_filters(self):
        results = get_filtered_questions(category="science", difficulty="easy")
        assert len(results) > 0
        assert all(q.category == "science" and q.difficulty == "easy" for q in results)

    def test_all_categories_have_questions(self):
        for cat in CATEGORIES:
            results = get_questions_by_category(cat)
            assert len(results) > 0, f"No questions for category: {cat}"

    def test_all_difficulties_have_questions(self):
        for diff in DIFFICULTIES:
            results = get_questions_by_difficulty(diff)
            assert len(results) > 0, f"No questions for difficulty: {diff}"

    def test_question_options_count(self):
        for q in QUESTIONS_DB:
            assert len(q.options) == 4, f"Question has {len(q.options)} options: {q.text}"

    def test_correct_index_in_range(self):
        for q in QUESTIONS_DB:
            assert 0 <= q.correct_index < len(q.options), f"Invalid correct_index: {q.text}"


class TestQuizService:
    def setup_method(self):
        self.service = QuizService()

    def test_create_game(self):
        game = self.service.create_game(
            chat_id=123,
            category="science",
            difficulty="easy",
            round_count=5,
        )
        assert game.chat_id == 123
        assert game.category == "science"
        assert game.is_active is True
        assert len(game.questions) <= 5

    def test_create_game_mixed_category(self):
        game = self.service.create_game(
            chat_id=456,
            category="mixed",
            difficulty="mixed",
            round_count=10,
        )
        assert game.is_active is True
        assert len(game.questions) > 0

    def test_add_player(self):
        self.service.create_game(chat_id=123, category="science", difficulty="easy")
        result = self.service.add_player(123, 1001, "player1")
        assert result is True
        game = self.service.get_game(123)
        assert 1001 in game.players

    def test_add_duplicate_player(self):
        self.service.create_game(chat_id=123, category="science", difficulty="easy")
        self.service.add_player(123, 1001, "player1")
        result = self.service.add_player(123, 1001, "player1")
        assert result is False

    def test_remove_player(self):
        self.service.create_game(chat_id=123, category="science", difficulty="easy")
        self.service.add_player(123, 1001, "player1")
        result = self.service.remove_player(123, 1001)
        assert result is True
        game = self.service.get_game(123)
        assert 1001 not in game.players

    def test_process_correct_answer(self):
        game = self.service.create_game(
            chat_id=123, category="science", difficulty="easy", round_count=5
        )
        self.service.add_player(123, 1001, "player1")
        self.service.start_question(123)
        correct_idx = game.current_question.correct_index
        result = self.service.process_answer(123, 1001, correct_idx)
        assert result is not None
        assert result["is_correct"] is True
        assert result["points"] > 0

    def test_process_wrong_answer(self):
        game = self.service.create_game(
            chat_id=123, category="science", difficulty="easy", round_count=5
        )
        self.service.add_player(123, 1001, "player1")
        self.service.start_question(123)
        correct_idx = game.current_question.correct_index
        wrong_idx = (correct_idx + 1) % 4
        result = self.service.process_answer(123, 1001, wrong_idx)
        assert result is not None
        assert result["is_correct"] is False
        assert result["points"] == 0

    def test_double_answer_rejected(self):
        game = self.service.create_game(
            chat_id=123, category="science", difficulty="easy", round_count=5
        )
        self.service.add_player(123, 1001, "player1")
        self.service.start_question(123)
        self.service.process_answer(123, 1001, 0)
        result = self.service.process_answer(123, 1001, 1)
        assert result is None

    def test_next_question(self):
        self.service.create_game(
            chat_id=123, category="mixed", difficulty="mixed", round_count=5
        )
        self.service.add_player(123, 1001, "player1")
        self.service.start_question(123)
        has_next = self.service.next_question(123)
        assert has_next is True
        game = self.service.get_game(123)
        assert game.current_index == 1

    def test_end_game(self):
        self.service.create_game(
            chat_id=123, category="science", difficulty="easy", round_count=2
        )
        self.service.add_player(123, 1001, "player1")
        self.service.add_player(123, 1002, "player2")
        self.service.start_question(123)
        game = self.service.get_game(123)
        self.service.process_answer(123, 1001, game.current_question.correct_index)
        results = self.service.end_game(123)
        assert results is not None
        assert "rankings" in results
        assert "winner" in results
        assert len(results["rankings"]) == 2

    def test_cancel_game(self):
        self.service.create_game(chat_id=123, category="science", difficulty="easy")
        result = self.service.cancel_game(123)
        assert result is True
        assert self.service.get_game(123) is None

    def test_cancel_nonexistent_game(self):
        result = self.service.cancel_game(999)
        assert result is False

    def test_format_scoreboard(self):
        self.service.create_game(
            chat_id=123, category="science", difficulty="easy", round_count=5
        )
        self.service.add_player(123, 1001, "Alice")
        self.service.add_player(123, 1002, "Bob")
        text = self.service.format_scoreboard(123)
        assert "Alice" in text
        assert "Bob" in text
        assert "Standings" in text

    def test_streak_tracking(self):
        game = self.service.create_game(
            chat_id=123, category="mixed", difficulty="mixed", round_count=5
        )
        self.service.add_player(123, 1001, "player1")

        for i in range(3):
            self.service.start_question(123)
            correct_idx = game.current_question.correct_index
            result = self.service.process_answer(123, 1001, correct_idx)
            if i < len(game.questions) - 1:
                self.service.next_question(123)

        player = game.players[1001]
        assert player.streak >= 1
        assert player.max_streak >= 1


class TestGameState:
    def test_current_question(self):
        q = Question("Test?", ["A", "B", "C", "D"], 0, "science", "easy")
        state = GameState(
            chat_id=1, category="science", difficulty="easy", questions=[q]
        )
        assert state.current_question == q

    def test_current_question_empty(self):
        state = GameState(
            chat_id=1, category="science", difficulty="easy", questions=[]
        )
        assert state.current_question is None

    def test_is_last_question(self):
        q = Question("Test?", ["A", "B", "C", "D"], 0, "science", "easy")
        state = GameState(
            chat_id=1, category="science", difficulty="easy", questions=[q]
        )
        assert state.is_last_question is True

    def test_progress_text(self):
        q1 = Question("Q1?", ["A", "B", "C", "D"], 0, "science", "easy")
        q2 = Question("Q2?", ["A", "B", "C", "D"], 1, "science", "easy")
        state = GameState(
            chat_id=1, category="science", difficulty="easy", questions=[q1, q2]
        )
        assert state.progress_text == "Question 1/2"

    def test_category_display_mixed(self):
        state = GameState(
            chat_id=1, category="mixed", difficulty="easy", questions=[]
        )
        assert state.category_display == "🎲 Mixed"

    def test_category_display_named(self):
        state = GameState(
            chat_id=1, category="science", difficulty="easy", questions=[]
        )
        assert "Science" in state.category_display


class TestPlayerState:
    def test_default_values(self):
        player = PlayerState(user_id=1, username="test")
        assert player.score == 0
        assert player.correct == 0
        assert player.wrong == 0
        assert player.streak == 0
        assert player.max_streak == 0

    def test_score_accumulation(self):
        player = PlayerState(user_id=1, username="test")
        player.score += 10
        player.score += 20
        assert player.score == 30


class TestSettings:
    def test_default_settings(self):
        s = Settings(bot_token="test:token")
        assert s.question_timeout == 30
        assert s.max_players == 10
        assert s.min_players == 1
        assert s.points_easy == 10
        assert s.points_medium == 20
        assert s.points_hard == 30
        assert s.bonus_points == 5
