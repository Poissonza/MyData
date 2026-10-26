from data import Col, Tab

REFERENCE_TABS = [
    Tab("Speed", "The Game Speed Options", "speeds"),
    Tab("Difficulty", "The Game Difficulty Options", "difficulty"),
    Tab("Factions", "The Factions in the Game", "faction"),
    Tab("Map", "The Map the game is played on", "maps"),
    Tab("World Size", "The World Size Options", "world_sizes"),
]

id_col = Col("id", "int", unique=True, label="ID")

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
    "games": [
        id_col,
        Col("ai_simultaneos_turns", "bool", label="AI Simultaneous Turns"),
        Col(
            "allow_fortress_instant_resolve",
            "bool",
            label="Allow Fortress Instant Resolve",
        ),
        Col("force_instant_resolve", "bool", label="Force Instant Resolve"),
        Col("peaceful_mode", "bool", label="Peaceful Mode"),
        Col("allow_optional_events", "bool", label="Allow Optional Events"),
        Col("score_victory", "bool", label="Score Victory"),
        Col("conquest_victory", "bool", label="Conquest Victory"),
        Col("worship_victory_path", "bool", label="Worship Victory Path"),
        Col("impress_victory_path", "bool", label="Impress Victory Path"),
        Col("master_victory_path", "bool", label="Master Victory Path"),
    ],
    "events":[
        id_col,
        Col("name", unique=True, required=True, label="Name"),
        Col("event_type", "int", label="Event Type"),
        Col("description", "long_text", label="Description"),
    ]
}
