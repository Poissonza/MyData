class Play:

    def __init__(self, data):

        self._id = data["id"]
        self._date = data["date"]
        self._quantity = data["quantity"]
        self._length = data["length"]
        self._incomplete = data["incomplete"]
        self._now_in_stats = data["now_in_stats"]
        self._location = data["location"]

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
