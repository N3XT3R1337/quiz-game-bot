from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str = ""
    database_url: str = "sqlite+aiosqlite:///quiz_bot.db"
    redis_url: str = "redis://localhost:6379/0"
    question_timeout: int = 30
    max_players: int = 10
    min_players: int = 1
    points_easy: int = 10
    points_medium: int = 20
    points_hard: int = 30
    bonus_time_threshold: int = 10
    bonus_points: int = 5

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
