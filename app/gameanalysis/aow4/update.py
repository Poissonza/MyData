from .loader import AOW4Loader
import pathlib
import json

DATA_DIR = pathlib.Path(__file__).parent / "data"


ao4 = AOW4Loader()
ao4.load(DATA_DIR / "game_played.json")
