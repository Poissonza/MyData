import requests
from pyspark.sql import SparkSession
import datetime
import time

# Source:
# https://boardgamegeek.com/wiki/page/BGG_XML_API2


class BGGUserConstants:
    USER_DB = "boardgame.boardgamegeek.src__bgg_users"


class BGGPlayConstants:
    BGG_PLAY_DB = "boardgame.boardgamegeek.src__bgg__plays"


class BGGThingConstants:
    BGGTHINGTYPE = ["boardgame", "boardgameexpansion", "boardgameaccessory"]
    BGG_THING_DB = "boardgame.boardgamegeek.src__bgg__thing"


class BGGApi:

    def __init__(self):
        self._base_url = "https://boardgamegeek.com/xmlapi2/"
        self._spark = SparkSession.getActiveSession()


class BGGCollection(BGGApi):

    def __init__(self):
        super().__init__()
        self._url = self._base_url + "collection"

    def get_collection(self, user_name: str):

        usr_df = self._spark.read.table(BGGUserConstants.USER_DB)
        row = usr_df.select("id").where(f"user_name = '{user_name}'").collect()[0].id

        params = {"username": user_name}

        data = requests.get(self._url, params=params)
        while data.status_code != 200:
            print(data.status_code)
            time.sleep(2)
            data = requests.get(self._url, params=params)

        return data.text, int(row)


class BGGPlays(BGGApi):

    def __init__(self):
        super().__init__()
        self._url = self._base_url + "plays"

    def get_play_last_date(self, id: int):

        if self._spark.catalog.tableExists(BGGPlayConstants.BGG_PLAY_DB):
            df = self._spark.read.table(BGGPlayConstants.BGG_PLAY_DB)
            val = df.where(f"gameid = {id}").agg({"date": "max"}).collect()
            return val[0].asDict()["max(date)"]
        else:
            return None

    def get_plays_by_item(
        self,
        id: int,
        type: str = "thing",
        mindate: str = "1990-01-01",
        maxdate: str = (datetime.date.today() + datetime.timedelta(days=-1)).strftime(
            "%Y-%m-%d"
        ),
        page: int = 1,
    ):

        coll_date = self.get_play_last_date(id)
        if coll_date is not None:
            new_col_date = (coll_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            mindate = new_col_date
        if mindate != maxdate:
            params = {
                "id": id,
                "type": type,
                "mindate": mindate,
                "maxdate": maxdate,
                "page": page,
            }

            request_data = requests.get(self._url, params=params)
            final = request_data.text
        else:
            final = None
        return final


class BGGUsers(BGGApi):

    def __init__(self):
        super().__init__()
        self._url = self._base_url + "user"
        self._current_user_list = self.get_current_user_list()

    def get_current_user_list(self):
        if self._spark.catalog.tableExists(BGGUserConstants.USER_DB):

            sp_data = self._spark.read.table(BGGUserConstants.USER_DB)

            usr_list = [data[0] for data in sp_data.select("user_name").collect()]
            return usr_list
        else:
            return []

    def get_data(
        self, name: str, buddies: int = 1, guilds: int = 1, hot: int = 1, page: int = 1
    ):
        if name not in self._current_user_list:
            print(f"User {name} not found in the current user list")
            request_param = {"name": name}

            re_data = requests.get(self._url, params=request_param)

            return re_data.text
        else:
            return None


class BGGThing(BGGApi):

    def __init__(self):
        super().__init__()
        self._url = self._base_url + "thing"
        self._game_id_list = self.get_game_ids()

    def get_game_ids(self):
        if self._spark.catalog.tableExists(BGGThingConstants.BGG_THING_DB):
            sp_df = self._spark.read.table(BGGThingConstants.BGG_THING_DB)
            thing_id = [int(data[0]) for data in sp_df.select("id").collect()]
            return thing_id
        else:
            return []

    def get_data(self, id: int = None, type: str = None, page: int = 1):
        if id not in self._game_id_list:
            print("id is not in the list")
            request_param = {
                "page": page,
                "stats": 1,
                "versions": 1,
                "marketplace": 1,
                "comments": 1,
            }
            if id is not None:
                request_param.update({"id": str(id)})

            if type is not None:
                assert (
                    type in BGGThingConstants.BGGTHINGTYPE
                ), "Thing type must be one of the following: {}".format(
                    BGGThingConstants.BGGTHINGTYPE
                )
                request_param.update({"type": type})

            request_data = requests.get(self._url, params=request_param)

            return request_data.text
        else:
            return None
