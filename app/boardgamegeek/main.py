# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from api import ThingAPI
from objects import BoardGame

if __name__ == "__main__":
    test = ThingAPI()

    xml_data = test.get_xml({"id": 192836, "versions": 1})
    xml_data = test.get_xml({"id": 173064, "versions": 1, "stats": 1})
    for item in xml_data:
        boardgame = BoardGame(item)
    # print(boardgame.to_dict())
