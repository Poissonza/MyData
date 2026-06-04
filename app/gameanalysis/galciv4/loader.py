from __future__ import annotations

from app.storage.loader import JsonDeltaLoader


class GalCiv4Loader(JsonDeltaLoader):
    TABLE_NAME = "gameanalysis/galciv4"
    PARTITION_BY = ["version"]

    def _parse(self, play_data: dict) -> list[dict]:
        rows = []
        for name, game in play_data.items():
            if not game.get("complete"):
                continue
            row = {
                "name": name,
                **game["setup"],
                "opponents": game.get("opponent", []),
                "victory_conditions": game.get("victory_conditions", []),
                **game["results"],
            }
            rows.append(row)
        return rows
