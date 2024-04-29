class Play:

    def __init__(self, data):

        self._data = data

        self._id = data["id"]
        self._date = data["date"]
        self._quantity = data["quantity"]
        self._length = data["length"]
        self._incomplete = data["incomplete"]
        self._now_in_stats = data["now_in_stats"]
        self._location = data["location"]
        self._objectid = data["objectid"]

    def to_dict(self):
        return self._data

    @property
    def objectid(self):
        return self._objectid

    @property
    def location(self):
        return self._location

    @property
    def now_in_stats(self):
        return self._now_in_stats

    @property
    def incomplete(self):
        return self._incomplete

    @property
    def length(self):
        return self._length

    @property
    def quantity(self):
        return self._quantity

    @property
    def date(self):
        return self._date

    @property
    def id(self):
        return self._id

class PlayPlayer:

    def __init__(self, data):
        self._data = data

        self._id = data["id"]
        self._name = data["name"]
        self._start_position = data["start_position"]
        self._colour = data["colour"]
        self._score = data["score"]
        self._new = data["new"]
        self._rating = data["rating"]
        self._win = data["win"]