from sqlalchemy import create_engine, inspect, Table, MetaData, select
import pathlib
import json

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
    "continent_form",
]


class HumankindDB:

    def __init__(self):
        self.engine = create_engine(
            "postgresql://humankind:humankind@localhost:5432/humankind", echo=False
        )
        inspection = inspect(self.engine)
        self.table_names = inspection.get_table_names()
        meta = MetaData()
        self.game_data_tables = [
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
        self.table_dict = {}
        [
            self.table_dict.update(
                {table_name: Table(table_name, meta, autoload_with=self.engine)}
            )
            for table_name in self.table_names
        ]

    def load_game_data(self, data_location):
        data = json.loads(data_location.read_text())
        for table in self.game_data_tables:
            self.load_data(table, data[table])

    def get_id(self, table, descriptor):
        sel = select(self.table_dict[table].c.id).where(
            self.table_dict[table].c.descriptor == descriptor
        )
        return self.engine.execute(sel).fetchone()

    def load_data(self, table, data):
        ins = self.table_dict[table].insert()
        for object in data:
            if self.get_id(table, object["descriptor"]) is None:
                if "version" in object:
                    try:
                        object.update(
                            {"version": self.get_id("version", object["version"])[0]}
                        )
                    except Exception as e:
                        raise ValueError(
                            f"Could not find the value {object['version']} in version"
                        )
                if "era" in object:
                    try:
                        object.update({"era": self.get_id("era", object["era"])[0]})
                    except Exception:
                        raise ValueError(
                            f"Could not find the value {object['era']} in era"
                        )
                self.engine.execute(ins, object)

    def load_game_plays(self, data_location):
        ins = self.table_dict["game"].insert()

        games = json.loads(data_location.read_text())
        for game in games:
            if self.get_id("game", game["descriptor"]) is None:
                final_game = {
                    "descriptor": game["descriptor"],
                    "seed": game["game_setup"]["seed"],
                    "land_percentage": game["game_setup"]["land_percentage"],
                    "version": self.get_id("version", game["version"])[0],
                    "start_date": game["start_date"],
                    "end_date": game["end_date"],
                }
                for attribute in GAME_UPDATE_LIST:
                    try:
                        final_game.update(
                            {
                                attribute: self.get_id(
                                    attribute, game["game_setup"][attribute]
                                )[0]
                            }
                        )
                    except:
                        raise ValueError(
                            f"Could not find the value: {game['game_setup'][attribute]} in {attribute}"
                        )
                self.engine.execute(ins, final_game)

                if "natural_wonder" in game:
                    ins_wonder = self.table_dict["natural_wonder_link"].insert()
                    for natural_wonder in game["natural_wonder"]:
                        try:
                            game_id = self.get_id("game", game["descriptor"])[0]
                        except:
                            raise ValueError(
                                f"Could not find the value: {game['descriptor']} in game"
                            )
                        try:
                            wonder_id = self.get_id("natural_wonder", natural_wonder)[0]
                        except:
                            raise ValueError(
                                f"Could not find the value: {natural_wonder} in Natural Wonders for {game['descriptor']}"
                            )
                        insert_data = {"game_id": game_id, "natural_wonder": wonder_id}
                        self.engine.execute(ins_wonder, insert_data)

                if "luxury_resource" in game:
                    ins_luxury = self.table_dict["luxury_resource_link"].insert()
                    for luxury in game["luxury_resource"]:
                        insert_data = {
                            "game_id": self.get_id("game", game["descriptor"])[0],
                            "resource_id": self.get_id(
                                "luxury_resource", luxury["resource"]
                            )[0],
                            "quantity": luxury["quantity"],
                        }
                        self.engine.execute(ins_luxury, insert_data)


game_data = pathlib.Path("data") / "Humankind" / "Game data.json"

games_played = pathlib.Path("data") / "Humankind" / "games_played.json"

db = HumankindDB()
db.load_game_data(game_data)
db.load_game_plays(games_played)
