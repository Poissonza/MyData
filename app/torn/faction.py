from app.torn.api import TornAPI


class Faction(TornAPI):

    def __init__(self, key: str = None, comment: str = "python"):
        if key is None:
            from app.config import Config

            key = Config.TORN_API_KEY
        super().__init__(key=key, category="faction", comment=comment)

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

    def get_balance(self, timestamp: int = None) -> dict:
        return self.get_torn_data("balance", timestamp=timestamp)

    def get_basic(self, timestamp: int = None) -> dict:
        return self.get_torn_data("basic", timestamp=timestamp)

    def get_chains(
        self,
        limit: int = None,
        sort: str = None,
        to: int = None,
        ts_from: int = None,
        timestamp: int = None,
    ) -> dict:
        return self.get_torn_data(
            "chains",
            limit=limit,
            sort=sort,
            to=to,
            **{"from": ts_from} if ts_from else {},
            timestamp=timestamp,
        )

    def get_crimes(
        self,
        category: str = None,
        filters: str = None,
        offset: int = None,
        ts_from: int = None,
        ts_to: int = None,
        sort: str = None,
        timestamp: int = None,
    ) -> dict:
        return self.get_torn_data(
            "crimes",
            category=category,
            filters=filters,
            offset=offset,
            **{"from": ts_from} if ts_from else {},
            to=ts_to,
            sort=sort,
            timestamp=timestamp,
        )

    def get_members(self) -> dict:
        return self.get_torn_data("members")

    def get_news_armoury_deposit(
        self,
        sort: str = "ASC",
        striptags: str = "true",
        to_ts: int = None,
        from_ts: int = None,
    ) -> dict:
        return self.get_torn_data(
            "news",
            cat="armoryDeposit",
            sort=sort,
            striptags=striptags,
            to=to_ts,
            **{"from": from_ts} if from_ts else {},
        )

    def get_news_armoury_action(
        self,
        sort: str = "ASC",
        striptags: str = "true",
        ts_to: int = None,
        ts_from: int = None,
    ) -> dict:
        return self.get_torn_data(
            "news",
            cat="armoryAction",
            sort=sort,
            striptags=striptags,
            to=ts_to,
            **{"from": ts_from} if ts_from else {},
        )
