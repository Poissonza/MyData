import xml.etree.ElementTree as ET

from app.api import API


class BGGAPI(API):

    def __init__(self):
        super().__init__(base_address="https://boardgamegeek.com/xmlapi2/")

    def get_xml(self, path: str, params: dict = None) -> ET.Element:
        return ET.fromstring(self.get(path, params).text)


class ThingAPI(BGGAPI):

    def get_xml(self, params: dict = None) -> ET.Element:
        return super().get_xml("thing", params)


class UserApi(BGGAPI):

    def get_xml(self, params: dict = None) -> ET.Element:
        return super().get_xml("user", params)


class PlaysApi(BGGAPI):

    def get_xml(self, params: dict = None) -> ET.Element:
        return super().get_xml("plays", params)
