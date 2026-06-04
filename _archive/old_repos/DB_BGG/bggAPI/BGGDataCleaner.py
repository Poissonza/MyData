import xml.etree.ElementTree as ET
import pathlib
import json
from pyspark.sql import SparkSession
import datetime as dt


class BGGThingConstants:
    BGG_ATTRIBUTES_LIST = [
        "category",
        "mechanic",
        "family",
        "artist",
        "publisher",
        "expansion",
        "designer",
    ]

    BGG_ATTRIBUTES_DB = "boardgame.boardgamegeek.src__bgg__boardgame_{}"
    BGG_ATTRIBUTES_LINK_DB = "boardgame.boardgamegeek.src__bgg__boardgame_{}"


class BGGCollectionCleaner:

    def __init__(self, xml_string):
        self._xml_string = xml_string

    def clean_collection(self, user_id):
        xml_data = ET.fromstring(self._xml_string)
        final_data = []

        for item in xml_data.findall("item"):
            item_dict = {
                "id": int(item.attrib["collid"]),
                "thingid": int(item.attrib["objectid"]),
                "objecttype": item.attrib["objecttype"],
                "subtype": item.attrib["subtype"],
                "name": item.find("name").text,
                "own": item.find("status").attrib["own"],
                "prevowned": item.find("status").attrib["prevowned"],
                "fortrade": item.find("status").attrib["fortrade"],
                "want": item.find("status").attrib["want"],
                "wanttoplay": item.find("status").attrib["wanttoplay"],
                "wanttobuy": item.find("status").attrib["wanttobuy"],
                "wishlist": item.find("status").attrib["wishlist"],
                "preordered": item.find("status").attrib["preordered"],
                "numplays": int(item.find("numplays").text),
                "user_id": user_id,
            }

            if item.find("yearpublished") is not None:
                item_dict.update(
                    {
                        "yearpublished": item.find("yearpublished").text,
                    }
                )
            final_data.append(item_dict)
        return final_data


class BGGUserCleaner:

    def __init__(self, xml_string: str):
        self._xml_string = xml_string

    def clean_user(self):
        user_list = []
        xml_data = ET.fromstring(self._xml_string)

        user_dict = {
            "id": xml_data.attrib["id"],
            "user_name": xml_data.attrib["name"],
            "first_name": xml_data.find("firstname").attrib["value"],
            "last_name": xml_data.find("lastname").attrib["value"],
            "year_registered": int(xml_data.find("yearregistered").attrib["value"]),
            "last_login": xml_data.find("lastlogin").attrib["value"],
            "country": xml_data.find("country").attrib["value"],
        }
        return user_dict


class BGGDataCleaner:

    def __init__(self, xml_string):
        self._xml_string = xml_string
        self._spark = SparkSession.getActiveSession()
        self._attribute_ids = self.get_attribute_ids()

    def get_attribute_ids(self):
        attribute_ids = {}
        for attribute in BGGThingConstants.BGG_ATTRIBUTES_LIST:
            if self._spark.catalog.tableExists(
                BGGThingConstants.BGG_ATTRIBUTES_DB.format(attribute)
            ):
                try:
                    att_df = self._spark.read.table(
                        BGGThingConstants.BGG_ATTRIBUTES_DB.format(attribute)
                    )
                except Exception as e:
                    attribute_ids.update({attribute: []})
                    break
                att_id = [data[0] for data in att_df.select("id").collect()]

                attribute_ids.update({attribute: att_id})
            else:
                attribute_ids.update({attribute: []})
        return attribute_ids

    def multiple_clean(self):
        xml_data = ET.fromstring(self._xml_string)
        final = []
        att_data = []
        att_link = []
        mp_data = []
        for item in xml_data:
            thing_data, att_data, alt_name, version_data, poll_dict, mp_data = (
                self.clean_thing(item)
            )
            final.append(thing_data)
        return final, att_data, alt_name, version_data, poll_dict, mp_data

    def clean_thing(self, xml_data):
        fin_att_data = {}
        fin_att_link = {}
        fin_alternative_names = []
        fin_version_data = {}
        fin_market_place_data = []
        poll_dict = {}
        game_data = {
            "id": int(xml_data.attrib["id"]),
            "name": xml_data.find("name[@type='primary']").attrib["value"],
            "yearpublished": int(xml_data.find("yearpublished").attrib["value"]),
            "minplayers": int(xml_data.find("minplayers").attrib["value"]),
            "maxplayers": int(xml_data.find("maxplayers").attrib["value"]),
            "playingtime": int(xml_data.find("playingtime").attrib["value"]),
            "minplaytime": int(xml_data.find("minplaytime").attrib["value"]),
            "maxplaytime": int(xml_data.find("maxplaytime").attrib["value"]),
            "minage": int(xml_data.find("minage").attrib["value"]),
            "rating": float(
                xml_data.find("statistics")
                .find("ratings")
                .find("average")
                .attrib["value"]
            ),
            "weight": float(
                xml_data.find("statistics")
                .find("ratings")
                .find("averageweight")
                .attrib["value"]
            ),
            "owned": int(
                xml_data.find("statistics")
                .find("ratings")
                .find("owned")
                .attrib["value"]
            ),
            "trading": int(
                xml_data.find("statistics")
                .find("ratings")
                .find("trading")
                .attrib["value"]
            ),
            "wanting": int(
                xml_data.find("statistics")
                .find("ratings")
                .find("wanting")
                .attrib["value"]
            ),
            "wishing": int(
                xml_data.find("statistics")
                .find("ratings")
                .find("wishing")
                .attrib["value"]
            ),
            "numcomments": int(
                xml_data.find("statistics")
                .find("ratings")
                .find("numcomments")
                .attrib["value"]
            ),
            "numweights": int(
                xml_data.find("statistics")
                .find("ratings")
                .find("numweights")
                .attrib["value"]
            ),
        }
        meta_data = {}

        for attribute in BGGThingConstants.BGG_ATTRIBUTES_LIST:

            attribute_data = xml_data.findall(f"link[@type='boardgame{attribute}']")
            if len(attribute_data) > 0:

                att_data, att_link = self.get_boardgame_attribute(
                    xml_data.findall(f"link[@type='boardgame{attribute}']"),
                    xml_data.attrib["id"],
                    attribute,
                )
                if len(att_data) > 0:
                    fin_att_data.update({attribute: att_data})
                if len(att_link) > 0:
                    fin_att_link.update({attribute: att_link})

        alternative_name_data = xml_data.findall(f"name[@type='alternate']")

        if len(alternative_name_data) > 0:
            fin_alternative_names = self.get_boardgame_alternative_name(
                alternative_name_data, xml_data.attrib["id"]
            )

        poll_data = xml_data.findall("poll")

        if len(poll_data) > 0:
            poll_dict = self.get_poll_details(poll_data, xml_data.attrib["id"])

        version_data = xml_data.find("versions")

        if version_data is not None:
            v = self.get_version_details(version_data, xml_data.attrib["id"])

            fin_version_data.update(v)

        final_data = {"game_data": game_data, "meta_data": meta_data}
        attribute_data = {"attribute": fin_att_data, "link": fin_att_link}

        market_place_data = xml_data.findall("marketplacelistings")
        if len(market_place_data) > 0:
            for listing in market_place_data[0].findall("listing"):
                mp_dict = {
                    "thing_id": int(xml_data.attrib["id"]),
                    "list_date": listing.find("listdate").attrib["value"],
                    "currency": listing.find("price").attrib["currency"],
                    "price": float(listing.find("price").attrib["value"]),
                    "condition": listing.find("condition").attrib["value"],
                    "notes": listing.find("notes").attrib["value"],
                }

                fin_market_place_data.append(mp_dict)

        return (
            game_data,
            attribute_data,
            fin_alternative_names,
            fin_version_data,
            poll_dict,
            fin_market_place_data,
        )

    def get_poll_details(self, data, game_id: str):
        language_dependence_list = []
        player_age_list = []
        num_players_list = []
        for poll in data:

            if poll.attrib["name"] == "suggested_numplayers":
                for result in poll.findall("results"):
                    poll_dict = {
                        "game_id": game_id,
                        "numplayers": result.attrib["numplayers"],
                        "best": int(
                            result.find("result[@value='Best']").attrib["numvotes"]
                        ),
                        "recommended": int(
                            result.find("result[@value='Recommended']").attrib[
                                "numvotes"
                            ]
                        ),
                        "not_recommended": int(
                            result.find("result[@value='Not Recommended']").attrib[
                                "numvotes"
                            ]
                        ),
                    }

                    num_players_list.append(poll_dict)
            elif poll.attrib["name"] == "suggested_playerage":
                for result in poll.find("results").findall("result"):
                    poll_pa_dict = {
                        "game_id": game_id,
                        "number_of_players": result.attrib["value"],
                        "number_of_votes": result.attrib["numvotes"],
                    }
                    player_age_list.append(poll_pa_dict)
            elif poll.attrib["name"] == "language_dependence":
                for result in poll.find("results").findall("result"):
                    lan_dep_dict = {
                        "game_id": game_id,
                        "level": result.attrib["level"],
                        "description": result.attrib["value"],
                        "number_of_votes": result.attrib["numvotes"],
                    }
                    language_dependence_list.append(lan_dep_dict)
            else:
                raise ValueError(f"The Poll {poll.attrib['name']} is not supported yet")

        return {
            "num_players": num_players_list,
            "age": player_age_list,
            "language": language_dependence_list,
        }

    def get_boardgame_alternative_name(self, data, game_id):
        alt_name_data = []
        for name in data:
            alt_name_data.append(
                {
                    "id": game_id,
                    "name": name.attrib["value"],
                }
            )
        return alt_name_data

    def get_boardgame_attribute(self, data, game_id, attribute_name):
        attribute_data = []
        attribute_link = []
        for attribute in data:
            if attribute.attrib["id"] not in self._attribute_ids[attribute_name]:
                attribute_data.append(
                    {
                        "id": attribute.attrib["id"],
                        "name": attribute.attrib["value"],
                    }
                )
                self._attribute_ids[attribute_name].append(attribute.attrib["id"])

            attribute_link.append(
                {f"{attribute_name}_id": attribute.attrib["id"], "game_id": game_id}
            )

        return attribute_data, attribute_link

    def get_version_details(self, data, game_id: str):
        board_game_version_link = []
        version_data = []
        board_game_publisher_link = []
        board_game_language_link = []
        for item in data.findall("item"):
            version_id = item.attrib["id"]

            version_dict = {
                "game_id": game_id,
                "version_id": version_id,
                "type": item.attrib["type"],
                "yearpublished": item.find("yearpublished").attrib["value"],
                "name": item.find("name[@type='primary']").attrib["value"],
                "width": item.find("width").attrib["value"],
                "length": item.find("length").attrib["value"],
                "depth": item.find("depth").attrib["value"],
                "weight": item.find("weight").attrib["value"],
                "productcode": item.find("productcode").attrib["value"],
            }
            version_data.append(version_dict)

            for link in item.findall("link"):
                if link.attrib["type"] == "boardgameversion":
                    link_dict = {
                        "game_id": game_id,
                        "version_id": version_id,
                        "id": link.attrib["id"],
                        "value": link.attrib["value"],
                        "inbound": link.attrib["inbound"],
                    }
                    board_game_version_link.append(link_dict)
                elif link.attrib["type"] == "boardgamepublisher":
                    link_dict = {
                        "game_id": game_id,
                        "version_id": version_id,
                        "id": link.attrib["id"],
                        "value": link.attrib["value"],
                    }
                    board_game_publisher_link.append(link_dict)
                elif link.attrib["type"] == "language":
                    link_dict = {
                        "game_id": game_id,
                        "version_id": version_id,
                        "id": link.attrib["id"],
                        "value": link.attrib["value"],
                    }
                    board_game_language_link.append(link_dict)

        final_version = {
            "version": version_data,
            "bg_version": board_game_version_link,
            "bg_publisher": board_game_publisher_link,
            "language": board_game_language_link,
        }
        return final_version


class BGGPlaysCleaner:

    def __init__(self, xml_string):
        self._xml_string = xml_string
        self._spark = SparkSession.getActiveSession()

    def get_number_of_plays(self):
        xml_data = ET.fromstring(self._xml_string)
        return int(xml_data.attrib["total"])

    def clean_plays(self):
        xml_data = ET.fromstring(self._xml_string)
        final_play_list = []
        final_players = []

        for play in xml_data.findall("play"):
            play_id = play.attrib["id"]
            play_dict = {
                "play_id": play_id,
                "userid": play.attrib["userid"],
                "date": dt.datetime.strptime(play.attrib["date"], "%Y-%m-%d"),
                "quantity": play.attrib["quantity"],
                "length": play.attrib["length"],
                "incomplete": play.attrib["incomplete"],
                "nowinstats": play.attrib["nowinstats"],
                "location": play.attrib["location"],
                "gameid": play.find("item").attrib["objectid"],
            }

            if play.find("comments") is not None:
                play_dict.update({"comments": play.find("comments").text})
            else:
                play_dict.update({"comments": None})

            if play.find("players") is not None:
                player_data = play.find("players").findall("player")
                for player in player_data:
                    player_dict = player.attrib
                    player_dict.update({"play_id": play_id})
                    final_players.append(player_dict)

            final_play_list.append(play_dict)
        return final_play_list, final_players
