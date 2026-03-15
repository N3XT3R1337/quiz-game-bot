from dataclasses import dataclass, field


@dataclass
class Question:
    text: str
    options: list[str]
    correct_index: int
    category: str
    difficulty: str

    @property
    def correct_answer(self) -> str:
        return self.options[self.correct_index]


CATEGORIES = {
    "science": "🔬 Science",
    "history": "📜 History",
    "geography": "🌍 Geography",
    "technology": "💻 Technology",
    "entertainment": "🎬 Entertainment",
    "sports": "⚽ Sports",
    "literature": "📚 Literature",
    "math": "🔢 Mathematics",
}

DIFFICULTIES = {
    "easy": "🟢 Easy",
    "medium": "🟡 Medium",
    "hard": "🔴 Hard",
}

QUESTIONS_DB: list[Question] = [
    Question(
        text="What is the chemical symbol for gold?",
        options=["Ag", "Au", "Fe", "Cu"],
        correct_index=1,
        category="science",
        difficulty="easy",
    ),
    Question(
        text="What planet is known as the Red Planet?",
        options=["Venus", "Jupiter", "Mars", "Saturn"],
        correct_index=2,
        category="science",
        difficulty="easy",
    ),
    Question(
        text="What is the speed of light approximately?",
        options=["300,000 km/s", "150,000 km/s", "500,000 km/s", "100,000 km/s"],
        correct_index=0,
        category="science",
        difficulty="medium",
    ),
    Question(
        text="What is the powerhouse of the cell?",
        options=["Nucleus", "Ribosome", "Mitochondria", "Golgi apparatus"],
        correct_index=2,
        category="science",
        difficulty="easy",
    ),
    Question(
        text="What is the atomic number of Carbon?",
        options=["4", "6", "8", "12"],
        correct_index=1,
        category="science",
        difficulty="medium",
    ),
    Question(
        text="What subatomic particle has no electric charge?",
        options=["Proton", "Electron", "Neutron", "Positron"],
        correct_index=2,
        category="science",
        difficulty="medium",
    ),
    Question(
        text="What is the Heisenberg Uncertainty Principle about?",
        options=[
            "Energy conservation",
            "Position and momentum measurement limits",
            "Speed of light constancy",
            "Quantum entanglement",
        ],
        correct_index=1,
        category="science",
        difficulty="hard",
    ),
    Question(
        text="Which year did World War II end?",
        options=["1943", "1944", "1945", "1946"],
        correct_index=2,
        category="history",
        difficulty="easy",
    ),
    Question(
        text="Who was the first President of the United States?",
        options=["John Adams", "Thomas Jefferson", "George Washington", "Benjamin Franklin"],
        correct_index=2,
        category="history",
        difficulty="easy",
    ),
    Question(
        text="In which year did the Berlin Wall fall?",
        options=["1987", "1988", "1989", "1990"],
        correct_index=2,
        category="history",
        difficulty="medium",
    ),
    Question(
        text="Which empire was ruled by Genghis Khan?",
        options=["Ottoman Empire", "Mongol Empire", "Roman Empire", "Persian Empire"],
        correct_index=1,
        category="history",
        difficulty="easy",
    ),
    Question(
        text="What treaty ended World War I?",
        options=["Treaty of Paris", "Treaty of Versailles", "Treaty of Vienna", "Treaty of Ghent"],
        correct_index=1,
        category="history",
        difficulty="medium",
    ),
    Question(
        text="Who was the last pharaoh of ancient Egypt?",
        options=["Nefertiti", "Hatshepsut", "Cleopatra VII", "Ramesses II"],
        correct_index=2,
        category="history",
        difficulty="hard",
    ),
    Question(
        text="What is the capital of Australia?",
        options=["Sydney", "Melbourne", "Canberra", "Brisbane"],
        correct_index=2,
        category="geography",
        difficulty="easy",
    ),
    Question(
        text="Which is the longest river in the world?",
        options=["Amazon", "Nile", "Mississippi", "Yangtze"],
        correct_index=1,
        category="geography",
        difficulty="easy",
    ),
    Question(
        text="What is the smallest country in the world?",
        options=["Monaco", "Vatican City", "San Marino", "Liechtenstein"],
        correct_index=1,
        category="geography",
        difficulty="medium",
    ),
    Question(
        text="Which desert is the largest in the world?",
        options=["Sahara", "Arabian", "Antarctic", "Gobi"],
        correct_index=2,
        category="geography",
        difficulty="hard",
    ),
    Question(
        text="Mount Kilimanjaro is located in which country?",
        options=["Kenya", "Tanzania", "Uganda", "Ethiopia"],
        correct_index=1,
        category="geography",
        difficulty="medium",
    ),
    Question(
        text="Who created the Python programming language?",
        options=["Linus Torvalds", "James Gosling", "Guido van Rossum", "Dennis Ritchie"],
        correct_index=2,
        category="technology",
        difficulty="easy",
    ),
    Question(
        text="What does CPU stand for?",
        options=[
            "Central Processing Unit",
            "Computer Personal Unit",
            "Central Program Utility",
            "Central Peripheral Unit",
        ],
        correct_index=0,
        category="technology",
        difficulty="easy",
    ),
    Question(
        text="What year was the first iPhone released?",
        options=["2005", "2006", "2007", "2008"],
        correct_index=2,
        category="technology",
        difficulty="medium",
    ),
    Question(
        text="What does SQL stand for?",
        options=[
            "Structured Query Language",
            "Simple Query Language",
            "Standard Query Logic",
            "Sequential Query Language",
        ],
        correct_index=0,
        category="technology",
        difficulty="easy",
    ),
    Question(
        text="Which company developed the Rust programming language?",
        options=["Google", "Microsoft", "Mozilla", "Apple"],
        correct_index=2,
        category="technology",
        difficulty="hard",
    ),
    Question(
        text="What is the time complexity of binary search?",
        options=["O(n)", "O(log n)", "O(n log n)", "O(1)"],
        correct_index=1,
        category="technology",
        difficulty="medium",
    ),
    Question(
        text="Who directed the movie 'Inception'?",
        options=["Steven Spielberg", "Christopher Nolan", "Martin Scorsese", "James Cameron"],
        correct_index=1,
        category="entertainment",
        difficulty="easy",
    ),
    Question(
        text="Which band released the album 'Abbey Road'?",
        options=["The Rolling Stones", "The Beatles", "Led Zeppelin", "Pink Floyd"],
        correct_index=1,
        category="entertainment",
        difficulty="easy",
    ),
    Question(
        text="What is the highest-grossing film of all time?",
        options=["Avengers: Endgame", "Avatar", "Titanic", "Star Wars: The Force Awakens"],
        correct_index=1,
        category="entertainment",
        difficulty="medium",
    ),
    Question(
        text="Who played the Joker in 'The Dark Knight'?",
        options=["Jack Nicholson", "Jared Leto", "Heath Ledger", "Joaquin Phoenix"],
        correct_index=2,
        category="entertainment",
        difficulty="easy",
    ),
    Question(
        text="Which sport is played at Wimbledon?",
        options=["Cricket", "Tennis", "Golf", "Polo"],
        correct_index=1,
        category="sports",
        difficulty="easy",
    ),
    Question(
        text="How many players are on a standard soccer team?",
        options=["9", "10", "11", "12"],
        correct_index=2,
        category="sports",
        difficulty="easy",
    ),
    Question(
        text="Which country has won the most FIFA World Cups?",
        options=["Germany", "Argentina", "Brazil", "Italy"],
        correct_index=2,
        category="sports",
        difficulty="medium",
    ),
    Question(
        text="In which sport would you perform a slam dunk?",
        options=["Volleyball", "Basketball", "Tennis", "Handball"],
        correct_index=1,
        category="sports",
        difficulty="easy",
    ),
    Question(
        text="What is the fastest recorded tennis serve speed?",
        options=["210 km/h", "230 km/h", "253 km/h", "263 km/h"],
        correct_index=3,
        category="sports",
        difficulty="hard",
    ),
    Question(
        text="Who wrote 'Romeo and Juliet'?",
        options=["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
        correct_index=1,
        category="literature",
        difficulty="easy",
    ),
    Question(
        text="Who wrote '1984'?",
        options=["Aldous Huxley", "George Orwell", "Ray Bradbury", "H.G. Wells"],
        correct_index=1,
        category="literature",
        difficulty="easy",
    ),
    Question(
        text="What is the first book of the Bible?",
        options=["Exodus", "Genesis", "Leviticus", "Deuteronomy"],
        correct_index=1,
        category="literature",
        difficulty="easy",
    ),
    Question(
        text="Who wrote 'The Brothers Karamazov'?",
        options=["Leo Tolstoy", "Anton Chekhov", "Fyodor Dostoevsky", "Ivan Turgenev"],
        correct_index=2,
        category="literature",
        difficulty="medium",
    ),
    Question(
        text="What is the value of Pi to two decimal places?",
        options=["3.12", "3.14", "3.16", "3.18"],
        correct_index=1,
        category="math",
        difficulty="easy",
    ),
    Question(
        text="What is the square root of 144?",
        options=["10", "11", "12", "13"],
        correct_index=2,
        category="math",
        difficulty="easy",
    ),
    Question(
        text="What is the derivative of x²?",
        options=["x", "2x", "x²", "2"],
        correct_index=1,
        category="math",
        difficulty="medium",
    ),
    Question(
        text="What is the integral of 1/x?",
        options=["x", "ln(x)", "1/x²", "e^x"],
        correct_index=1,
        category="math",
        difficulty="hard",
    ),
    Question(
        text="What is Euler's number approximately?",
        options=["2.718", "3.141", "1.618", "2.236"],
        correct_index=0,
        category="math",
        difficulty="medium",
    ),
    Question(
        text="What is 17 × 23?",
        options=["381", "391", "401", "371"],
        correct_index=1,
        category="math",
        difficulty="medium",
    ),
]


def get_questions_by_category(category: str) -> list[Question]:
    return [q for q in QUESTIONS_DB if q.category == category]


def get_questions_by_difficulty(difficulty: str) -> list[Question]:
    return [q for q in QUESTIONS_DB if q.difficulty == difficulty]


def get_questions(category: str, difficulty: str) -> list[Question]:
    return [
        q for q in QUESTIONS_DB
        if q.category == category and q.difficulty == difficulty
    ]


def get_filtered_questions(
    category: str | None = None,
    difficulty: str | None = None,
) -> list[Question]:
    result = QUESTIONS_DB[:]
    if category and category != "mixed":
        result = [q for q in result if q.category == category]
    if difficulty and difficulty != "mixed":
        result = [q for q in result if q.difficulty == difficulty]
    return result
