```
 ██████╗ ██╗   ██╗██╗███████╗     ██████╗  █████╗ ███╗   ███╗███████╗
██╔═══██╗██║   ██║██║╚══███╔╝    ██╔════╝ ██╔══██╗████╗ ████║██╔════╝
██║   ██║██║   ██║██║  ███╔╝     ██║  ███╗███████║██╔████╔██║█████╗
██║▄▄ ██║██║   ██║██║ ███╔╝      ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝
╚██████╔╝╚██████╔╝██║███████╗    ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗
 ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝     ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
                    ██████╗  ██████╗ ████████╗
                    ██╔══██╗██╔═══██╗╚══██╔══╝
                    ██████╔╝██║   ██║   ██║
                    ██╔══██╗██║   ██║   ██║
                    ██████╔╝╚██████╔╝   ██║
                    ╚═════╝  ╚═════╝    ╚═╝
```

<p align="center">
  <strong>Multiplayer quiz game Telegram bot with leaderboards, timed questions, and competitive gameplay</strong>
</p>

<p align="center">
  <a href="https://github.com/N3XT3R1337/quiz-game-bot/actions"><img src="https://img.shields.io/github/actions/workflow/status/N3XT3R1337/quiz-game-bot/ci.yml?style=flat-square&logo=github&label=build" alt="Build Status"></a>
  <a href="https://github.com/N3XT3R1337/quiz-game-bot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/N3XT3R1337/quiz-game-bot?style=flat-square&color=blue" alt="License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11+-blue?style=flat-square&logo=python&logoColor=white" alt="Python Version"></a>
  <a href="https://docs.aiogram.dev/en/latest/"><img src="https://img.shields.io/badge/aiogram-3.x-green?style=flat-square" alt="aiogram"></a>
  <a href="https://redis.io/"><img src="https://img.shields.io/badge/redis-7.0+-red?style=flat-square&logo=redis&logoColor=white" alt="Redis"></a>
</p>

---

## Features

- **Multiplayer Gameplay** — Up to 10 players per game session with real-time scoring
- **8 Quiz Categories** — Science, History, Geography, Technology, Entertainment, Sports, Literature, Mathematics
- **3 Difficulty Levels** — Easy, Medium, Hard with scaled point rewards
- **Timed Questions** — Configurable countdown timer with speed bonuses
- **Streak System** — Consecutive correct answers earn multiplied bonus points
- **Live Leaderboards** — Global, weekly, and per-category rankings
- **Player Statistics** — Track accuracy, win rate, average response time, game history
- **FSM Game Flow** — Clean state machine managing lobby → category → difficulty → play → results
- **Persistent Storage** — SQLAlchemy async ORM for player data, Redis for real-time game state
- **Configurable Settings** — Adjust round count, timeout, and scoring per session

## Tech Stack

| Component       | Technology                     |
|----------------|--------------------------------|
| Bot Framework  | aiogram 3.x (async)            |
| Database       | SQLAlchemy 2.0 + aiosqlite     |
| Cache/Scores   | Redis 7.0+                     |
| State Machine  | aiogram FSM                    |
| Configuration  | pydantic-settings              |
| Testing        | pytest + pytest-asyncio        |
| Language       | Python 3.11+                   |

## Project Structure

```
quiz-game-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Entry point, dispatcher setup
│   ├── config.py             # Settings via pydantic-settings
│   ├── models.py             # SQLAlchemy ORM models
│   ├── database.py           # Async engine & session factory
│   ├── redis_client.py       # Redis wrapper for game state
│   ├── states.py             # FSM state definitions
│   ├── questions.py          # Question bank & filtering
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py          # /start, /help, /stats, settings
│   │   ├── game.py           # Game flow, answering, scoring
│   │   └── leaderboard.py    # Leaderboard views
│   ├── keyboards/
│   │   ├── __init__.py
│   │   └── game_kb.py        # Inline keyboards
│   └── services/
│       ├── __init__.py
│       ├── quiz_service.py   # Game logic & state management
│       └── score_service.py  # DB operations & formatting
├── tests/
│   ├── __init__.py
│   └── test_quiz.py          # Unit tests
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Installation

### Prerequisites

- Python 3.11 or higher
- Redis server running locally or remotely
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Setup

```bash
git clone https://github.com/N3XT3R1337/quiz-game-bot.git
cd quiz-game-bot
```

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

```bash
pip install -r requirements.txt
```

```bash
cp .env.example .env
```

Edit `.env` and set your bot token:

```env
BOT_TOKEN=123456789:ABCDefGhIJKlMnOpQrStUvWxYz
DATABASE_URL=sqlite+aiosqlite:///quiz_bot.db
REDIS_URL=redis://localhost:6379/0
```

### Running

```bash
python -m bot.main
```

## Usage

### Starting a Game

Send `/start` to the bot to open the main menu. Tap **New Game** to begin:

```
User: /start
Bot:  🎮 Welcome to Quiz Game Bot!
      [New Game] [Leaderboard]
      [My Stats] [Settings]
```

### Game Flow

1. **Select Category** — Choose from 8 categories or Mixed
2. **Select Difficulty** — Easy, Medium, Hard, or Mixed
3. **Lobby** — Share the join button; other players tap to join
4. **Play** — Answer timed multiple-choice questions
5. **Results** — View final rankings, accuracy, and streaks

```
Bot:  📝 Question 3/10
      🟡 MEDIUM | ⏱ 30s
      ❓ What is the speed of light approximately?
      [A. 300,000 km/s]
      [B. 150,000 km/s]
      [C. 500,000 km/s]
      [D. 100,000 km/s]
```

### Viewing Stats

```
User: /stats
Bot:  📊 Stats for alice
      ━━━━━━━━━━━━━━━━━━━━━
      🎮 Games Played: 15
      🏆 Wins: 8 (53.3%)
      ⭐ Total Score: 1250
      ✅ Correct: 98
      ❌ Wrong: 32
      🎯 Accuracy: 75.4%
      ⏱ Avg Response: 8.42s
```

### Leaderboards

```
User: /leaderboard
Bot:  🌍 Global Leaderboard
      ━━━━━━━━━━━━━━━━━━━━━
      🥇 alice — 1250 pts (15 games, 8 wins)
      🥈 bob — 980 pts (12 games, 5 wins)
      🥉 charlie — 720 pts (9 games, 3 wins)
```

### Scoring System

| Difficulty | Base Points |
|-----------|-------------|
| Easy      | 10 pts      |
| Medium    | 20 pts      |
| Hard      | 30 pts      |

**Bonuses:**
- ⚡ Speed bonus: Answer within 10s for +5 pts
- 🔥 Streak bonus: 3+ correct in a row = streak × 2 extra pts
- ⏱ Time bonus: Up to 5 pts scaled by remaining time

## Testing

```bash
pytest tests/ -v
```

```bash
pytest tests/ -v --tb=short
```

## Configuration

All settings can be configured via environment variables or `.env` file:

| Variable              | Default                          | Description                  |
|----------------------|----------------------------------|------------------------------|
| `BOT_TOKEN`          | —                                | Telegram bot API token       |
| `DATABASE_URL`       | `sqlite+aiosqlite:///quiz_bot.db`| SQLAlchemy connection string |
| `REDIS_URL`          | `redis://localhost:6379/0`       | Redis connection URL         |
| `QUESTION_TIMEOUT`   | `30`                             | Seconds per question         |
| `MAX_PLAYERS`        | `10`                             | Max players per game         |
| `POINTS_EASY`        | `10`                             | Points for easy questions    |
| `POINTS_MEDIUM`      | `20`                             | Points for medium questions  |
| `POINTS_HARD`        | `30`                             | Points for hard questions    |
| `BONUS_POINTS`       | `5`                              | Speed bonus points           |

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 panaceya (N3XT3R1337)
