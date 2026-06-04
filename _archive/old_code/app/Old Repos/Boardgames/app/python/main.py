from API.bgg_api import bgg_api
from bgg_db_connector.DBConnector import DBConnector
import pandas as pd
import time
from tqdm import tqdm

PLAYERS = ["scod101"]

bgg_api = bgg_api()
con = DBConnector()

for player in PLAYERS:
    if con.check_player(player):
        print("Player does not exist")
        con.insert_player(bgg_api.fetch_player(player))
    else:
        print("Player already exists")
collected_players = pd.DataFrame(con.get_players())
for v, row in collected_players.iterrows():
    print(f"row {row}")
    col_data = bgg_api.fetch_collection(row["username"], row["id"])
    try:
        current_games = pd.DataFrame(con.check_games())["id"].values
        print(current_games)
    except:
        current_games = [-99]
    for game in tqdm(pd.DataFrame(col_data)["gameid"].values):
        if not int(game) in current_games:
            print(f"fetching id: {game}")
            data = [bgg_api.fetch_game(game)]
            con.insert_game(data)
            time.sleep(5)
    con.insert_collection(col_data)


bgg_api.fetch_game(5)
bgg_api.fetch_plays(user_name="scod101")
