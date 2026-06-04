from app.torn.api import TornAPI


class User(TornAPI):

    def __init__(self, key: str = None, comment: str = "python"):
        if key is None:
            from app.config import Config

            key = Config.TORN_API_KEY
        super().__init__(key=key, category="user", comment=comment)

    def get_base_user(self) -> dict:
        return self.get_torn_data("")

    def get_attacks(
        self,
        filters: str = None,
        limit: int = None,
        sort: str = None,
        to: int = None,
        ts_from: int = None,
        timestamp: int = None,
    ) -> dict:
        return self.get_torn_data(
            "attacks",
            filters=filters,
            limit=limit,
            sort=sort,
            to=to,
            **{"from": ts_from} if ts_from else {},
            timestamp=timestamp,
        )

    def get_basic(self, striptags: str = None, timestamp: int = None) -> dict:
        return self.get_torn_data("basic", striptags=striptags, timestamp=timestamp)

    def get_bounties(self, timestamp: int = None) -> dict:
        return self.get_torn_data("bounties", timestamp=timestamp)

    def get_battlestats(self, timestamp: int = None) -> dict:
        return self.get_torn_data("battlestats", timestamp=timestamp)

    def get_education(self, timestamp: int = None) -> dict:
        return self.get_torn_data("education", timestamp=timestamp)

    def get_enlisted_cars(self, timestamp: int = None) -> dict:
        return self.get_torn_data("enlistedcars", timestamp=timestamp)

    def get_hof(self, timestamp: int = None) -> dict:
        return self.get_torn_data("hof", timestamp=timestamp)

    def get_honors(self, timestamp: int = None) -> dict:
        return self.get_torn_data("honors", timestamp=timestamp)

    def get_job_points(self, timestamp: int = None) -> dict:
        return self.get_torn_data("jobpoints", timestamp=timestamp)
