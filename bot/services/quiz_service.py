import random
import time
from dataclasses import dataclass, field

from bot.config import settings
from bot.questions import Question, get_filtered_questions, CATEGORIES


@dataclass
class PlayerState:
    user_id: int
    username: str
    score: int = 0
    correct: int = 0
    wrong: int = 0
    total_time: float = 0.0
    streak: int = 0
    max_streak: int = 0


@dataclass
class GameState:
    chat_id: int
    category: str
    difficulty: str
    questions: list[Question] = field(default_factory=list)
    current_index: int = 0
    players: dict[int, PlayerState] = field(default_factory=dict)
    is_active: bool = False
    round_count: int = 10
    timeout: int = 30
    question_start_time: float = 0.0
    answered_current: set[int] = field(default_factory=set)

    @property
    def current_question(self) -> Question | None:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    @property
    def is_last_question(self) -> bool:
        return self.current_index >= len(self.questions) - 1

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def progress_text(self) -> str:
        return f"Question {self.current_index + 1}/{self.total_questions}"

    @property
    def category_display(self) -> str:
        if self.category == "mixed":
            return "🎲 Mixed"
        return CATEGORIES.get(self.category, self.category)


class QuizService:
    def __init__(self):
        self.active_games: dict[int, GameState] = {}

    def create_game(
        self,
        chat_id: int,
        category: str,
        difficulty: str,
        round_count: int = 10,
        timeout: int = 30,
    ) -> GameState:
        questions = get_filtered_questions(category, difficulty)
        if not questions:
            questions = get_filtered_questions(None, None)

        random.shuffle(questions)
        selected = questions[:round_count]

        game = GameState(
            chat_id=chat_id,
            category=category,
            difficulty=difficulty,
            questions=selected,
            round_count=min(round_count, len(selected)),
            timeout=timeout,
            is_active=True,
        )
        self.active_games[chat_id] = game
        return game

    def get_game(self, chat_id: int) -> GameState | None:
        return self.active_games.get(chat_id)

    def add_player(self, chat_id: int, user_id: int, username: str) -> bool:
        game = self.active_games.get(chat_id)
        if not game:
            return False
        if user_id in game.players:
            return False
        if len(game.players) >= settings.max_players:
            return False
        game.players[user_id] = PlayerState(user_id=user_id, username=username)
        return True

    def remove_player(self, chat_id: int, user_id: int) -> bool:
        game = self.active_games.get(chat_id)
        if not game or user_id not in game.players:
            return False
        del game.players[user_id]
        return True

    def start_question(self, chat_id: int) -> Question | None:
        game = self.active_games.get(chat_id)
        if not game or not game.is_active:
            return None
        game.question_start_time = time.time()
        game.answered_current = set()
        return game.current_question

    def process_answer(
        self,
        chat_id: int,
        user_id: int,
        answer_index: int,
    ) -> dict | None:
        game = self.active_games.get(chat_id)
        if not game or not game.is_active:
            return None

        if user_id in game.answered_current:
            return None

        question = game.current_question
        if not question:
            return None

        game.answered_current.add(user_id)
        response_time = time.time() - game.question_start_time
        is_correct = answer_index == question.correct_index
        points = 0

        player = game.players.get(user_id)
        if not player:
            return None

        if is_correct:
            difficulty_points = {
                "easy": settings.points_easy,
                "medium": settings.points_medium,
                "hard": settings.points_hard,
            }
            points = difficulty_points.get(question.difficulty, settings.points_medium)

            if response_time <= settings.bonus_time_threshold:
                points += settings.bonus_points

            speed_bonus = max(0, int((game.timeout - response_time) / game.timeout * 5))
            points += speed_bonus

            player.score += points
            player.correct += 1
            player.streak += 1
            if player.streak > player.max_streak:
                player.max_streak = player.streak

            if player.streak >= 3:
                streak_bonus = player.streak * 2
                points += streak_bonus
                player.score += streak_bonus
        else:
            player.wrong += 1
            player.streak = 0

        player.total_time += response_time

        all_answered = len(game.answered_current) >= len(game.players)

        return {
            "is_correct": is_correct,
            "points": points,
            "response_time": round(response_time, 2),
            "correct_answer": question.correct_answer,
            "streak": player.streak,
            "all_answered": all_answered,
            "player_score": player.score,
        }

    def next_question(self, chat_id: int) -> bool:
        game = self.active_games.get(chat_id)
        if not game:
            return False
        game.current_index += 1
        return game.current_index < len(game.questions)

    def end_game(self, chat_id: int) -> dict | None:
        game = self.active_games.get(chat_id)
        if not game:
            return None

        game.is_active = False
        rankings = sorted(
            game.players.values(),
            key=lambda p: (p.score, p.correct, -p.total_time),
            reverse=True,
        )

        results = {
            "rankings": [
                {
                    "position": i + 1,
                    "user_id": p.user_id,
                    "username": p.username,
                    "score": p.score,
                    "correct": p.correct,
                    "wrong": p.wrong,
                    "accuracy": round(p.correct / max(p.correct + p.wrong, 1) * 100, 1),
                    "avg_time": round(p.total_time / max(p.correct + p.wrong, 1), 2),
                    "max_streak": p.max_streak,
                }
                for i, p in enumerate(rankings)
            ],
            "category": game.category,
            "difficulty": game.difficulty,
            "total_questions": game.total_questions,
        }

        if rankings:
            results["winner"] = {
                "user_id": rankings[0].user_id,
                "username": rankings[0].username,
                "score": rankings[0].score,
            }

        del self.active_games[chat_id]
        return results

    def cancel_game(self, chat_id: int) -> bool:
        if chat_id in self.active_games:
            del self.active_games[chat_id]
            return True
        return False

    def get_question_status(self, chat_id: int) -> str:
        game = self.active_games.get(chat_id)
        if not game:
            return ""
        answered = len(game.answered_current)
        total = len(game.players)
        return f"📝 {answered}/{total} players answered"

    def format_scoreboard(self, chat_id: int) -> str:
        game = self.active_games.get(chat_id)
        if not game:
            return "No active game."

        sorted_players = sorted(
            game.players.values(),
            key=lambda p: p.score,
            reverse=True,
        )

        medals = ["🥇", "🥈", "🥉"]
        lines = ["📊 Current Standings:\n"]

        for i, player in enumerate(sorted_players):
            medal = medals[i] if i < len(medals) else f"{i + 1}."
            streak_text = f" 🔥{player.streak}" if player.streak >= 2 else ""
            lines.append(
                f"{medal} {player.username}: {player.score} pts "
                f"({player.correct}✅ {player.wrong}❌){streak_text}"
            )

        return "\n".join(lines)

    def format_results(self, results: dict) -> str:
        lines = [
            "🏁 Game Over!\n",
            f"Category: {results['category']} | "
            f"Difficulty: {results['difficulty']}",
            f"Questions: {results['total_questions']}\n",
            "━━━ Final Rankings ━━━\n",
        ]

        medals = ["🥇", "🥈", "🥉"]
        for r in results["rankings"]:
            medal = medals[r["position"] - 1] if r["position"] <= 3 else f"{r['position']}."
            lines.append(
                f"{medal} {r['username']}\n"
                f"   Score: {r['score']} | "
                f"Accuracy: {r['accuracy']}% | "
                f"Avg Time: {r['avg_time']}s | "
                f"Best Streak: {r['max_streak']}"
            )

        if results.get("winner"):
            w = results["winner"]
            lines.append(f"\n🎉 Winner: {w['username']} with {w['score']} points!")

        return "\n".join(lines)


quiz_service = QuizService()
