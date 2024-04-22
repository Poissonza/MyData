import requests
import xml.etree.ElementTree as ET


class API:

    def __init__(self):
        self._api_endpoint = "https://boardgamegeek.com/xmlapi2/"
        self._url = None

    def get_xml(self, params=None):
        try:
            data = requests.get(self._url, params=params).text
        except Exception as e:
            raise e
        return data


class ThingAPI(API):

    def __init__(self):
        super().__init__()

        self._url = self._api_endpoint + "thing"

class UserApi(API):

    def __init__(self):
        super().__init__()

        self._url = self._api_endpoint + "user"


class PlaysApi(API):

    def __init__(self):
        super().__init__()

        self._url = self._api_endpoint + "plays"