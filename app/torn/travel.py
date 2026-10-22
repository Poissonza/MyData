from __future__ import annotations

from datetime import datetime


class TravelDataCleaning:

    def clean(self, api_data: dict) -> dict[str, list]:
        travel = []
        purchase = []
        hunt = []
        rehab = []
        travel_fee = []
        fortune_teller = []

        for log_id, entry in api_data.items():
            base = {
                "id": log_id,
                "log": entry["log"],
                "title": entry["title"],
                "timestamp": entry["timestamp"],
                "timestamp_conv": datetime.fromtimestamp(entry["timestamp"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "category": entry["category"],
            }

            title = entry["title"]
            data = entry.get("data", {})

            if title == "Travel initiate":
                base.update(
                    {
                        "origin": data["origin"],
                        "destination": data["destination"],
                        "travel_method": data["travel_method"],
                        "duration": data["duration"],
                    }
                )
                travel.append(base)
            elif title == "Item abroad buy":
                base.update(
                    {
                        "item": data["item"],
                        "quantity": int(data["quantity"]),
                        "cost_each": int(data["cost_each"]),
                        "cost_total": int(data["cost_total"]),
                        "destination": data["area"],
                    }
                )
                purchase.append(base)
            elif title == "Hunting":
                base.update(
                    {
                        "session_type": data["session_type"],
                        "cost": int(data["cost"]),
                        "income": int(data["income"]),
                    }
                )
                hunt.append(base)
            elif title == "Rehab":
                base.update(
                    {
                        "cost": data["cost"],
                        "rehab_times": data["rehab_times"],
                        "addiction": data["addiction"],
                        "happy_increased": data["happy_increased"],
                    }
                )
                rehab.append(base)
            elif title == "Travel fee":
                base.update({"cost": data["cost"]})
                travel_fee.append(base)
            elif title == "Fortune teller":
                base.update({"cost": data["cost"], "percentage": data["percentage"]})
                fortune_teller.append(base)
            elif title in (
                "Offshore bank withdraw",
                "Offshore bank deposit",
                "Offshore bank interest",
            ):
                base.update(data)
            else:
                raise ValueError(f"Unrecognised travel log title: {title!r}")

        return {
            "travel": travel,
            "purchase": purchase,
            "hunt": hunt,
            "rehab": rehab,
            "travel_fee": travel_fee,
            "fortune_teller": fortune_teller,
        }
