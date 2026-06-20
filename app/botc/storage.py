from app.storage.delta import DeltaWriter

class BOTCPlayersWriter(DeltaWriter):
    TABLE_NAME = "botc/players"

class BOTCRolesWriter(DeltaWriter):
    TABLE_NAME = "botc/roles"