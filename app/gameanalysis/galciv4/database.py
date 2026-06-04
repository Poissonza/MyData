import pathlib
import json

from sqlalchemy import create_engine

from app.config import Config
from app.gameanalysis.galciv4.table_insertions import GalCivInsertion
from app.gameanalysis.galciv4.table_queries import GalCivQuery


class GalCivDatabase:

    def __init__(self, db_name: str = "galciv4"):
        self.engine = create_engine(Config.db_url(db_name), echo=False)

    def load(
        self,
        game_data_path: pathlib.Path,
        play_data_path: pathlib.Path,
    ) -> None:
        game_data = json.loads(game_data_path.read_text())
        play_data = json.loads(play_data_path.read_text())

        ins = GalCivInsertion(self.engine)
        ins.fill_version(game_data["version"])
        ins.fill_anomolies(game_data["anomolies"])
        ins.fill_abilities(game_data["abilities"])
        ins.fill_ascension_crystal(game_data["ascension_crystals"])
        ins.fill_asteroid(game_data["asteroid"])
        ins.fill_biology(game_data["biology"])
        ins.fill_black_hole(game_data["black_holes"])
        ins.fill_civilization_proximity(game_data["civilization_proximity"])
        ins.fill_galaxy_difficulty(game_data["galaxy_difficulty"])
        ins.fill_game_pacing(game_data["game_pacing"])
        ins.fill_hostile_entities(game_data["hostile_entities"])
        ins.fill_ideology(game_data["ideology"])
        ins.fill_minor_races(game_data["minor_races"])
        ins.fill_nebulas(game_data["nebulas"])
        ins.fill_number_of_sectors(game_data["number_of_sectors"])
        ins.fill_planets_frequency(game_data["planets_frequency"])
        ins.fill_relics(game_data["relics"])
        ins.fill_research_rate(game_data["research_rate"])
        ins.fill_resources(game_data["resources"])
        ins.fill_star_frequency(game_data["star_frequency"])
        ins.fill_starting_sector_size(game_data["starting_sector_size"])
        ins.fill_victory_condition(game_data["victory_condition"])
        ins.fill_race(game_data["race"])
        ins.fill_game(play_data)

    def query(self) -> GalCivQuery:
        return GalCivQuery(self.engine)
