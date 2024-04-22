from .things import Thing

class BoardGame(Thing):

    def __init__(self, data):
        self._data = data
        super().__init__(data)

        self._type = data["type"]
        self._description = data["description"]
        self._year_published = data["year_published"]
        self._min_players = data["min_players"]
        self._max_players = data["max_players"]
        self._play_time = data["play_time"]
        self._min_play_time = data["min_play_time"]
        self._max_play_time = data["max_play_time"]
        self._min_age = data["min_age"]
        self._boardgame_category = data["boardgame_category"]
        self._boardgame_mechanic = data["boardgame_mechanic"]
        self._designer = data["designer"]


    def to_dict(self):
        return self._data

    @property
    def type (self):
        return self._type

    @property
    def description (self):
        return self._description

    @property
    def year_published (self):
        return self._year_published



    @property
    def min_players(self):
        return self._min_players

    @property
    def max_players(self):
        return self._max_players

    @property
    def play_time(self):
        return self._play_time

    @property
    def min_play_time(self):
        return self._min_play_time

    @property
    def max_play_time(self):
        return self._max_play_time

    @property
    def min_age(self):
        return self._min_age


    @property
    def boardgame_category(self):
        return self._boardgame_category

    @property
    def boardgame_mechanic(self):
        return self._boardgame_mechanic

    @property
    def designer(self):
        return self._designer


