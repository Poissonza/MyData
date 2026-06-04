from __future__ import annotations

from app.storage.delta import DeltaWriter


class TTTVideoWriter(DeltaWriter):
    TABLE_NAME = "ttt/video"


class TTTRoundsWriter(DeltaWriter):
    TABLE_NAME = "ttt/rounds"
    PARTITION_BY = ["video_link"]


class TTTPlayersWriter(DeltaWriter):
    TABLE_NAME = "ttt/players"


class TTTRolesWriter(DeltaWriter):
    TABLE_NAME = "ttt/roles"


class TTTWinnerChartWriter(DeltaWriter):
    TABLE_NAME = "ttt/winnerchartdetails"


class TTTPlaysWriter(DeltaWriter):
    TABLE_NAME = "ttt/plays"
    PARTITION_BY = ["video_id"]
