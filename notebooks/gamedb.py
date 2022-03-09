from sqlalchemy import create_engine, Table, Column, MetaData, Integer, String, Date, select, func, ForeignKey, Float


class GameDB:
    def __init__(self, db=None, create_tables=False):
        self.engine = create_engine(f"sqlite:///{db}.db", echo=False)
        self.meta_data = MetaData()
        if create_tables:
            self.create_tables()

        self.plays = Table("plays", self.meta_data, autoload_with=self.engine)
        self.playsplayer = Table("playsplayer", self.meta_data, autoload_with=self.engine)
        self.games = Table("games", self.meta_data, autoload_with=self.engine)
        self.classificationlink = Table("classificationgamelink", self.meta_data, autoload_with=self.engine)
        self.classification = Table("classifications", self.meta_data, autoload_with=self.engine)

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
            Column("id", Integer, primary_key=True),
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

        game = Table(
            "games",
            self.meta_data,
            Column("id", Integer, primary_key=True),
            Column("name", String),
            Column("yearpublished", Integer),
            Column("minplayers", Integer),
            Column("maxplayers", Integer),
            Column("playingtime", Integer),
            Column("minplaytime", Integer),
            Column("maxplaytime", Integer),
            Column("minage", Integer),
            Column("usersrated", Integer),
            Column("average", Float),
            Column("bayesaverage", Float),
            Column("stddev", Float),
            Column("median", Float),
            Column("owned", Integer),
            Column("trading", Integer),
            Column("wanting", Integer),
            Column("wishing", Integer),
            Column("numcomments", Integer),
            Column("numweights", Integer),
            Column("averageweight", Float),
            Column("description", String)
        )

        classifications = Table(
            "classifications",
            self.meta_data,
            Column("internalId", Integer, primary_key=True),
            Column("id", Integer),
            Column("type", String),
            Column("value", String)
        )

        classificationgamelink = Table(
            "classificationgamelink",
            self.meta_data,
            Column("id", Integer, primary_key=True),
            Column("gameid", Integer),
            Column("classificationid", Integer)
        )

        self.meta_data.create_all(self.engine)

    def insert_play(self, data):
        ins = self.plays.insert()
        self.engine.execute(ins, data)

    def insert_classification_link(self, data):
        ins = self.classificationlink.insert()
        self.engine.execute(ins, data)

    def insert_classification(self, data):
        ins = self.classification.insert()
        self.engine.execute(ins, data)

    def get_classification_id(self):
        s = select(self.classification.c.id)
        return [item for t in self.engine.execute(s).fetchall() for item in t]

    def get_play_id(self, gameid):
        s = select(self.plays.c.playid).where(self.plays.c.gameid == gameid)
        return [item for t in self.engine.execute(s).fetchall() for item in t]

    def get_last_date(self, gameid):
        s = select(func.max(self.plays.c.date)).where(self.plays.c.gameid == gameid)
        return self.engine.execute(s).fetchone()

    def insert_player_play(self, data):
        ins = self.playsplayer.insert()
        self.engine.execute(ins, data)

    def insert_game(self, data):
        ins = self.games.insert()
        self.engine.execute(ins, data)

    def get_game_id(self):
        s = select(self.games.c.id)
        return [item for t in self.engine.execute(s).fetchall() for item in t]
