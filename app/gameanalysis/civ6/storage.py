from __future__ import annotations

from app.storage.delta import DeltaWriter


class Civ6ExpansionLoader(DeltaWriter):
    TABLE_NAME = "civ6/expansion"


class Civ6CivilizationsLoader(DeltaWriter):
    TABLE_NAME = "civ6/civilizations"


class Civ6WondersLoader(DeltaWriter):
    TABLE_NAME = "civ6/wonders"


class Civ6GameModeLoader(DeltaWriter):
    TABLE_NAME = "civ6/gamemode"


class Civ6GameSpeedLoader(DeltaWriter):
    TABLE_NAME = "civ6/gamespeed"


class Civ6MapTypeLoader(DeltaWriter):
    TABLE_NAME = "civ6/maptype"


class Civ6MapFeatureLoader(DeltaWriter):
    TABLE_NAME = "civ6/mapfeature"


class Civ6SecretSocietyLoader(DeltaWriter):
    TABLE_NAME = "civ6/secretsociety"


class Civ6CityStateLoader(DeltaWriter):
    TABLE_NAME = "civ6/citystate"


class Civ6LuxuryResourcesLoader(DeltaWriter):
    TABLE_NAME = "civ6/luxuryresources"


class Civ6PlayedGame(DeltaWriter):
    TABLE_NAME = "civ6/playedgame"
