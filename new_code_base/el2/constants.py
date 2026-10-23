from data import Col, Tab

REFERENCE_TABS = [
    Tab("Speed", "The Game Speed Options", "speed"),
    Tab("Difficulty", "The Game Difficulty Options", "difficulty"),
]


TABLES = {
    "speed": [Col("id"), Col("name"), Col("description")],
    "difficulty": [Col("id"), Col("name")],
}

TABLE_NAMES = ["speed", "difficulty"]
