import os
from sqlalchemy import create_engine, MetaData, Table, select, exc


class DBConnector:
    def __init__(self):
        self.dbuser = os.getenv("db_user")
        self.dbpass = os.getenv("db_pass")
        self.db_local = os.getenv("db_databaseserver")
        self.schema = os.getenv("db_database")

        self.engine = create_engine(
            f"postgresql://{self.dbuser}:{self.dbpass}@{self.db_local}:5432/{self.schema}",
            echo=False,
        )

        self.meta_data = MetaData()
        self.get_tables()

    def get_tables(self):
        self.players = Table(
            "player", self.meta_data, autoload_with=self.engine, schema="bgg"
        )
        self.collection = Table(
            "collection", self.meta_data, autoload_with=self.engine, schema="bgg"
        )
        self.games = Table(
            "games", self.meta_data, autoload_with=self.engine, schema="bgg"
        )
        print("Tables fetched")

    def check_games(self):
        con = self.engine.connect()
        sel = select(self.games.c.id)
        results = con.execute(sel).fetchall()
        return results

    def insert_game(self, data):
        con = self.engine.connect()
        ins = self.games.insert()
        try:
            con.execute(ins, data)
        except exc.IntegrityError:
            print("Found a duplicate")
        con.commit()
        con.close()

    def insert_collection(self, data):
        con = self.engine.connect()
        ins = self.collection.insert()
        con.execute(ins, data)

        con.commit()
        con.close()

    def insert_player(self, data):
        con = self.engine.connect()
        ins = self.players.insert()
        sel = select(self.players)
        con.execute(ins, data)
        con.commit()
        con.close()

    def check_player(self, player_name):
        sel = select(self.players.c.id).where(self.players.c.username == player_name)
        con = self.engine.connect()
        results = con.execute(sel).fetchone()
        return results is None

    def get_players(self):
        sel = select(self.players.c.id, self.players.c.username)
        con = self.engine.connect()

        res = con.execute(sel).fetchall()

        return res
