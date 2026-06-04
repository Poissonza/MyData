import pathlib
import json

from sqlalchemy import create_engine, inspect, MetaData, Table, select

from app.config import Config


class Civ6Database:
    REFERENCE_TABLES = [
        "expansion",
        "city_state",
        "civilization",
        "game_mode",
        "game_speed",
        "luxury_resource",
        "map_feature",
        "map_type",
        "secret_society",
        "wonder",
    ]

    def __init__(self, db_name: str = "civ6"):
        self.engine = create_engine(Config.db_url(db_name), echo=False)
        meta = MetaData()
        table_names = inspect(self.engine).get_table_names()
        self.table_dict = {
            t: Table(t, meta, autoload_with=self.engine) for t in table_names
        }

    def _get_id(self, table: str, column: str, value: str):
        sel = select(self.table_dict[table].c.id).where(
            self.table_dict[table].c[column] == value
        )
        with self.engine.connect() as conn:
            return conn.execute(sel).fetchone()

    def _insert(self, table: str, data: dict) -> None:
        with self.engine.connect() as conn:
            conn.execute(self.table_dict[table].insert(), data)
            conn.commit()

    def load_default_data(self, data_path: pathlib.Path) -> None:
        data = json.loads(data_path.read_text())
        self._fill_expansions(data["expansion"])
        self._fill_city_states(data["citystate"])
        self._fill_civilizations(data["civilization"])
        self._fill_game_modes(data["gamemode"])
        self._fill_game_speeds(data["gamespeed"])
        self._fill_luxury_resources(data["luxuryresource"])
        self._fill_map_features(data["mapfeature"])
        self._fill_map_types(data["maptype"])
        self._fill_secret_societies(data["secret_society"])
        self._fill_wonders(data["wonder"])

    def load_games(self, data_path: pathlib.Path) -> None:
        games = json.loads(data_path.read_text())
        for game in games:
            if self._get_id("game", "game_name", game["game_name"]) is not None:
                continue
            game_row = {
                "game_name": game["game_name"],
                "game_seed": game["game_seed"],
                "map_seed": game["map_seed"],
                "map_type": self._get_id("map_type", "map_type", game["map_type"])[0],
                "civ_played": self._get_id(
                    "civilization", "leader", game["civ_leader"]
                )[0],
                "difficulty": game["difficulty"],
                "game_speed": self._get_id("game_speed", "game_speed", game["game_speed"])[0],
                "game_version": game["game_version"],
            }
            if "secretsociety" in game:
                game_row["secret_society"] = self._get_id(
                    "secret_society", "secret_society", game["secretsociety"]
                )[0]
            self._insert("game", game_row)
            game_id = self._get_id("game", "game_name", game["game_name"])[0]

            for mode in game.get("game_modes", []):
                self._insert(
                    "game_mode_link",
                    {"game": game_id, "game_mode": self._get_id("game_mode", "game_mode", mode)[0]},
                )
            for wonder in game.get("wonders", []):
                self._insert(
                    "wonder_link",
                    {"game": game_id, "wonder": self._get_id("wonder", "wonder", wonder)[0]},
                )
            for opponent in game.get("opponents", []):
                self._insert(
                    "opponent_link",
                    {
                        "game": game_id,
                        "civilization": self._get_id("civilization", "leader", opponent["leader"])[0],
                    },
                )
            for city_state in game.get("citystates", []):
                self._insert(
                    "city_state_link",
                    {
                        "game": game_id,
                        "city_state": self._get_id("city_state", "city_state", city_state)[0],
                    },
                )
            for luxury in game.get("luxuryresources", []):
                self._insert(
                    "luxury_resource_link",
                    {
                        "game": game_id,
                        "luxury_resource": self._get_id("luxury_resource", "luxury_resource", luxury)[0],
                    },
                )
            for feature in game.get("mapfeatures", []):
                self._insert(
                    "map_feature_link",
                    {
                        "game": game_id,
                        "map_feature": self._get_id("map_feature", "feature", feature["map_feature"])[0],
                        "feature_count": feature["feature_count"],
                    },
                )
            results = game["results"]
            self._insert(
                "results",
                {
                    "game": game_id,
                    "number_of_turns": results["number_of_turns"],
                    "score": results["score"],
                    "victory_condition": results["victory_condition"],
                },
            )

    def _fill_expansions(self, data: list) -> None:
        for row in data:
            if self._get_id("expansion", "expansion", row["expansion"]) is None:
                self._insert("expansion", row)

    def _fill_city_states(self, data: list) -> None:
        for row in data:
            if self._get_id("city_state", "city_state", row["city_state"]) is None:
                row["expansion"] = self._get_id("expansion", "expansion", row["expansion"])[0]
                self._insert("city_state", row)

    def _fill_civilizations(self, data: list) -> None:
        for row in data:
            if self._get_id("civilization", "leader", row["leader"]) is None:
                row["expansion"] = self._get_id("expansion", "expansion", row["expansion"])[0]
                self._insert("civilization", row)

    def _fill_game_modes(self, data: list) -> None:
        for mode in data:
            if self._get_id("game_mode", "game_mode", mode) is None:
                self._insert("game_mode", {"game_mode": mode})

    def _fill_game_speeds(self, data: list) -> None:
        for speed in data:
            if self._get_id("game_speed", "game_speed", speed) is None:
                self._insert("game_speed", {"game_speed": speed})

    def _fill_luxury_resources(self, data: list) -> None:
        for row in data:
            if self._get_id("luxury_resource", "luxury_resource", row["luxury_resource"]) is None:
                row["expansion"] = self._get_id("expansion", "expansion", row["expansion"])[0]
                self._insert("luxury_resource", row)

    def _fill_map_features(self, data: list) -> None:
        for row in data:
            if self._get_id("map_feature", "feature", row["feature"]) is None:
                row["expansion"] = self._get_id("expansion", "expansion", row["expansion"])[0]
                self._insert("map_feature", row)

    def _fill_map_types(self, data: list) -> None:
        for map_type in data:
            if self._get_id("map_type", "map_type", map_type) is None:
                self._insert("map_type", {"map_type": map_type})

    def _fill_secret_societies(self, data: list) -> None:
        for society in data:
            if self._get_id("secret_society", "secret_society", society) is None:
                self._insert("secret_society", {"secret_society": society})

    def _fill_wonders(self, data: list) -> None:
        for row in data:
            if self._get_id("wonder", "wonder", row["wonder"]) is None:
                row["expansion"] = self._get_id("expansion", "expansion", row["expansion"])[0]
                self._insert("wonder", row)
