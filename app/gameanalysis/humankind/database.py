import pathlib
import json

from sqlalchemy import create_engine, inspect, Table, MetaData, select

from app.config import Config

GAME_UPDATE_LIST = [
    "world_size",
    "world_shape",
    "continent_shape",
    "climate",
    "number_of_continents",
    "new_world",
    "island_odds",
    "world_wrap",
    "hemisphere",
    "continent_spread",
    "continent_form",
    "lake_odds",
    "lake_size",
    "rivers",
    "ridges_and_cliffs",
    "elevation",
    "difficulty",
    "pace",
    "end_conditions",
]


class HumankindDatabase:
    GAME_DATA_TABLES = [
        "version",
        "lake_odds",
        "rivers",
        "end_conditions",
        "elevation",
        "lake_size",
        "ridges_and_cliffs",
        "hemisphere",
        "world_wrap",
        "island_odds",
        "new_world",
        "continent_shape",
        "number_of_continents",
        "strategic_resource",
        "luxury_resource",
        "natural_wonder",
        "world_size",
        "world_shape",
        "pace",
        "era",
        "difficulty",
        "continent_spread",
        "continent_form",
        "climate",
        "civilization",
    ]

    def __init__(self, db_name: str = "humankind"):
        self.engine = create_engine(Config.db_url(db_name), echo=False)
        meta = MetaData()
        table_names = inspect(self.engine).get_table_names()
        self.table_dict = {
            t: Table(t, meta, autoload_with=self.engine) for t in table_names
        }

    def _get_id(self, table: str, descriptor: str):
        sel = select(self.table_dict[table].c.id).where(
            self.table_dict[table].c.descriptor == descriptor
        )
        with self.engine.connect() as conn:
            return conn.execute(sel).fetchone()

    def _load_row(self, table: str, data: dict) -> None:
        with self.engine.connect() as conn:
            conn.execute(self.table_dict[table].insert(), data)
            conn.commit()

    def load_game_data(self, data_path: pathlib.Path) -> None:
        data = json.loads(data_path.read_text())
        for table in self.GAME_DATA_TABLES:
            for row in data[table]:
                if self._get_id(table, row["descriptor"]) is None:
                    if "version" in row:
                        row["version"] = self._get_id("version", row["version"])[0]
                    if "era" in row:
                        row["era"] = self._get_id("era", row["era"])[0]
                    self._load_row(table, row)

    def load_game_plays(self, data_path: pathlib.Path) -> None:
        games = json.loads(data_path.read_text())
        for game in games:
            if self._get_id("game", game["descriptor"]) is not None:
                continue

            row = {
                "descriptor": game["descriptor"],
                "seed": game["game_setup"]["seed"],
                "land_percentage": game["game_setup"]["land_percentage"],
                "version": self._get_id("version", game["version"])[0],
                "start_date": game["start_date"],
                "end_date": game["end_date"],
            }
            for attr in GAME_UPDATE_LIST:
                row[attr] = self._get_id(attr, game["game_setup"][attr])[0]

            self._load_row("game", row)
            game_id = self._get_id("game", game["descriptor"])[0]

            if "natural_wonder" in game:
                for wonder in game["natural_wonder"]:
                    self._load_row(
                        "natural_wonder_link",
                        {
                            "game_id": game_id,
                            "natural_wonder": self._get_id(
                                "natural_wonder", wonder
                            )[0],
                        },
                    )

            if "luxury_resource" in game:
                for luxury in game["luxury_resource"]:
                    self._load_row(
                        "luxury_resource_link",
                        {
                            "game_id": game_id,
                            "resource_id": self._get_id(
                                "luxury_resource", luxury["resource"]
                            )[0],
                            "quantity": luxury["quantity"],
                        },
                    )
