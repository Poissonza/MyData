import pathlib
import json
from app.gameanalysis.civ6.storage import (Civ6CityStateLoader,
                                           Civ6ExpansionLoader,
                                           Civ6CivilizationsLoader,
                                           Civ6WondersLoader,
                                           Civ6GameModeLoader, Civ6GameSpeedLoader, Civ6MapTypeLoader,
                                           Civ6LuxuryResourcesLoader, Civ6PlayedGame)

DATA_DIR = pathlib.Path(__file__).parent / "data"


def _load_json(filename: str) -> list[dict]:
    return json.loads((DATA_DIR / filename).read_bytes())


def __load_all():
    __load_city_states()
    __load_civilizations()
    __load_expansions()
    __load_luxury_resource()
    # TODO: Fix the Spark loading for lists
    # __load_game_mode()
    # __load_game_speed()
    __load_wonders()
    # __load_map_types()
    # __load_victory_condition()
    __load_played_game()


def __load_city_states():
    data = _load_json("default_data.json")
    Civ6CityStateLoader().write(data["citystate"], mode="overwrite")
    print(f"Wrote {len(data['citystate'])} city state rows")


def __load_civilizations(mode: str = "overwrite"):
    data = _load_json("default_data.json")
    Civ6CivilizationsLoader().write(
        data["civilization"],
        mode=mode,
    )
    print(f"Wrote {len(data['civilization'])} civilization rows")


def __load_expansions(mode: str = "overwrite"):
    data = _load_json("default_data.json")
    Civ6ExpansionLoader().write(
        data["expansion"],
        mode=mode,
    )
    print(f"Wrote {len(data['expansion'])} expansion rows")

def __load_game_mode(mode: str = "overwrite"):
    data = _load_json("default_data.json")
    Civ6GameModeLoader().write(
        data["gamemode"],
        mode=mode,
    )
    print(f"Wrote {len(data['gamemode'])} gamemode rows")

def __load_game_speed(mode: str = "overwrite"):
    data = _load_json("default_data.json")
    Civ6GameSpeedLoader().write(
        data["gamespeed"],
    )
    print(f"Wrote {len(data['gamespeed'])} gamespeed rows")

def __load_luxury_resource(mode: str = "overwrite"):
    data = _load_json("default_data.json")
    Civ6LuxuryResourcesLoader().write(
        data["luxuryresource"],
        mode=mode,
    )
    print(f"Wrote {len(data['luxuryresource'])} luxury resource rows")

def __load_played_game(mode: str = "overwrite"):
    data = _load_json("game_played.json")
    Civ6PlayedGame().write(
        data,
        mode=mode,
    )
    print(f"Wrote {len(data)} played game rows")

def __load_wonders(mode: str = "overwrite"):
    data = _load_json("default_data.json")
    Civ6WondersLoader().write(
        data["wonder"],
        mode=mode,
    )
    print(f"Wrote {len(data['wonder'])} wonder rows")

def __load_map_types(mode: str = "overwrite"):
    data = _load_json("default_data.json")
    Civ6MapTypeLoader().write(
        data["maptype"],
        mode=mode,
    )
    print(f"Wrote {len(data['maptype'])} maptype rows")

def __load_victory_condition(mode: str = "overwrite"):
    data = _load_json("default_data.json")
    Civ6MapTypeLoader().write(
        data["VicoryCondition"],
        mode=mode,
    )
    print(f"Wrote {len(data['VicoryCondition'])} Vicory Condition rows")


if __name__ == "__main__":
    __load_all()
