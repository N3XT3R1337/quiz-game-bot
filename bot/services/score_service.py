from datetime import datetime

from sqlalchemy import select, func, desc, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import async_session
from bot.models import User, GameSession, GameAnswer


class ScoreService:
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str,
    ) -> User:
        async with async_session() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
            else:
                if user.username != username or user.first_name != first_name:
                    user.username = username
                    user.first_name = first_name
                    await session.commit()

            return user

    async def save_game_results(
        self,
        results: dict,
        chat_id: int,
    ):
        async with async_session() as session:
            for ranking in results["rankings"]:
                stmt = select(User).where(User.telegram_id == ranking["user_id"])
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    continue

                user.total_games += 1
                user.total_score += ranking["score"]
                user.correct_answers += ranking["correct"]
                user.wrong_answers += ranking["wrong"]

                total_answers = user.correct_answers + user.wrong_answers
                if total_answers > 0:
                    user.average_time = (
                        (user.average_time * (total_answers - ranking["correct"] - ranking["wrong"])
                         + ranking["avg_time"] * (ranking["correct"] + ranking["wrong"]))
                        / total_answers
                    )

                is_winner = ranking["position"] == 1
                if is_winner:
                    user.total_wins += 1

                game_session = GameSession(
                    chat_id=chat_id,
                    user_id=user.id,
                    category=results["category"],
                    difficulty=results["difficulty"],
                    score=ranking["score"],
                    is_winner=is_winner,
                    questions_answered=ranking["correct"] + ranking["wrong"],
                    finished_at=datetime.utcnow(),
                )
                session.add(game_session)

            await session.commit()

    async def save_answer(
        self,
        telegram_id: int,
        chat_id: int,
        question_text: str,
        selected_answer: str,
        correct_answer: str,
        is_correct: bool,
        response_time: float,
        points_earned: int,
    ):
        async with async_session() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return

            answer = GameAnswer(
                user_id=user.id,
                chat_id=chat_id,
                question_text=question_text,
                selected_answer=selected_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
                response_time=response_time,
                points_earned=points_earned,
            )
            session.add(answer)
            await session.commit()

    async def get_user_stats(self, telegram_id: int) -> dict | None:
        async with async_session() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return None

            total_answers = user.correct_answers + user.wrong_answers
            accuracy = round(user.correct_answers / max(total_answers, 1) * 100, 1)
            win_rate = round(user.total_wins / max(user.total_games, 1) * 100, 1)

            recent_stmt = (
                select(GameSession)
                .where(GameSession.user_id == user.id)
                .order_by(desc(GameSession.started_at))
                .limit(5)
            )
            recent_result = await session.execute(recent_stmt)
            recent_games = recent_result.scalars().all()

            return {
                "username": user.username or user.first_name,
                "total_games": user.total_games,
                "total_wins": user.total_wins,
                "win_rate": win_rate,
                "total_score": user.total_score,
                "correct_answers": user.correct_answers,
                "wrong_answers": user.wrong_answers,
                "accuracy": accuracy,
                "average_time": round(user.average_time, 2),
                "recent_games": [
                    {
                        "category": g.category,
                        "difficulty": g.difficulty,
                        "score": g.score,
                        "is_winner": g.is_winner,
                        "date": g.started_at.strftime("%Y-%m-%d"),
                    }
                    for g in recent_games
                ],
            }

    async def get_global_leaderboard(self, limit: int = 10) -> list[dict]:
        async with async_session() as session:
            stmt = (
                select(User)
                .where(User.total_games > 0)
                .order_by(desc(User.total_score))
                .limit(limit)
            )
            result = await session.execute(stmt)
            users = result.scalars().all()

            return [
                {
                    "position": i + 1,
                    "username": u.username or u.first_name,
                    "total_score": u.total_score,
                    "games": u.total_games,
                    "wins": u.total_wins,
                    "accuracy": round(
                        u.correct_answers / max(u.correct_answers + u.wrong_answers, 1) * 100, 1
                    ),
                }
                for i, u in enumerate(users)
            ]

    async def get_category_leaderboard(
        self, category: str, limit: int = 10
    ) -> list[dict]:
        async with async_session() as session:
            stmt = (
                select(
                    User.telegram_id,
                    User.username,
                    User.first_name,
                    func.sum(GameSession.score).label("total_score"),
                    func.count(GameSession.id).label("games_played"),
                    func.sum(
                        func.cast(GameSession.is_winner, Integer)
                    ).label("wins"),
                )
                .join(GameSession, User.id == GameSession.user_id)
                .where(GameSession.category == category)
                .group_by(User.id)
                .order_by(desc("total_score"))
                .limit(limit)
            )

            result = await session.execute(stmt)
            rows = result.all()

            return [
                {
                    "position": i + 1,
                    "username": row.username or row.first_name,
                    "total_score": row.total_score or 0,
                    "games": row.games_played or 0,
                    "wins": row.wins or 0,
                }
                for i, row in enumerate(rows)
            ]

    def format_stats(self, stats: dict) -> str:
        lines = [
            f"📊 Stats for {stats['username']}\n",
            "━━━━━━━━━━━━━━━━━━━━━",
            f"🎮 Games Played: {stats['total_games']}",
            f"🏆 Wins: {stats['total_wins']} ({stats['win_rate']}%)",
            f"⭐ Total Score: {stats['total_score']}",
            f"✅ Correct: {stats['correct_answers']}",
            f"❌ Wrong: {stats['wrong_answers']}",
            f"🎯 Accuracy: {stats['accuracy']}%",
            f"⏱ Avg Response: {stats['average_time']}s",
        ]

        if stats["recent_games"]:
            lines.append("\n📋 Recent Games:")
            for g in stats["recent_games"]:
                result_emoji = "🏆" if g["is_winner"] else "📝"
                lines.append(
                    f"  {result_emoji} {g['category']} ({g['difficulty']}) - "
                    f"{g['score']} pts | {g['date']}"
                )

        return "\n".join(lines)

    def format_leaderboard(self, entries: list[dict], title: str) -> str:
        if not entries:
            return f"{title}\n\nNo data yet. Play some games!"

        medals = ["🥇", "🥈", "🥉"]
        lines = [f"{title}\n", "━━━━━━━━━━━━━━━━━━━━━"]

        for entry in entries:
            medal = medals[entry["position"] - 1] if entry["position"] <= 3 else f"{entry['position']}."
            lines.append(
                f"{medal} {entry['username']} — {entry['total_score']} pts "
                f"({entry['games']} games, {entry.get('wins', 0)} wins)"
            )

        return "\n".join(lines)


score_service = ScoreService()
