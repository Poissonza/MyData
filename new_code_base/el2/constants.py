from data import Col, Tab

REFERENCE_TABS = [
    Tab("Speed", "The Game Speed Options", "speed"),
    Tab("Difficulty", "The Game Difficulty Options", "difficulty"),
    Tab("Factions", "The Factions in the Game", "faction"),
]

id_col = Col("ID")

TABLES = {
    "speed": [id_col, Col("name"), Col("description")],
    "difficulty": [id_col, Col("name")],
    "faction": [id_col, Col("name"), Col("description")],
}

TABLE_NAMES = ["speed", "difficulty"]
