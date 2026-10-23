from data import Col, Tab

REFERENCE_TABS = [
    Tab("Speed", "The Game Speed Options", "speeds"),
    Tab("Difficulty", "The Game Difficulty Options", "difficulty"),
    Tab("Factions", "The Factions in the Game", "faction"),
    Tab("Map", "The Map the game is played on", "maps"),
    Tab("World Size", "The World Size Options", "world_sizes"),
]

id_col = Col("id")

TABLES = {
    "speeds": [
        id_col,
        Col("name", unique=True, required=True),
        Col("description", "long_text"),
    ],
    "difficulty": [id_col, Col("name", unique=True, required=True)],
    "faction": [
        id_col,
        Col("name", unique=True, required=True),
        Col("description", "long_text"),
    ],
    "maps": [
        id_col,
        Col("name", unique=True, required=True),
        Col("description", "long_text"),
    ],
    "world_sizes": [
        id_col,
        Col("name", unique=True, required=True),
        Col("number_of_players", "int"),
        Col("description", "long_text"),
    ],
}
