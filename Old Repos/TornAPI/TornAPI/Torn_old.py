import requests
from datetime import datetime as dt
import pandas as pd


class TornAPI:
    def __init__(self, key):
        self._header = {"accept": "application/json", "Authorization": f"ApiKey {key}"}
        self._base_url = "https://api.torn.com/v2/"

    def get_logcategories(self):
        url = self._base_url + "torn/logcategories"

        data = requests.get(url, headers=self._header)

        return data

    def get_items(self):
        url = self._base_url + "torn/items"

        data = requests.get(url, headers=self._header)

        return data


class User(TornAPI):
    def __init__(self, key):
        super().__init__(key)
        self._base_url = f"{self._base_url}user/"

    def get_user(self):
        print(self._header)
        data = requests.get(self._base_url, headers=self._header)

        return data.json()


class UserLog(User):
    def __init__(self, key):
        super().__init__(key)

    def get_full_log(self, input_date: dt):
        from_date = int(input_date.timestamp())
        to_date = int(from_date + (86400))

        data_for_day = {}
        finished = False

        while not finished:
            resp = requests.get(
                self._base_url,
                headers=self._header,
                params={"selections": "log", "from": from_date, "to": to_date},
            )
            print(resp.status_code)

            data = resp.json()["log"]
            if len(data) == 100:
                data_check = []
                for id in data:
                    data_check.append(data[id]["timestamp"])
                data_for_day.update(data)
                to_date = int(min(data_check))
            else:
                data_for_day.update(data)
                finished = True

        return data_for_day

    def get_bazaar_log(self, input_date: dt):
        from_date = input_date.timestamp()
        to_date = from_date + 86400

        data = requests.get(
            self._base_url,
            headers=self._header,
            params={"selections": "log", "cat": 87, "from": from_date, "to": to_date},
        )

        return data

    def get_travel_log(self, input_date: dt):
        from_date = input_date.timestamp()
        to_date = from_date + 86400

        data = requests.get(
            self._base_url,
            headers=self._header,
            params={"selections": "log", "cat": 87, "from": from_date, "to": to_date},
        )

        return data

    def get_bazaar_log(self):
        data = requests.get(
            self._base_url,
            headers=self._header,
            params={"selections": "log", "cat": 18},
        )

        return data

    def get_item_market_log(self, input_date: dt):
        from_date = input_date.timestamp()
        to_date = from_date + 86400
        data = requests.get(
            self._base_url,
            headers=self._header,
            params={"selections": "log", "cat": 11, "from": from_date, "to": to_date},
        )

        return data


class Faction(TornAPI):
    def __init__(self, key):
        super().__init__(key)
        self._base_url = f"{self._base_url}faction/"

    def get_attacks(self, input_date: dt):
        url = self._base_url + "attacks"

        from_date = int(input_date.timestamp())
        to_date = int(from_date + (86400))

        data_for_day = {}
        finished = False

        while not finished:
            resp = requests.get(
                url,
                headers=self._header,
                params={"selections": "log", "from": from_date, "to": to_date},
            )

            data = resp.json()["attacks"]
            if len(data) == 100:
                data_check = []

                for attack in data:
                    data_check.append(attack["started"])
                    data_for_day.update({attack["id"]: attack})

                to_date = int(min(data_check))
            else:
                for attack in data:
                    data_for_day.update({attack["id"]: attack})
                finished = True

        return data_for_day
