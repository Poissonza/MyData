import urllib
from bs4 import BeautifulSoup

class BGGAPI:
    def populate_game_info(self, game_id: int):
        final_dict = {"bggId" : game_id}

        game_url = f"https://boardgamegeek.com/xmlapi2/thing?id={game_id}&stats=1"
        url_data = urllib.request.urlopen(game_url).read()

        soup = BeautifulSoup(url_data, "html.parser")

        final_dict.update({"weight": float(soup.items.find("averageweight")["value"])})
        return final_dict
