import requests

class API:
    def __init__(self, base_url: str, params: dict = None, header: dict = None) -> None:
        self._base_url = base_url
        self._params = params
        self._header = header

    def get(self, path: str, params: dict = None) -> requests.Response:
        url = self._base_url + path
        merged = {**self._params, **(params or {})}
        return requests.get(url, headers=self._header, params=merged)

    def get_json(self, path: str, params: dict = None) -> dict:
        return self.get(path, params).json()

