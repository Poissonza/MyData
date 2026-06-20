from app.botc.storage import (BOTCPlayersWriter)

import json
import pathlib

DIRECTORY = pathlib.Path(__file__).parent / "data"

def _load_json(filename: str) -> dict:
    return json.loads((DIRECTORY / filename).read_bytes())

def _load_players():
    data = _load_json("botc_data.json")
    BOTCPlayersWriter().write(
        data = data["players"],
        mode = "overwrite",
        make_id=True,
        id_col="name"
    )

if __name__ == "__main__":
    _load_players()