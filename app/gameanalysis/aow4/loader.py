from __future__ import annotations

from app.storage.loader import JsonDeltaLoader


class AOW4Loader(JsonDeltaLoader):
    TABLE_NAME = "gameanalysis/aow4"
    PARTITION_BY = ["difficulty"]

    def _parse(self, game_data: dict) -> list[dict]:
        rows = []
        for game in game_data.get("Game_Played", []):
            row = {
                "name": game["Name"],
                "realm": game.get("Realm"),
                "player_distance": game.get("Player_Distance"),
                "players": game.get("Players"),
                "difficulty": game.get("Difficulty"),
                "turn_system": game.get("Turn_System"),
                "faction": game.get("Faction"),
                "opponents": game.get("Opponents", []),
            }
            rows.append(row)
        return rows
