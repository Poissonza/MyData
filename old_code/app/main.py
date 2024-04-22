# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


# from pcgaming import GameData
from boardgamegeek import ThingAPI, BoardGame
from database import DataBaseConnection

# Press the green button in the gutter to run the script.
if __name__ == "__main__":

    database_connection = DataBaseConnection("boardgames", "boardgames",
                                             "db", database="boardgames", schema="bgg")

    test = ThingAPI()

    xml_data = test.get_xml({"id": 192836, "versions": 1})
    xml_data = test.get_xml({"id": 173064, "versions": 1, "stats": 1})
    for item in xml_data:
        boardgame = BoardGame(item)
        boardgame.to_database(database_connection)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
