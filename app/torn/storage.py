from __future__ import annotations

import datetime

from app.storage.delta import DeltaWriter


class TornEntityWriter(DeltaWriter):
    PARTITION_BY = ["endpoint"]

    def write_response(self, endpoint: str, response: dict) -> None:
        rows = [
            {
                "endpoint": endpoint,
                "retrieved_at": datetime.datetime.utcnow().isoformat(),
                "data": response,
            }
        ]
        self.write(rows, mode="append")


class TornUserWriter(TornEntityWriter):
    TABLE_NAME = "torn/user"


class TornFactionWriter(TornEntityWriter):
    TABLE_NAME = "torn/faction"
