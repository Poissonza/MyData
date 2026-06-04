from __future__ import annotations

from app.storage.loader import JsonDeltaLoader


class Civ6Loader(JsonDeltaLoader):
    TABLE_NAME = "gameanalysis/civ6"
    PARTITION_BY = ["game_speed"]

    def _parse(self, game_data: list) -> list[dict]:
        rows = []
        for game in game_data:
            results = game.get("results", {})
            row = {
                "game_name": game["game_name"],
                "game_seed": game.get("game_seed"),
                "map_seed": game.get("map_seed"),
                "map_type": game.get("map_type"),
                "map_size": game.get("map_size"),
                "civ_leader": game["civ_leader"],
                "civ_country": game["civ_country"],
                "difficulty": game.get("difficulty"),
                "game_speed": game.get("game_speed"),
                "game_version": game.get("game_version"),
                "game_modes": game.get("game_modes", []),
                "wonders": game.get("wonders", []),
                "opponents": [
                    f"{o['leader']} ({o['country']})"
                    for o in game.get("opponents", [])
                ],
                "city_states": game.get("citystates", []),
                "luxury_resources": game.get("luxuryresources", []),
                "map_features": [
                    f"{f['map_feature']}:{f['feature_count']}"
                    for f in game.get("mapfeatures", [])
                ],
                "secret_society": game.get("secretsociety"),
                "turns": results.get("number_of_turns"),
                "score": results.get("score"),
                "victory_condition": results.get("victory_condition"),
            }
            rows.append(row)
        return rows
