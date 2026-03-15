import json
from typing import Any

import redis.asyncio as aioredis

from bot.config import settings


class RedisClient:
    def __init__(self):
        self._redis: aioredis.Redis | None = None

    async def connect(self):
        self._redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self):
        if self._redis:
            await self._redis.close()

    async def set_game_state(self, chat_id: int, state: dict[str, Any]):
        key = f"game:{chat_id}"
        await self._redis.set(key, json.dumps(state), ex=3600)

    async def get_game_state(self, chat_id: int) -> dict[str, Any] | None:
        key = f"game:{chat_id}"
        data = await self._redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def delete_game_state(self, chat_id: int):
        key = f"game:{chat_id}"
        await self._redis.delete(key)

    async def update_score(self, chat_id: int, user_id: int, points: int):
        key = f"scores:{chat_id}"
        await self._redis.hincrby(key, str(user_id), points)

    async def get_scores(self, chat_id: int) -> dict[str, int]:
        key = f"scores:{chat_id}"
        data = await self._redis.hgetall(key)
        return {k: int(v) for k, v in data.items()}

    async def reset_scores(self, chat_id: int):
        key = f"scores:{chat_id}"
        await self._redis.delete(key)

    async def set_question_timer(self, chat_id: int, question_id: int, timeout: int):
        key = f"timer:{chat_id}:{question_id}"
        await self._redis.set(key, "active", ex=timeout)

    async def is_question_active(self, chat_id: int, question_id: int) -> bool:
        key = f"timer:{chat_id}:{question_id}"
        return await self._redis.exists(key) > 0

    async def add_player(self, chat_id: int, user_id: int, username: str):
        key = f"players:{chat_id}"
        await self._redis.hset(key, str(user_id), username)
        await self._redis.expire(key, 3600)

    async def remove_player(self, chat_id: int, user_id: int):
        key = f"players:{chat_id}"
        await self._redis.hdel(key, str(user_id))

    async def get_players(self, chat_id: int) -> dict[str, str]:
        key = f"players:{chat_id}"
        return await self._redis.hgetall(key)

    async def clear_players(self, chat_id: int):
        key = f"players:{chat_id}"
        await self._redis.delete(key)

    async def record_answer(self, chat_id: int, question_index: int, user_id: int):
        key = f"answered:{chat_id}:{question_index}"
        await self._redis.sadd(key, str(user_id))
        await self._redis.expire(key, 3600)

    async def has_answered(self, chat_id: int, question_index: int, user_id: int) -> bool:
        key = f"answered:{chat_id}:{question_index}"
        return await self._redis.sismember(key, str(user_id))

    async def get_answer_count(self, chat_id: int, question_index: int) -> int:
        key = f"answered:{chat_id}:{question_index}"
        return await self._redis.scard(key)

    async def clear_answers(self, chat_id: int, question_index: int):
        key = f"answered:{chat_id}:{question_index}"
        await self._redis.delete(key)

    async def set_leaderboard(self, category: str, user_id: int, score: int):
        key = f"leaderboard:{category}"
        await self._redis.zadd(key, {str(user_id): score})

    async def get_leaderboard(self, category: str, top_n: int = 10) -> list[tuple[str, float]]:
        key = f"leaderboard:{category}"
        return await self._redis.zrevrange(key, 0, top_n - 1, withscores=True)

    async def get_global_leaderboard(self, top_n: int = 10) -> list[tuple[str, float]]:
        return await self.get_leaderboard("global", top_n)


redis_client = RedisClient()
