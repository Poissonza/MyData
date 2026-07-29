import requests


class API:
    def __init__(self, base_url: str, params: dict | None = None, header: dict | None = None) -> None:
        self._base_url = base_url
        self._params = params or {}
        self._header = header or {}

    def get(self, path: str, params: dict | None = None) -> requests.Response:
        url = self._base_url + path
        merged = {**self._params, **(params or {})}
        response = requests.get(url, headers=self._header, params=merged)
        response.raise_for_status()
        return response

    def get_json(self, path: str, params: dict | None = None) -> dict:
        return self.get(path, params).json()

    def get_text(self, path: str, params: dict | None = None) -> str:
        return self.get(path, params).text
