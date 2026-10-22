import requests as re
from bs4 import BeautifulSoup


class bgg_api:
    def __init__(self):
        self.base_url = "https://boardgamegeek.com/xmlapi2/"

    def fetch_player(self, player_name):
        parameters = {"name": player_name}

        request = re.get(f"{self.base_url}user", params=parameters)

        print(f"status code: {request.status_code}")
        soup = BeautifulSoup(request.content, "xml")

        final_dict = {
            "id": soup.find("user")["id"],
            "username": soup.find("user")["name"],
            "firstname": soup.find("firstname")["value"],
            "lastname": soup.find("lastname")["value"],
            "yearregistered": soup.find("yearregistered")["value"],
            "lastlogin": soup.find("lastlogin")["value"],
            "stateorprovince": soup.find("stateorprovince")["value"],
            "country": soup.find("country")["value"],
        }
        return final_dict

    def fetch_collection(self, username, id):

        conversion_dict = {"0": False, "1": True}
        url = f"{self.base_url}collection"

        parameters = {"username": username, "stats": 1}
        requests = re.get(url, params=parameters)
        soup = BeautifulSoup(requests.content, "xml")
        games = soup.findAll("item")
        final_results = []

        for game in games:
            rating = None
            if game.find("rating")["value"] != "N/A":
                rating = float(game.find("rating")["value"])

            res_dict = {
                "collid": game["collid"],
                "gameid": game["objectid"],
                "playerid": id,
                "own": conversion_dict[game.find("status")["own"]],
                "preordered": conversion_dict[game.find("status")["preordered"]],
                "prevowned": conversion_dict[game.find("status")["prevowned"]],
                "want": conversion_dict[game.find("status")["want"]],
                "wanttobuy": conversion_dict[game.find("status")["wanttobuy"]],
                "wanttoplay": conversion_dict[game.find("status")["wanttoplay"]],
                "wishlist": conversion_dict[game.find("status")["wishlist"]],
                "rating": rating,
            }
            final_results.append(res_dict)
        return final_results

    def fetch_game(self, gameid):
        url = f"{self.base_url}thing?id={gameid}"
        url_params = {"id": gameid, "stats": 1}
        request = re.get(f"{self.base_url}thing", params=url_params)

        print(f"Status Code:{request.status_code}")
        print(request.url)
        soup = BeautifulSoup(request.content, "xml")

        try:
            name = soup.find("name", type="primary")["value"]
        except:
            name = None

        final_dict = {
            "id": gameid,
            "name": name,
            "yearpublished": int(soup.find("yearpublished")["value"]),
            "minplayers": int(soup.find("minplayers")["value"]),
            "maxplayers": int(soup.find("maxplayers")["value"]),
            "playingtime": int(soup.find("playingtime")["value"]),
            "minage": int(soup.find("minage")["value"]),
            "rating": float(soup.find("ratings").find("average")["value"]),
            "weight": float(soup.find("ratings").find("averageweight")["value"]),
        }

        return final_dict

    def fetch_plays(self, user_name=None, game_id=None):
        if user_name is None:
            url = f"{self.base_url}plays?id={game_id}"
        else:
            url = f"{self.base_url}plays?username={user_name}"

        request = re.get(url)
