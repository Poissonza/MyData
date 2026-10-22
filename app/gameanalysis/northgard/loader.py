from __future__ import annotations

from app.storage.loader import JsonDeltaLoader


class NorthgardLoader(JsonDeltaLoader):
    TABLE_NAME = "gameanalysis/northgard"
    PARTITION_BY = ["difficulty"]

    def _parse(self, games: list) -> list[dict]:
        rows = []
        for game in games:
            outcome = game.get("Outcome", {})
            row = {
                "game_name": game["Game_name"],
                "date": game.get("Date"),
                "clan": game.get("clan"),
                "military": game.get("Military"),
                "color": game.get("Color"),
                "difficulty": game.get("Difficulty"),
                "map_size": game.get("Map_size"),
                "military_path": game.get("Military_Path"),
                "events": [
                    f"{e['Year']}-{e['Month']}: {e['Event']}"
                    for e in game.get("Events", [])
                ],
                "opponents": [
                    f"{o['clan']} ({o.get('Military', '')})"
                    for o in game.get("Opponents", [])
                ],
                "outcome_condition": outcome.get("Condition"),
                "outcome_year": outcome.get("year"),
                "outcome_month": outcome.get("month"),
            }
            rows.append(row)
        return rows
