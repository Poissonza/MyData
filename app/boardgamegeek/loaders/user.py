from boardgamegeek.util import XMLTools
from app.boardgamegeek.objects import User


def create_user_from_xml(xml_file):
    xml_tools = XMLTools(xml_file)

    data = {
        "id": xml_file.attrib["id"],
        "user_name": xml_file.attrib["name"],
        "first_name": xml_tools.fetch_element("firstname", "value"),
        "last_name": xml_tools.fetch_element("lastname", "value"),
        "avatar_link": xml_tools.fetch_element("avatarlink", "value"),
        "year_registered": xml_tools.fetch_element("yearregistered", "value", int),
        "last_login": xml_tools.fetch_element("lastlogin", "value"),
        "state_or_province": xml_tools.fetch_element("stateorprovince", "value"),
        "country": xml_tools.fetch_element("country", "value"),
        "trade_rating": xml_tools.fetch_element("traderating", "value", int),
    }

    return User(data)
