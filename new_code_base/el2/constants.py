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
        Col("name", unique=True, required=True, label="Name"),
        Col("description", "long_text", label="Description"),
    ],
    "difficulty": [id_col, Col("name", unique=True, required=True, label="Name")],
    "faction": [
        id_col,
        Col("name", unique=True, required=True, label="Name"),
        Col("description", "long_text", label="Description"),
    ],
    "maps": [
        id_col,
        Col("name", unique=True, required=True, label="Name"),
        Col("description", "long_text", label="Description"),
    ],
    "world_sizes": [
        id_col,
        Col("name", unique=True, required=True, label="Name"),
        Col("number_of_players", "int", label="Number of Players"),
        Col("description", "long_text", label="Description"),
    ],
}
