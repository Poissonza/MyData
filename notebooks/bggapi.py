import pathlib
import urllib
from bs4 import BeautifulSoup
import math
from tqdm import tqdm
from time import sleep
import json


class BGGAPI:
    def populate_game_info(self, game_id: int):
        final_dict = {"bggId": game_id}

        game_url = f"https://boardgamegeek.com/xmlapi2/thing?id={game_id}&stats=1"
        url_data = urllib.request.urlopen(game_url).read()

        soup = BeautifulSoup(url_data, "html.parser")

        final_dict.update(
            {
                "weight": float(soup.items.find("averageweight")["value"]),
                "rating": float(soup.ratings.average["value"]),
                "bayesrating": float(soup.ratings.bayesaverage["value"]),
            }
        )
        return final_dict

    def get_plays(selfs, game_id: int, cache_location: pathlib.Path):

        data_export = cache_location / "data_export.json"
        id_collected_file = cache_location / "id_collected.json"
        last_date_file = cache_location / "last_date.json"

        if id_collected_file.is_file():
            with id_collected_file.open as file:
                id_collected_json = json.load(file)
            id_collected = id_collected_json[game_id]
        else:
            id_collected_json = {}
            id_collected = []

        if last_date_file.is_file():
            with last_date_file.open() as file:
                last_date = json.load(file)
        else:
            last_date = {}

        if not game_id in last_date:
            last_date.update({game_id:"0000-00-00"})

        if data_export.is_file():
            with data_export.open() as file:
                final_data = json.load(file)
        else:
            final_data = []

        play_url = f"https://boardgamegeek.com/xmlapi2/plays?id={game_id}&mindate={last_date[game_id]}"

        url_data = urllib.request.urlopen(play_url).read()

        soup = BeautifulSoup(url_data, "html.parser")
        max_pages = math.ceil(int(soup.plays["total"]) / 100)

        for page in tqdm(range(max_pages, 0, -1), maxinterval=max_pages, desc="Page"):
            url_data = urllib.request.urlopen(f"{play_url}&mindate={last_date[game_id]}&page={page}").read()
            soup2 = BeautifulSoup(url_data, "html.parser")
            for play in soup2.findAll("play"):
                if not int(play["id"]) in id_collected:
                    dict = {
                        "playid": play["id"],
                        "userid": play["userid"],
                        "date": play["date"],
                        "quantity": play["quantity"],
                        "length": play["length"],
                        "location": play["location"],
                        "game": play.item["name"],
                    }
                    if not play.find("comments") == None:
                        dict.update({"comment": play.comments.text})
                    if not play.find("players") == None:
                        player_number = 1
                        for player in play.players.findAll("player"):
                            try:
                                dict.update(
                                    {f"player_{player_number}_score": int(player["score"])}
                                )
                            except:
                                player_number += 1
                                pass
                            player_number += 1
                    final_data.append(dict)
                    last_date.update({game_id: play["date"]})
                    id_collected.append(int(play["id"]))
            sleep(1.5)
            with data_export.open("w") as file:
                json.dump(final_data, file)

            id_collected_json.update({game_id: id_collected})
            with id_collected_file.open("w") as file:
                json.dump(id_collected_json, file)

            with last_date_file.open("w") as file:
                json.dump(last_date, file)

        return final_data
