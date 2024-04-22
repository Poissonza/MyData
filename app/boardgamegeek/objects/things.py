class Thing:

    def __init__(self, data):

        self._id = data["id"]
        self._name = data["name"]

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name
