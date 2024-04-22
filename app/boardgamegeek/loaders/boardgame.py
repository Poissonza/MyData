from app.boardgamegeek.objects import BoardGame
from app.boardgamegeek.util import XMLTools

def get_boardgame_from_xml(xml_file):
    xml_tools = XMLTools(xml_file)

    data = {
        "id": xml_file.attrib["id"],
        "name": xml_tools.fetch_element("name[@type='primary']", "value"),
        "type": xml_file.attrib["type"],
        "description": xml_tools.fetch_element("description").text,
        "year_published": xml_tools.fetch_element(
            "yearpublished", "value", int
        ),
        "min_players": xml_tools.fetch_element("minplayers", "value", int),
        "max_players": xml_tools.fetch_element("maxplayers", "value", int),
        "play_time": xml_tools.fetch_element("playingtime", "value", int),
        "min_play_time": xml_tools.fetch_element("minplaytime", "value", int),
        "max_play_time": xml_tools.fetch_element("maxplaytime", "value", int),
        "min_age": xml_tools.fetch_element("minage", "value", int),
        "boardgame_category": xml_tools.fetch_element_list(
            "link[@type='boardgamecategory']", "value"
        ),
        "boardgame_mechanic": xml_tools.fetch_element_list(
            "link[@type='boardgamemechanic']", "value"
        ),
        "boardgame_family": xml_tools.fetch_element_list(
            "link[@type='boardgamefamily']", "value"
        ),
        "designer": xml_tools.fetch_element_list(
            "link[@type='boardgamedesigner']", "value"
        )
    }

    return BoardGame(data)
