import pandas as pd
from sqlalchemy import URL, create_engine, MetaData, Table, select

from app.config import Config


class PCGamingDatabase:
    TABLE_LIST = ["collection", "games", "player"]

    def __init__(self, schema: str = "pcgaming"):
        url = URL.create(
            "postgresql",
            username=Config.DB_USER,
            password=Config.DB_PASSWORD,
            host=Config.DB_HOST,
            port=int(Config.DB_PORT),
            database=Config.DB_NAME,
        )
        self._engine = create_engine(url)
        self._tables = self._load_tables(schema)

    def _load_tables(self, schema: str) -> dict:
        meta = MetaData()
        return {
            t: Table(t, meta, autoload_with=self._engine, schema=schema)
            for t in self.TABLE_LIST
        }

    def fetch(self, table: str, single: bool = False):
        sel = select(self._tables[table])
        with self._engine.connect() as conn:
            result = conn.execute(sel)
            return result.fetchone() if single else result.fetchall()

    def insert(self, table: str, data: dict) -> None:
        with self._engine.connect() as conn:
            conn.execute(self._tables[table].insert(), data)
            conn.commit()


class GameData:

    def __init__(self):
        self._db = PCGamingDatabase()
        self._game_dict = self._get_game_dict()

    def _get_game_dict(self) -> dict:
        data = pd.DataFrame(self._db.fetch("games"))
        return dict(zip(data["name"], data["id"]))

    @property
    def game_dict(self) -> dict:
        return self._game_dict
