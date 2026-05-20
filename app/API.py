import requests as re

class API:

    def __init__(self, base_address: str, params: dict =None, header:dict = None, **kwargs):
        self._base_address = base_address
        self._params = params
        self._header = header
        self._kwargs = kwargs

    def get_data(self, table:str, params:dict = None):
        url = self._base_address + table
        if not params:
            params = self._params.copy()

        request = re.get(url, headers=self._header, params=params)

        return request.json()

class TornAPI(API):
    def __init__(self, key:str, params: dict = None, **kwargs):
        header = {"accept": "application/json", "Authorization": f"ApiKey {key}"}
        base_address = "https://api.torn.com/v2/"
        params = {}

        if kwargs:
            if "comment" in kwargs:
                params.update({"comment": kwargs["comment"]})

        super().__init__(base_address, params, header, **kwargs)

    def get_torn_data(self, table:str, **kwargs):

        params = self._params.copy()

        if kwargs:
            if "filters" in kwargs:
                assert kwargs["filters"] in [
                    "incoming",
                    "outgoing",
                ], "Filter type is not one of the accepted values."

            if "sort" in kwargs:
                assert kwargs["sort"] in [
                    "ASC",
                    "DESC",
                ], "Sort type is not one of the accepted values."

            if "striptags" in kwargs:
                assert kwargs["striptags"] in [
                    "true",
                    "false",
                ], "Striptags is not one of the accepted values."

            params.update(kwargs)


        data = self.get_data(table, params)

        return data

