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

    def get_plays(selfs, game_id: int, db):

        id_collected = db.get_play_id(game_id)
        last_date = db.get_last_date(game_id)[0]

        if last_date is None:
            last_date = "0000-00-00"

        play_url = f"https://boardgamegeek.com/xmlapi2/plays?id={game_id}"

        url_data = urllib.request.urlopen(
            f"{play_url}&mindate={last_date}"
        ).read()

        soup = BeautifulSoup(url_data, "html.parser")
        max_pages = math.ceil(int(soup.plays["total"]) / 100)

        for page in tqdm(range(max_pages, 0, -1), maxinterval=max_pages, desc=f"{game_id}: Page"):
            url_data = urllib.request.urlopen(
                f"{play_url}&mindate={last_date}&page={page}"
            ).read()
            soup2 = BeautifulSoup(url_data, "html.parser")
            for play in soup2.findAll("play"):
                if not int(play["id"]) in id_collected:
                    dict = {
                        "playid": int(play["id"]),
                        "userid": int(play["userid"]),
                        "date": play["date"],
                        "quantity": play["quantity"],
                        "length": int(play["length"]),
                        "location": play["location"],
                        "game": play.item["name"],
                        "gameid": game_id,
                    }
                    if not play.find("comments") == None:
                        dict.update({"comments": play.comments.text})
                    if not play.find("players") == None:
                        for player in play.players.findAll("player"):
                            player_dict = {
                                "playid": int(play["id"]),
                                "username": player["username"],
                                "userid": int(player["userid"]),
                                "name": player["name"],
                                "color": player["color"],
                            }
                            list = ["startposition", "new", "rating", "win", "score"]
                            for item in list:
                                try:
                                    player_dict.update({item: int(player[item])})
                                except:
                                    pass

                            db.insert_player_play(player_dict)
                    db.insert_play(dict)
                    last_date = play["date"]
                    id_collected.append(int(play["id"]))
            sleep(1.5)
