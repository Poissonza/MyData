from .database import DataBaseConnection
import pandas as pd


class GameData:

    def __init__(
        self, username: str, password: str, host: str, database: str, schema: str
    ):
        self._db_connection = DataBaseConnection(
            username=username,
            password=password,
            host=host,
            database=database,
            schema=schema,
        )
        self._game_dict = self.get_game_dict()

    def get_game_dict(self) -> dict:
        data = pd.DataFrame(self._db_connection.fetch_data("game"))
        game_dict = dict(zip(data["name"], data["id"]))

        return game_dict
