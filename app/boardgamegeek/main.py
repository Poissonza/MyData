from app.boardgamegeek.api import ThingAPI
from app.boardgamegeek.objects.objects import BoardGame

if __name__ == "__main__":
    api = ThingAPI()
    xml_data = api.get_xml({"id": 173064, "versions": 1, "stats": 1})
    for item in xml_data:
        boardgame = BoardGame(item)
