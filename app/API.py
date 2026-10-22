import requests


class API:

    def __init__(self, base_address: str, params: dict = None, header: dict = None):
        self._base_address = base_address
        self._params = params or {}
        self._header = header

    def get(self, path: str, params: dict = None) -> requests.Response:
        url = self._base_address + path
        merged = {**self._params, **(params or {})}
        return requests.get(
            url, headers=self._header, params=merged if merged else None
        )

    def get_json(self, path: str, params: dict = None) -> dict:
        return self.get(path, params).json()
