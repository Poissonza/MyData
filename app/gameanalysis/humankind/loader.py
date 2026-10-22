from __future__ import annotations

from app.storage.loader import JsonDeltaLoader


class HumankindLoader(JsonDeltaLoader):
    TABLE_NAME = "gameanalysis/humankind"
    PARTITION_BY = ["version"]

    def _parse(self, games: list) -> list[dict]:
        rows = []
        for game in games:
            setup = game.get("game_setup", {})
            row = {
                "descriptor": game["descriptor"],
                "version": game.get("version"),
                "start_date": game.get("start_date"),
                "end_date": game.get("end_date"),
                "seed": setup.get("seed"),
                "land_percentage": setup.get("land_percentage"),
                "world_size": setup.get("world_size"),
                "world_shape": setup.get("world_shape"),
                "continent_shape": setup.get("continent_shape"),
                "climate": setup.get("climate"),
                "number_of_continents": setup.get("number_of_continents"),
                "new_world": setup.get("new_world"),
                "island_odds": setup.get("island_odds"),
                "world_wrap": setup.get("world_wrap"),
                "hemisphere": setup.get("hemisphere"),
                "continent_spread": setup.get("continent_spread"),
                "continent_form": setup.get("continent_form"),
                "lake_odds": setup.get("lake_odds"),
                "lake_size": setup.get("lake_size"),
                "rivers": setup.get("rivers"),
                "ridges_and_cliffs": setup.get("ridges_and_cliffs"),
                "elevation": setup.get("elevation"),
                "difficulty": setup.get("difficulty"),
                "pace": setup.get("pace"),
                "end_conditions": setup.get("end_conditions"),
                "natural_wonders": game.get("natural_wonder", []),
                "luxury_resources": [
                    f"{r['resource']}:{r['quantity']}"
                    for r in game.get("luxury_resource", [])
                ],
            }
            rows.append(row)
        return rows
