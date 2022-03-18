import pathlib
# import urllib
import requests
from bs4 import BeautifulSoup
import math
from tqdm import tqdm
from time import sleep
import json

from more_itertools import chunked


class BGGAPI:

    def populate_game_info_batch(self, game_id, db):
        fetched_games = db.get_game_id()
        collected_classification = db.get_classification_id()
        chunks = chunked(game_id, 100)
        for chunk in tqdm(chunks, desc="Game Chunk"):
            game_ids = ",".join([str(item) for item in chunk])
            game_url = f"https://boardgamegeek.com/xmlapi2/thing?id={game_ids}&stats=1"
            url_data = requests.get(game_url).content
            soup = BeautifulSoup(url_data, "html.parser")
            # return soup
            for game in soup.findAll("item"):
                if not int(game["id"]) in fetched_games:
                    dict = {
                        "id": int(game["id"]),
                        "name": game.find("name", type="primary")["value"],
                        "yearpublished": int(game.find("yearpublished")["value"]),
                        "minplayers": int(game.find("minplayers")["value"]),
                        "maxplayers": int(game.find("maxplayers")["value"]),
                        "playingtime": int(game.find("playingtime")["value"]),
                        "minplaytime": int(game.find("minplaytime")["value"]),
                        "maxplaytime": int(game.find("maxplaytime")["value"]),
                        "minage": int(game.find("minage")["value"]),
                        "usersrated": int(game.find("usersrated")["value"]),
                        "average": float(game.find("average")["value"]),
                        "bayesaverage": float(game.find("bayesaverage")["value"]),
                        "stddev": float(game.find("stddev")["value"]),
                        "media": int(game.find("median")["value"]),
                        "owned": int(game.find("owned")["value"]),
                        "trading": int(game.find("trading")["value"]),
                        "wanting": int(game.find("wanting")["value"]),
                        "wishing": int(game.find("wishing")["value"]),
                        "numcomments": int(game.find("numcomments")["value"]),
                        "numweights": int(game.find("numweights")["value"]),
                        "averageweight": float(game.find("averageweight")["value"]),
                        "description": game.find("description").contents[0],
                    }
                    for classification in game.findAll("link"):
                        class_dict = {
                            "gameid": int(game["id"]),
                            "classificationid": int(classification["id"])
                        }
                        if not int(classification["id"]) in collected_classification:
                            db.insert_classification(
                                {
                                    "id": int(classification["id"]),
                                    "type": classification["type"],
                                    "value": classification["value"]
                                }
                            )
                            collected_classification.append(int(classification["id"]))
                        db.insert_classification_link(class_dict)
                    if game.find("rank") is not None:
                        for rank in game.findAll("rank"):
                            db.insert_rank(
                                {
                                    "type": rank["type"],
                                    "id": int(rank["id"]),
                                    "gameid": int(game["id"]),
                                    "name": rank["name"],
                                    "friendlyname": rank["friendlyname"],
                                    "value": int(rank["value"]),
                                    "bayesaverage": float(rank["bayesaverage"]),
                                }
                            )

                    fetched_games.append(int(game["id"]))
                    db.insert_game(dict)
            sleep(1)

    def populate_game_info(self, game_id: list, db):
        fetched_games = db.get_game_id()
        chunks = chunked(game_id, 100)
        for game in tqdm(game_id, desc="Game"):
            if not game in fetched_games:
                game_url = f"https://boardgamegeek.com/xmlapi2/thing?id={game}&stats=1"
                url_data = requests.get(game_url).content
                soup = BeautifulSoup(url_data, "html.parser")
                dict = {
                    "id": int(soup.items.item["id"]),
                    "name": soup.find("name", type="primary")["value"],
                    "yearpublished": int(soup.find("yearpublished")["value"]),
                    "minplayers": int(soup.find("minplayers")["value"]),
                    "maxplayers": int(soup.find("maxplayers")["value"]),
                    "playingtime": int(soup.find("playingtime")["value"]),
                    "minplaytime": int(soup.find("minplaytime")["value"]),
                    "maxplaytime": int(soup.find("maxplaytime")["value"]),
                    "minage": int(soup.find("minage")["value"]),
                    "usersrated": int(soup.find("usersrated")["value"]),
                    "average": float(soup.find("average")["value"]),
                    "bayesaverage": float(soup.find("bayesaverage")["value"]),
                    "stddev": float(soup.find("stddev")["value"]),
                    "media": int(soup.find("median")["value"]),
                    "owned": int(soup.find("owned")["value"]),
                    "trading": int(soup.find("trading")["value"]),
                    "wanting": int(soup.find("wanting")["value"]),
                    "wishing": int(soup.find("wishing")["value"]),
                    "numcomments": int(soup.find("numcomments")["value"]),
                    "numweights": int(soup.find("numweights")["value"]),
                    "averageweight": float(soup.find("averageweight")["value"]),
                }
                db.insert_game(dict)

    def get_plays(selfs, game_id: int, db):
        id_collected = db.get_play_id(game_id)
        last_date = db.get_last_date(game_id)[0]

        if last_date is None:
            last_date = "0000-00-00"

        play_url = f"https://boardgamegeek.com/xmlapi2/plays?id={game_id}"

        url_data = requests.get(
            f"{play_url}&mindate={last_date}"
        ).content

        soup = BeautifulSoup(url_data, "html.parser")
        max_pages = math.ceil(int(soup.plays["total"]) / 100)

        for page in tqdm(range(max_pages, 0, -1), maxinterval=max_pages, desc=f"{game_id}: Page"):
            url_data = requests.get(
                f"{play_url}&mindate={last_date}&page={page}"
            ).content
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
            sleep(1)
