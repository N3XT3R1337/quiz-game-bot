from aiogram.fsm.state import State, StatesGroup


class GameStates(StatesGroup):
    idle = State()
    waiting_for_players = State()
    selecting_category = State()
    selecting_difficulty = State()
    playing = State()
    answering = State()
    between_questions = State()
    showing_results = State()
    game_over = State()


class SettingsStates(StatesGroup):
    main_menu = State()
    changing_rounds = State()
    changing_timeout = State()


class LeaderboardStates(StatesGroup):
    viewing = State()
    selecting_category = State()
    selecting_period = State()
