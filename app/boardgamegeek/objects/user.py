class User:

    def __init__(self, data):

        self._data = data
        self._id = data["id"]

        self._user_name = data["user_name"]
        self._first_name = data["first_name"]
        self._last_name = data["last_name"]
        self._avatar_link = data["avatar_link"]
        self._year_registered = data["year_registered"]
        self._last_login = data["last_login"]
        self._state_or_province = data["state_or_province"]
        self._country = data["country"]
        self._trade_rating = data["trade_rating"]

    def to_dict(self):
        return self._data

    @property
    def id(self):
        return self._id

    @property
    def user_name(self):
        return self._user_name

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def avatar_link(self):
        return self._avatar_link

    @property
    def year_registered(self):
        return self._year_registered

    @property
    def last_login(self):
        return self._last_login

    @property
    def state_or_province(self):
        return self._state_or_province

    @property
    def country(self):
        return self._country

    @property
    def webaddress(self):
        return self._webaddress

    @property
    def trade_rating(self):
        return self._trade_rating
