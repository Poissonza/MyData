from .util import XMLTools
import xml.etree.ElementTree as ET


class Thing:

    def __init__(self, xml_data):
        self._xml_data = xml_data
        self._xml_tool = XMLTools(xml_data)

        self._id = None
        self._name = None
        self._type = None

        self.create_thing()

    def create_thing(self):
        self._id = self._xml_data.attrib.get("id")
        self._name = self._xml_data.find("name[@type='primary']").attrib.get("value")
        self._type = self._xml_data.attrib.get("type")
        # return dict

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type


class BoardGame(Thing):

    def __init__(self, xml_data):
        super().__init__(xml_data)

        self._description = None
        self._year_published = None
        self._min_players = None
        self._max_players = None
        self._play_time = None
        self._min_play_time = None
        self._max_play_time = None
        self._min_age = None
        self._boardgame_category = None
        self._boardgame_mechanic = None
        self._boardgame_family = None
        self._designer = None
        self._version = None
        self.create_game()

    def create_game(self):
        self._description = self._xml_tool.fetch_element("description").text
        self._year_published = self._xml_tool.fetch_element(
            "yearpublished", "value", int
        )
        self._min_players = self._xml_tool.fetch_element("minplayers", "value", int)

        self._max_players = self._xml_tool.fetch_element("maxplayers", "value", int)
        self._play_time = self._xml_tool.fetch_element("playingtime", "value", int)

        self._min_play_time = self._xml_tool.fetch_element("minplaytime", "value", int)
        self._max_play_time = self._xml_tool.fetch_element("maxplaytime", "value", int)
        self._min_age = self._xml_tool.fetch_element("minage", "value", int)
        version_list = []
        for version in self._xml_data.find("versions"):
            version_list.append(BoardGameVersion(version))

        self._version = version_list

        self._boardgame_category = self._xml_tool.fetch_element_list(
            "link[@type='boardgamecategory']", "value"
        )
        self._boardgame_mechanic = self._xml_tool.fetch_element_list(
            "link[@type='boardgamemechanic']", "value"
        )
        self._boardgame_family = self._xml_tool.fetch_element_list(
            "link[@type='boardgamefamily']", "value"
        )
        self._designer = self._xml_tool.fetch_element_list(
            "link[@type='boardgamedesigner']", "value"
        )
        BoardGameStatistics(self._xml_data.find("statistics/ratings"))

    def to_dict(self):
        dict = {
            "id": self._id,
            "name": self._name,
            "type": self._type,
            "description": self._description,
            "year_published": self._year_published,
            "min_players": self._min_players,
            "max_players": self._max_players,
            "play_time": self._play_time,
            "min_play_time": self._min_play_time,
            "max_play_time": self._max_play_time,
            "min_age": self._min_age,
            "boardgame_category": self._boardgame_category,
            "boardgame_mechanic": self._boardgame_mechanic,
            "boardgame_family": self._boardgame_family,
            "designer": self._designer,
        }
        return dict

    def to_database(self, database_connection):
        database_connection.insert_data("games", self.to_dict())

    @property
    def description(self):
        return self._description

    @property
    def year_published(self):
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
    def version(self):
        return self._version

    @property
    def boardgame_category(self):
        return self._boardgame_category

    @property
    def boardgame_mechanic(self):
        return self._boardgame_mechanic

    @property
    def designer(self):
        return self._designer

    def __str__(self):
        return f"designer {self._designer}"


class BoardGameVersion(Thing):

    def __init__(self, xml_data):
        super().__init__(xml_data)
        self._thumbnail = None
        self._image = None
        self._game_id = None
        self._publisher = None
        self._artist = None
        self._year_published = None
        self._product_code = None
        self._width = None
        self._length = None
        self._depth = None
        self._weight = None
        self._language = None

        self.create_version()

    def create_version(self):
        self._thumbnail = self._xml_tool.fetch_element("thumbnail").text
        self._image = self._xml_tool.fetch_element("image").text
        self._game_id = self._xml_tool.fetch_element(
            "link[@type='boardgameversion']", "id", int
        )
        self._publisher = self._xml_tool.fetch_element_list(
            "link[@type='boardgamepublisher']", "value"
        )
        self._artist = self._xml_tool.fetch_element_list(
            "link[@type='boardgameartist']", "value"
        )
        self._year_published = self._xml_tool.fetch_element(
            "yearpublished", "value", int
        )
        self._product_code = self._xml_tool.fetch_element("productcode", "value")
        self._width = self._xml_tool.fetch_element("width", "value", float)
        self._length = self._xml_tool.fetch_element("length", "value", float)
        self._depth = self._xml_tool.fetch_element("depth", "value", float)
        self._weight = self._xml_tool.fetch_element("weight", "value", float)
        self._language = self._xml_tool.fetch_element("link[@type='language']", "value")

    def to_dict(self):
        dict = {
            "id": self._id,
            "name": self._name,
            "thumbnail": self._thumbnail,
            "image": self._image,
            "game_id": self._game_id,
            "publisher": self._publisher,
            "artist": self._artist,
            "year_published": self._year_published,
            "product_code": self._product_code,
            "width": self._width,
            "length": self._length,
            "depth": self._depth,
            "weight": self._weight,
            "language": self._language,
        }

        return dict

    @property
    def thumbnail(self):
        return self._thumbnail

    @property
    def image(self):
        return self._image

    @property
    def game_id(self):
        return self._game_id

    @property
    def publisher(self):
        return self._publisher

    @property
    def artist(self):
        return self._artist

    @property
    def year_published(self):
        return self._year_published

    @property
    def product_code(self):
        return self._product_code

    @property
    def width(self):
        return self._width

    @property
    def length(self):
        return self._length

    @property
    def depth(self):
        return self._depth

    @property
    def weight(self):
        return self._weight

    @property
    def language(self):
        return self._language

    def __str__(self):
        return f"Name: {self._name}, id: {self._id}, Type {self._type}, test: {self._product_code}, widht{self._width}, length: {self._length}, depth: {self._depth}, weight: {self._weight}, language: {self._language}"


class BoardGameStatistics:

    def __init__(self, xml_data):
        self._xml_tools = XMLTools(xml_data)
        self._xml_data = xml_data
        self._user_rated = None
        self._average_rating = None
        self._bayes_rating = None
        self._ranks = None
        self._stddev = None
        self._median = None
        self._owned = None
        self._trading = None
        self._wanting = None
        self._wishing = None
        self._num_comments = None
        self._num_weights = None
        self._average_weight = None

        self.create_statistics()
        print(self.to_dict())

    def create_statistics(self):
        self._user_rated = self._xml_tools.fetch_element("usersrated", "value", int)
        self._average_rating = self._xml_tools.fetch_element("average", "value", float)
        self._bayes_rating = self._xml_tools.fetch_element(
            "bayesaverage", "value", float
        )
        self._stddev = self._xml_tools.fetch_element("stddev", "value", float)
        self._median = self._xml_tools.fetch_element("median", "value", float)
        self._owned = self._xml_tools.fetch_element("owned", "value", int)
        self._trading = self._xml_tools.fetch_element("trading", "value", int)
        self._wanting = self._xml_tools.fetch_element("wanting", "value", int)
        self._wishing = self._xml_tools.fetch_element("wishing", "value", int)
        self._num_comments = self._xml_tools.fetch_element("numcomments", "value", int)
        self._num_weights = self._xml_tools.fetch_element("numweights", "value", int)
        self._average_weight = self._xml_tools.fetch_element(
            "averageweight", "value", float
        )

    def to_dict(self):
        dict = {
            "user_rated": self._user_rated,
            "average_rating": self._average_rating,
            "bayes_rating": self._bayes_rating,
            "stddev": self._stddev,
            "median": self._median,
            "owned": self._owned,
            "trading": self._trading,
            "wanting": self._wanting,
            "wishing": self._wishing,
            "num_comments": self._num_comments,
            "num_weights": self._num_weights,
            "average_weight": self._average_weight,
        }

        return dict

    @property
    def user_rated(self):
        return self._user_rated

    @property
    def average_rate(self):
        return self._average_rating

    @property
    def bayes_rating(self):
        return self._bayes_rating

    @property
    def rank(self):
        return self._ranks

    @property
    def stddev(self):
        return self._stddev

    @property
    def median(self):
        return self._median

    @property
    def owned(self):
        return self._owned

    @property
    def trading(self):
        return self._trading

    @property
    def wanting(self):
        return self._wanting

    @property
    def wishing(self):
        return self._wishing

    @property
    def num_comments(self):
        return self._num_comments

    @property
    def num_weight(self):
        return self._num_weights

    @property
    def average_weight(self):
        return self._average_weight


class User:

    def __init__(
        self,
        id,
        user_name: str,
        first_name: str,
        last_name: str,
        avatar_link: str,
        year_registered: int,
        last_login,
        state_or_province,
        country,
        webaddress,
        trade_rating,
    ):
        self._id = id
        self._user_name = user_name
        self._first_name = first_name
        self._last_name = last_name
        self._avatar_link = avatar_link
        self._year_registered = year_registered
        self._last_login = last_login
        self._state_or_province = state_or_province
        self._country = country
        self._webaddress = webaddress
        self._trade_rating = trade_rating

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
