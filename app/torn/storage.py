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


class TornTravelWriter(DeltaWriter):
    TABLE_NAME = "torn/travel"
    PARTITION_BY = ["category"]

    def write_travel_data(self, cleaned: dict[str, list]) -> None:
        for category, rows in cleaned.items():
            if rows:
                for row in rows:
                    row["category"] = category
                self.write(rows, mode="append")
