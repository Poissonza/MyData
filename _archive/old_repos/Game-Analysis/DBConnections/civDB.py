from sqlalchemy import (
    create_engine,
    Table,
    MetaData,
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    select,
)
import pathlib
import json


class civdb:
    def __init__(self, default_data_location=None):
        self.engine = create_engine(
            "postgresql://civ:civ@localhost:5432/civ6", echo=False
        )
        self.load_tables()

        if default_data_location:
            self.fill_default_data(default_data_location)

    def load_tables(self):
        meta = MetaData()
        self.expansion = Table("expansion", meta, autoload_with=self.engine)
        self.city_state_table = Table("city_state", meta, autoload_with=self.engine)
        self.civilization_table = Table("civilization", meta, autoload_with=self.engine)
        self.game_mode_table = Table("game_mode", meta, autoload_with=self.engine)
        self.game_speed_table = Table("game_speed", meta, autoload_with=self.engine)
        self.luxury_table = Table("luxury_resource", meta, autoload_with=self.engine)
        self.map_feature_table = Table("map_feature", meta, autoload_with=self.engine)
        self.map_type_table = Table("map_type", meta, autoload_with=self.engine)
        self.secret_society_table = Table(
            "secret_society", meta, autoload_with=self.engine
        )
        self.wonder_table = Table("wonder", meta, autoload_with=self.engine)
        self.game_table = Table("game", meta, autoload_with=self.engine)
        self.game_mode_link_table = Table(
            "game_mode_link", meta, autoload_with=self.engine
        )
        self.wonder_link_table = Table("wonder_link", meta, autoload_with=self.engine)
        self.opponent_link_table = Table(
            "opponent_link", meta, autoload_with=self.engine
        )
        self.city_state_link_table = Table(
            "city_state_link", meta, autoload_with=self.engine
        )
        self.results_table = Table("results", meta, autoload_with=self.engine)
        self.map_feature_link_table = Table(
            "map_feature_link", meta, autoload_with=self.engine
        )
        self.luxury_resource_link_table = Table(
            "luxury_resource_link", meta, autoload_with=self.engine
        )

    def fill_default_data(self, default_data_location):
        default_data = json.loads(default_data_location.read_text())
        self.fill_expansion(default_data["expansion"])
        self.fill_city_state(default_data["citystate"])
        self.fill_civilization(default_data["civilization"])
        self.fill_game_mode(default_data["gamemode"])
        self.fill_game_speed(default_data["gamespeed"])
        self.fill_luxury_data(default_data["luxuryresource"])
        self.fill_map_feature(default_data["mapfeature"])
        self.fill_map_type(default_data["maptype"])
        self.fill_secret_society(default_data["secret_society"])
        self.fill_wonder(default_data["wonder"])

    def insert_city_state(self, city_state):
        ins = self.city_state_table.insert()
        self.engine.execute(ins, city_state)

    def insert_city_state_link(self, city_state_link):
        ins = self.city_state_link_table.insert()
        self.engine.execute(ins, city_state_link)

    def insert_civilization(self, civilization):
        ins = self.civilization_table.insert()
        self.engine.execute(ins, civilization)

    def insert_expansion(self, expansion):
        ins = self.expansion.insert()
        self.engine.execute(ins, expansion)

    def insert_game(self, game):
        ins = self.game_table.insert()
        self.engine.execute(ins, game)

    def insert_game_mode(self, game_mode):
        ins = self.game_mode_table.insert()
        self.engine.execute(ins, game_mode)

    def insert_game_mode_link(self, game_mode_link):
        ins = self.game_mode_link_table.insert()
        self.engine.execute(ins, game_mode_link)

    def insert_game_speed(self, game_speed):
        ins = self.game_speed_table.insert()
        self.engine.execute(ins, game_speed)

    def insert_luxury(self, luxury_data):
        ins = self.luxury_table.insert()
        self.engine.execute(ins, luxury_data)

    def insert_luxury_link(self, luxury_resource_link):
        ins = self.luxury_resource_link_table.insert()
        self.engine.execute(ins, luxury_resource_link)

    def insert_map_feature(self, map_feature):
        ins = self.map_feature_table.insert()
        self.engine.execute(ins, map_feature)

    def insert_map_feature_link(self, map_feature_link):
        ins = self.map_feature_link_table.insert()
        self.engine.execute(ins, map_feature_link)

    def insert_map_type(self, map_type):
        ins = self.map_type_table.insert()
        self.engine.execute(ins, map_type)

    def insert_opponent_link(self, opponent_link):
        ins = self.opponent_link_table.insert()
        self.engine.execute(ins, opponent_link)

    def insert_results(self, results, game_id):
        ins = self.results_table.insert()
        results.update({"game": game_id})
        self.engine.execute(ins, results)

    def insert_secret_society(self, secret_society):
        ins = self.secret_society_table.insert()
        self.engine.execute(ins, secret_society)

    def insert_wonder(self, wonder):
        ins = self.wonder_table.insert()
        self.engine.execute(ins, wonder)

    def insert_wonder_link(self, wonder_link):
        ins = self.wonder_link_table.insert()
        self.engine.execute(ins, wonder_link)

    def fill_city_state(self, city_state_data):
        for city_state in city_state_data:
            if self.get_city_state_id(city_state["city_state"]) is None:
                if self.get_expansion_id(city_state["expansion"]) is None:
                    raise ValueError(
                        f"The Expansion {city_state['expansion']} does not exist"
                    )
                else:
                    city_state.update(
                        {"expansion": self.get_expansion_id(city_state["expansion"])[0]}
                    )
                self.insert_city_state(city_state)

    def fill_city_state_link(self, city_state_link_data, game_id):
        for city_state_link in city_state_link_data:
            try:
                self.insert_city_state_link(
                    {
                        "game": game_id,
                        "city_state": self.get_city_state_id(city_state_link)[0],
                    }
                )
            except:
                raise ValueError(f"Could not find city State {city_state_link}")

    def fill_civilization(self, civilization_data):
        for civilization in civilization_data:
            if (
                self.get_civilization_id(
                    civilization["leader"], civilization["country"]
                )
                is None
            ):
                civilization.update(
                    {"expansion": self.get_expansion_id(civilization["expansion"])[0]}
                )
                self.insert_civilization(civilization)

    def fill_expansion(self, expansion_data):
        for expansion in expansion_data:
            if self.get_expansion_id(expansion["expansion"]) is None:
                self.insert_expansion(expansion)

    def fill_game(self, game_data):
        for game in game_data:
            if self.get_game_id(game["game_name"]) is None:
                game_data = {
                    "game_name": game["game_name"],
                    "game_seed": game["game_seed"],
                    "map_seed": game["map_seed"],
                    "map_type": self.get_map_type_id(game["map_type"])[0],
                    "civ_played": self.get_civilization_id(
                        leader_name=game["civ_leader"], country_name=game["civ_country"]
                    )[0],
                    "difficulty": game["difficulty"],
                    "game_speed": self.get_game_speed_id(game["game_speed"])[0],
                    "game_version": game["game_version"],
                }
                if "secretsociety" in game:
                    game_data.update(
                        {
                            "secret_society": self.get_secret_society_id(
                                game["secretsociety"]
                            )[0]
                        }
                    )
                self.insert_game(game_data)
                game_id = self.get_game_id(game["game_name"])[0]
                self.fill_game_mode_link(game["game_modes"], game_id)
                self.fill_wonder_link(game["wonders"], game_id)
                self.fill_oponent_link(game["opponents"], game_id)
                self.fill_city_state_link(game["citystates"], game_id)
                self.insert_results(game["results"], game_id)
                if "mapfeatures" in game:
                    self.fill_map_feature_link(game["mapfeatures"], game_id)
                self.fill_luxury_link(game["luxuryresources"], game_id)

    def fill_game_mode(self, game_mode_data):
        for game_mode in game_mode_data:
            if self.get_game_mode_id(game_mode) is None:
                game_mode = {"game_mode": game_mode}
                self.insert_game_mode(game_mode)

    def fill_game_mode_link(self, game_mode_link_data, game_id):
        for game_mode_link in game_mode_link_data:
            self.insert_game_mode_link(
                {"game": game_id, "game_mode": self.get_game_mode_id(game_mode_link)[0]}
            )

    def fill_game_speed(self, game_speed_data):
        for game_speed in game_speed_data:
            if self.get_game_speed_id(game_speed) is None:
                self.insert_game_speed({"game_speed": game_speed})

    def fill_luxury_data(self, luxury_data):
        for luxury in luxury_data:
            if self.get_luxury_id(luxury["luxury_resource"]) is None:
                luxury.update(
                    {"expansion": self.get_expansion_id(luxury["expansion"])[0]}
                )
                self.insert_luxury(luxury)

    def fill_luxury_link(self, luxury_link_data, game_id):
        for luxury_link in luxury_link_data:
            try:
                self.insert_luxury_link(
                    {
                        "game": game_id,
                        "luxury_resource": self.get_luxury_id(luxury_link)[0],
                    }
                )
            except:
                print(
                    f"Had an issue with Luxury: {luxury_link} with game id: {game_id}"
                )

    def fill_map_feature(self, map_feature_data):
        for map_feature in map_feature_data:
            if self.get_map_feature_id(map_feature["feature"]) is None:
                map_feature.update(
                    {"expansion": self.get_expansion_id(map_feature["expansion"])[0]}
                )
                self.insert_map_feature(map_feature)

    def fill_map_feature_link(self, map_feature_link_data, game_id):
        for map_feature in map_feature_link_data:
            map_feature.update(
                {
                    "game": game_id,
                    "map_feature": self.get_map_feature_id(map_feature["map_feature"])[
                        0
                    ],
                }
            )
            self.insert_map_feature_link(map_feature)

    def fill_map_type(self, map_type_data):
        for map_type in map_type_data:
            if self.get_map_type_id(map_type) is None:
                self.insert_map_type({"map_type": map_type})

    def fill_oponent_link(self, opponent_data, game_id):
        for opponent in opponent_data:
            try:
                self.insert_opponent_link(
                    {
                        "civilization": self.get_civilization_id(
                            opponent["leader"], opponent["country"]
                        )[0],
                        "game": game_id,
                    }
                )
            except:
                raise ValueError(
                    f"Could not find the civilization with leader: {opponent['leader']} and country {opponent['country']}"
                )

    def fill_secret_society(self, secret_society_data):
        for secret_society in secret_society_data:
            if self.get_secret_society_id(secret_society) is None:
                self.insert_secret_society({"secret_society": secret_society})

    def fill_wonder(self, wonder_data):
        for wonder in wonder_data:
            if self.get_wonder_id(wonder["wonder"]) is None:
                wonder.update(
                    {"expansion": self.get_expansion_id(wonder["expansion"])[0]}
                )
                self.insert_wonder(wonder)

    def fill_wonder_link(self, wonder_link_data, game_id):
        for wonder_link in wonder_link_data:
            try:
                self.insert_wonder_link(
                    {"wonder": self.get_wonder_id(wonder_link)[0], "game": game_id}
                )
            except:
                print(f"Issue with Wonder: {wonder_link} with Game ID {game_id} ")

    def get_city_state_id(self, city_state_name):
        sel = select(self.city_state_table.c.id).where(
            self.city_state_table.c.city_state == city_state_name
        )
        return self.engine.execute(sel).fetchone()

    def get_civilization_id(self, leader_name, country_name):
        sel = select(self.civilization_table.c.id).where(
            self.civilization_table.c.leader == leader_name,
            self.civilization_table.c.country == country_name,
        )
        return self.engine.execute(sel).fetchone()

    def get_expansion_id(self, expansion_name):
        sel = select(self.expansion.c.id).where(
            self.expansion.c.expansion == expansion_name
        )
        return self.engine.execute(sel).fetchone()

    def get_game_mode_id(self, game_mode_name):
        sel = select(self.game_mode_table.c.id).where(
            self.game_mode_table.c.game_mode == game_mode_name
        )
        return self.engine.execute(sel).fetchone()

    def get_game_id(self, game_name):
        sel = select(self.game_table.c.id).where(
            self.game_table.c.game_name == game_name
        )
        return self.engine.execute(sel).fetchone()

    def get_game_speed_id(self, game_speed):
        sel = select(self.game_speed_table.c.id).where(
            self.game_speed_table.c.game_speed == game_speed
        )
        return self.engine.execute(sel).fetchone()

    def get_luxury_id(self, luxury):
        sel = select(self.luxury_table.c.id).where(
            self.luxury_table.c.luxury_resource == luxury
        )
        return self.engine.execute(sel).fetchone()

    def get_map_feature_id(self, map_feature):
        sel = select(self.map_feature_table.c.id).where(
            self.map_feature_table.c.feature == map_feature
        )
        return self.engine.execute(sel).fetchone()

    def get_map_type_id(self, map_type):
        sel = select(self.map_type_table.c.id).where(
            self.map_type_table.c.map_type == map_type
        )
        return self.engine.execute(sel).fetchone()

    def get_secret_society_id(self, secret_society):
        sel = select(self.secret_society_table.c.id).where(
            self.secret_society_table.c.secret_society == secret_society
        )
        return self.engine.execute(sel).fetchone()

    def get_wonder_id(self, wonder):
        sel = select(self.wonder_table.c.id).where(self.wonder_table.c.wonder == wonder)
        return self.engine.execute(sel).fetchone()


data_file = pathlib.Path("data") / "Civilization 6" / "default_data.json"
civ = civdb(data_file)

game_file = pathlib.Path("data") / "Civilization 6" / "Game_played.json"
game_data = json.loads(game_file.read_text())
civ.fill_game(game_data)
