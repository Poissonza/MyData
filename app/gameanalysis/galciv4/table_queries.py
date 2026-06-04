from sqlalchemy import MetaData, Table, select
import pandas as pd


class GalCivQuery:

    def __init__(self, engine):
        self.engine = engine
        self.fetch_tables()

    def fetch_tables(self):
        meta = MetaData()
        self.result_table = Table("result", meta, autoload_with=self.engine)
        self.game_table = Table("game", meta, autoload_with=self.engine)
        self.race_table = Table("race", meta, autoload_with=self.engine)
        self.opponent_link_table = Table(
            "opponent_link", meta, autoload_with=self.engine
        )
        self.biology_table = Table("biology", meta, autoload_with=self.engine)

    def get_opponent_counts(self):
        s = select(self.race_table.c.race, self.opponent_link_table.c.game).join(
            self.race_table
        )
        return pd.DataFrame(self.engine.execute(s).fetchall(), columns=["Race", "Game"])

    def get_biology_of_races(self):
        s = select(self.race_table.c.race, self.biology_table.c.biology).join(
            self.race_table
        )
        return pd.DataFrame(self.engine.execute(s).fetchall(), columns=["race", "bio"])

    def get_result_values(self):
        s = select(self.result_table.c.turns, self.result_table.c.score)
        return pd.DataFrame(
            self.engine.execute(s).fetchall(), columns=["Turns", "Score"]
        )
