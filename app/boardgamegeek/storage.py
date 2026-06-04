from app.storage.delta import DeltaWriter


class BGGGamesWriter(DeltaWriter):
    TABLE_NAME = "boardgamegeek/games"
    PARTITION_BY = ["type"]


class BGGPlaysWriter(DeltaWriter):
    TABLE_NAME = "boardgamegeek/plays"
    PARTITION_BY = ["objectid"]


class BGGUsersWriter(DeltaWriter):
    TABLE_NAME = "boardgamegeek/users"
