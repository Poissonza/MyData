from sqlalchemy import MetaData, Table


class GalCivSupernovaInsertion:
    def __init__(self, engine):
        self.engine = engine
        self.get_tables()

    def get_tables(self):
        meta = MetaData()
        table_names = [
            "galaxy_difficulty",
            "game_pacing",
            "research_rate",
            "minor_races",
            "hostile_entities",
            "galaxy_size",
            "number_of_sectors",
            "civilization_proximity",
            "habitable_planets",
            "extreme_planets",
            "resources",
            "victory_condition",
            "version",
            "race",
        ]
        self.table_dict = {}
        [
            self.table_dict.update(
                {table_name: Table(table_name, meta, autoload_with=self.engine)}
            )
            for table_name in table_names
        ]
