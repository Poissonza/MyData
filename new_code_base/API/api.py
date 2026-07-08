import requests
from datetime import datetime as dt
import json

class API:
    def __init__(self, base_url: str, params: dict = None, header: dict = None) -> None:
        self._base_url = base_url
        self._params = params or {}
        self._header = header

    def get(self, path: str, params: dict = None) -> requests.Response:
        url = self._base_url + path
        merged = {**self._params, **(params or {})}
        try:
            response = requests.get(url, headers=self._header, params=merged)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise e

    def get_json(self, path: str, params: dict = None) -> dict:
        return self.get(path, params).json()


    def store_request(self, path: str, folder_path: str, params: dict = None) -> None:
        data = self.get_json(path, params)

        with open(folder_path + f"{path}_" + dt.today().strftime("%Y-%m-%d_%H-%M-%S") + ".json", "w") as f:
            json.dump(data, f)
