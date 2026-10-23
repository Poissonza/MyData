from data import Col, Tab

REFERENCE_TABS = [
    Tab("Speed", "The Game Speed Options", "speed"),
    Tab("Difficulty", "The Game Difficulty Options", "difficulty"),
    Tab("Factions", "The Factions in the Game", "faction"),
    Tab("Map", "The Map the game is played on", "map"),
]

id_col = Col("id")

TABLES = {
    "speed": [id_col, Col("name"), Col("description", "long_text")],
    "difficulty": [id_col, Col("name")],
    "faction": [id_col, Col("name"), Col("description", "long_text")],
    "map": [id_col, Col("name"), Col("description", "long_text")],
}
