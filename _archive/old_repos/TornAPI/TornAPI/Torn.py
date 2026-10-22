import requests as re
import datetime as dt


class TornAPI:

    def __init__(self, key: str, comment: str = "python"):
        self._header = {"accept": "application/json", "Authorization": f"ApiKey {key}"}
        self._params = {"comment": comment}

        self._comment = comment
        self._base_url = "https://api.torn.com/v2/"


class Faction(TornAPI):

    def __init__(self, key: str, comment: str = "python"):
        super().__init__(key, comment)
        self._url = self._base_url + "faction/"

    def get_attacks(
        self,
        filters: str = None,
        limit: int = 100,
        sort: str = None,
        to: int = None,
        ts_from: int = None,
        timestamp: int = None,
    ):
        url = self._url + "attacks"

        params = self._params

        if filters:
            assert filters in [
                "incoming",
                "outgoing",
            ], "Filter type is not one of the accepted values."
            params.update({"filters": filters})

        if limit:
            params.update({"limit": limit})

        if sort:
            assert sort in ["ASC", "DESC"], "Sort is not one of the accepted Variables."
            params.update({"sort": sort})

        if to:
            params.update({"to": to})

        if ts_from:
            params.update({"from": ts_from})

        if timestamp:
            params.update({"timestamp": timestamp})

        request = re.get(url, headers=self._header, params=params)

        return request.json()

    def get_balance(self, timestamp=None):
        url = self._url + "balance"

        params = self._params

        if timestamp:
            params = params.update({"timestamp": timestamp})

        if timestamp:
            url += f"?timestamp={timestamp}"
        request = re.get(url, headers=self._header, params=params)

        return request.json()

    def get_basic(self, timestamp=None):
        url = self._url + "basic"

        params = self._params

        if timestamp:
            params = params.update({"timestamp": timestamp})
        request = re.get(url, headers=self._header, params=params)

        return request.json()

    def get_chains(
        self,
        limit: int = 100,
        sort: str = "ASC",
        to: int = None,
        ts_from: int = None,
        timestamp: int = None,
    ):
        url = self._url + "chains"

        params = self._params
        params.update({"sort": sort})
        if to:
            params.update({"to": to})

        if ts_from:
            params.update({"from": ts_from})

        if timestamp:
            params.update({"timestamp": timestamp})

        request = re.get(url, headers=self._header, params=params)

        return request.json()

    def get_crimes(
        self,
        category: str = None,
        filters: str = None,
        offset: int = None,
        ts_from: int = None,
        ts_to: int = None,
        sort: str = None,
        timestamp: int = None,
    ):
        url = self._url + "crimes"

        request = re.get(url, headers=self._header, params=self._params)

        return request.json()

    def get_members(self):

        url = self._url + "members"

        request = re.get(url, headers=self._header, params=self._params)

        return request.json()

    def get_news_armoury_deposit(
        self,
        sort: str = "ASC",
        striptags: str = "true",
        to_ts: int = None,
        from_ts: int = None,
    ):
        params = self._params.copy()
        url = self._url + "news"

        if to_ts:
            params.update({"to": to_ts})

        if from_ts:
            params.update({"from": from_ts})

        assert sort in ["ASC", "DESC"], "Sort type is not in the accepted values."
        assert striptags in [
            "true",
            "false",
        ], "Striptags is not one of the accepted values."

        params.update({"cat": "armoryDeposit", "sort": sort, "striptags": striptags})

        data = re.get(url, headers=self._header, params=params)
        return data.json()

    def get_news_armoury_action(
        self,
        sort: str = "ASC",
        striptags: str = "true",
        ts_to: int = None,
        ts_from: int = None,
    ):
        params = self._params.copy()
        url = self._url + "news"

        if ts_to:
            params.update({"to": ts_to})

        if ts_from:
            params.update({"from": ts_from})

        assert sort in ["ASC", "DESC"], "Sort type is not in the accepted values."
        assert striptags in [
            "true",
            "false",
        ], "Striptags is not one of the accepted values."

        params.update({"cat": "armoryAction", "sort": sort, "striptags": striptags})

        data = re.get(url, headers=self._header, params=params)
        return data.json()


class User(TornAPI):

    def __init__(self, key: str, comment: str = "python"):
        super().__init__(key, comment)

        self._url = self._base_url + "user/"

    def get_base_user(self):
        data = re.get(self._url, headers=self._header, params=self._params)
        return data.json()

    def get_attacks(
        self,
        filters: str = None,
        limit: int = 100,
        sort: str = "ASC",
        to: int = None,
        ts_from: int = None,
        timestamp: int = None,
    ):
        params = self._params

        assert sort in ["ASC", "DESC"], "Sort type is not in the accepted values."
        params.update({"limit": limit, "sort": sort})

        if filters:
            assert filters in [
                "incoming",
                "outgoing",
            ], "Filter type is not one of the accepted values."
            params.update({"filters": filters})

        if to:
            params.update({"to": to})

        if ts_from:
            params.update({"from": ts_from})

        if timestamp:
            params.update({"timestamp": timestamp})

        data = re.get(self._url + "attacks", headers=self._header, params=self._params)
        return data.json()

    def get_basic(self, striptags: str = "true", timestamp: int = None):
        params = self._params

        assert striptags in [
            "true",
            "false",
        ], "Striptags is not one of the accepted values."
        params.update({"striptags": striptags})
        if timestamp:
            params.update({"timestamp": timestamp})

        data = re.get(self._url + "basic", headers=self._header, params=self._params)
        return data.json()

    def get_bounties(self, timestamp: int = None):

        params = self._params
        if timestamp:
            params.update({"timestamp": timestamp})

        data = re.get(self._url + "bounties", headers=self._header, params=self._params)

        return data.json()

    def get_battlestats(self, timestamp: int = None):
        params = self._params

        if timestamp:
            params.update({"timestamp": timestamp})

        data = re.get(self._url + "battlestats", headers=self._header, params=params)

        return data.json()

    def get_education(self, timestamp: int = None):
        params = self._params
        if timestamp:
            params.update({"timestamp": timestamp})

        data = re.get(self._url + "education", headers=self._header, params=params)

        return data.json()

    def get_enlisted_cars(self, timestamp: int = None):
        params = self._params
        if timestamp:
            params.update({"timestamp": timestamp})

        data = re.get(self._url + "enlistedcars", headers=self._header, params=params)

        return data.json()

    def get_hof(self, timestamp: int = None):

        params = self._params
        if timestamp:
            params.update({"timestamp": timestamp})

        data = re.get(self._url + "hof", headers=self._header, params=params)

        return data.json()

    def get_honors(self, timestamp: int = None):
        params = self._params
        if timestamp:
            params.update({"timestamp": timestamp})

        data = re.get(self._url + "honors", headers=self._header, params=params)

        return data.json()

    def get_job_points(self, timestamp: int = None):
        params = self._params

        if timestamp:
            params.update({"timestamp": timestamp})

        data = re.get(self._url + "jobpoints", headers=self._header, params=params)

        return data.json()
