import pandas as pd
from sqlalchemy import create_engine, MetaData, inspect
import pathlib
import json
from table_creations import GalCivTables
from table_insertions import GalCivInsertion
from table_queries import GalCivQuery
import matplotlib.pyplot as plt


class galcivdb:

    def __init__(
        self,
        game_data_location: pathlib.Path,
        play_data_location: pathlib.Path,
        create_tables: bool = True,
    ):
        self.engine = create_engine(
            "postgresql://galciv:galciv@localhost:5432/galciv4", echo=False
        )
        self.game_data = self.get_game_data(game_data_location)
        self.play_data = self.get_play_data(play_data_location)
        self.fill_data()
        self.fill_query()

    def get_game_data(self, location):
        data = location.read_text()
        return json.loads(data)

    def get_play_data(self, location):
        data = location.read_text()
        return json.loads(data)

    def fill_data(self):
        civ_ins = GalCivInsertion(self.engine)

        civ_ins.fill_version(self.game_data["version"])
        civ_ins.fill_anomolies(self.game_data["anomolies"])
        civ_ins.fill_abilities(self.game_data["abilities"])
        civ_ins.fill_ascension_crystal(self.game_data["ascension_crystals"])
        civ_ins.fill_asteroid(self.game_data["asteroid"])
        civ_ins.fill_biology(self.game_data["biology"])
        civ_ins.fill_black_hole(self.game_data["black_holes"])
        civ_ins.fill_civilization_proximity(self.game_data["civilization_proximity"])
        civ_ins.fill_galaxy_difficulty(self.game_data["galaxy_difficulty"])
        civ_ins.fill_game_pacing(self.game_data["game_pacing"])
        civ_ins.fill_hostile_entities(self.game_data["hostile_entities"])
        civ_ins.fill_ideology(self.game_data["ideology"])
        civ_ins.fill_minor_races(self.game_data["minor_races"])
        civ_ins.fill_nebulas(self.game_data["nebulas"])
        civ_ins.fill_number_of_sectors(self.game_data["number_of_sectors"])
        civ_ins.fill_planets_frequency(self.game_data["planets_frequency"])
        civ_ins.fill_relics(self.game_data["relics"])
        civ_ins.fill_research_rate(self.game_data["research_rate"])
        civ_ins.fill_resources(self.game_data["resources"])
        civ_ins.fill_star_frequency(self.game_data["star_frequency"])
        civ_ins.fill_starting_sector_size(self.game_data["starting_sector_size"])
        civ_ins.fill_victory_condition(self.game_data["victory_condition"])
        civ_ins.fill_race(self.game_data["race"])

        civ_ins.fill_game(self.play_data)

    def fill_query(self):
        return GalCivQuery(self.engine)


gd_loc = pathlib.Path("data") / "Galactic Civilization 4" / "game_data.json"
pd_loc = pathlib.Path("data") / "Galactic Civilization 4" / "play_data.json"

test = galcivdb(game_data_location=gd_loc, play_data_location=pd_loc)
query_machine = test.fill_query()

# query_machine.get_opponent_counts().groupby("Race").count().plot(kind="bar")
data = query_machine.get_result_values()

data.plot(x="Turns", y="Score", kind="scatter", figsize=(10, 5), logy=True)
plt.show()
