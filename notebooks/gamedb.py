from sqlalchemy import create_engine, Table, Column, MetaData, Integer, String, Date, select, func, ForeignKey


class GameDB:
    def __init__(self, db=None, create_tables=False):
        self.engine = create_engine(f"sqlite:///{db}.db", echo=False)
        self.meta_data = MetaData()
        if create_tables:
            self.create_tables()

        self.plays = Table("plays", self.meta_data, autoload_with=self.engine)
        self.playsplayer = Table("playsplayer", self.meta_data, autoload_with=self.engine)

    def create_tables(self):
        plays = Table(
            "plays",
            self.meta_data,
            Column("playid", Integer, primary_key=True),
            Column("userid", Integer),
            Column("date", String),
            Column("quantity", Integer),
            Column("length", Integer),
            Column("location", String),
            Column("game", String),
            Column("gameid", Integer),
            Column("comments", String),
        )

        playsplayer = Table(
            "playsplayer",
            self.meta_data,
            Column("id", Integer,primary_key=True),
            Column("playid", Integer, ForeignKey("plays.playid")),
            Column("username", String),
            Column("userid", Integer),
            Column("name", String),
            Column("startposition", String),
            Column("color", String),
            Column("score", Integer),
            Column("new", Integer),
            Column("rating", Integer),
            Column("win", Integer)
        )

        self.meta_data.create_all(self.engine)

    def insert_play(self, data):
        ins = self.plays.insert()
        self.engine.execute(ins, data)

    def get_play_id(self, gameid):
        s = select(self.plays.c.playid).where(self.plays.c.gameid == gameid)
        return [item for t in self.engine.execute(s).fetchall() for item in t]

    def get_last_date(self, gameid):
        s = select(func.max(self.plays.c.date)).where(self.plays.c.gameid == gameid)
        return self.engine.execute(s).fetchone()

    def insert_player_play(self, data):
        ins = self.playsplayer.insert()
        self.engine.execute(ins, data)
