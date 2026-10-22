import pandas as pd
from datetime import datetime as dt


class DataCleaning:
    def __init__(self):
        pass

    def travel_data_clean(self, api_data: dict):
        travel = []
        purchase = []
        hunt = []
        rehab = []
        travel_fee = []
        fortune_teller = []

        for travel_data in api_data:
            id = travel_data
            ind_data = api_data[id]

            ind_dict = {
                "id": id,
                "log": ind_data["log"],
                "title": ind_data["title"],
                "timestamp": ind_data["timestamp"],
                "timestamp_conv": dt.fromtimestamp(ind_data["timestamp"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "category": ind_data["category"],
            }

            if ind_data["title"] == "Travel initiate":
                ind_dict.update(
                    {
                        "origin": ind_data["data"]["origin"],
                        "destination": ind_data["data"]["destination"],
                        "travel_method": ind_data["data"]["travel_method"],
                        "duration": ind_data["data"]["duration"],
                    }
                )
                travel.append(ind_dict)

            elif ind_data["title"] == "Item abroad buy":
                ind_dict.update(
                    {
                        "item": ind_data["data"]["item"],
                        "quantity": int(ind_data["data"]["quantity"]),
                        "cost_each": int(ind_data["data"]["cost_each"]),
                        "cost_total": int(ind_data["data"]["cost_total"]),
                        "destination": ind_data["data"]["area"],
                    }
                )

                purchase.append(ind_dict)

            elif ind_data["title"] == "Hunting":
                ind_dict.update(
                    {
                        "session_type": ind_data["data"]["session_type"],
                        "cost": int(ind_data["data"]["cost"]),
                        "income": int(ind_data["data"]["income"]),
                    }
                )

                hunt.append(ind_dict)
            elif ind_data["title"] == "Rehab":
                ind_dict.update(
                    {
                        "cost": ind_data["data"]["cost"],
                        "rehab_times": ind_data["data"]["rehab_times"],
                        "addiction": ind_data["data"]["addiction"],
                        "happy_increased": ind_data["data"]["happy_increased"],
                    }
                )
                rehab.append(ind_dict)
            elif ind_data["title"] == "Offshore bank withdraw":
                ind_dict.update(
                    {
                        "withdrawn": ind_data["data"]["withdrawn"],
                        "balance": ind_data["data"]["balance"],
                    }
                )
            elif ind_data["title"] == "Offshore bank deposit":
                ind_dict.update(
                    {
                        "deposited": ind_data["data"]["deposited"],
                        "balance": ind_data["data"]["balance"],
                    }
                )
            elif ind_data["title"] == "Travel fee":
                ind_dict.update(
                    {
                        "cost": ind_data["data"]["cost"],
                    }
                )

                travel_fee.append(ind_dict)
            elif ind_data["title"] == "Fortune teller":
                ind_dict.update(
                    {
                        "cost": ind_data["data"]["cost"],
                        "percentage": ind_data["data"]["percentage"],
                    }
                )

                fortune_teller.append(ind_dict)
            elif ind_data["title"] == "Offshore bank interest":
                ind_dict.update(
                    {
                        "interest": ind_data["data"]["interest"],
                        "balance": ind_data["data"]["balance"],
                    }
                )
            else:
                raise Exception(f"Invalid Travel title: {ind_data['title']}")
        return travel, purchase, hunt, rehab, travel_fee, fortune_teller

    def item_data_clean(self, api_data: dict):
        items = []
        for item in api_data["items"]:
            item_dict = {
                "id": item["id"],
                "name": item["name"],
                "description": item["description"],
                "effect": item["effect"],
                "requirement": item["requirement"],
                "type": item["type"],
                "sub_type": item["sub_type"],
                "is_masked": item["is_masked"],
                "is_tradable": item["is_tradable"],
                "is_found_in_city": item["is_found_in_city"],
                "circulation": item["circulation"],
                "vendor": item["value"]["vendor"],
                # "country": item["value"]["country"],
                "market_price": item["value"]["market_price"],
            }
            items.append(item_dict)

        return items

    def item_market_data_clean(self, api_data: dict):
        item_purchase = []
        item_sale = []
        item_add = []
        for id in api_data:
            trans = api_data[id]

            ind_dict = {
                "id": id,
                "title": trans["title"],
                "timestamp": trans["timestamp"],
                "timestamp_conv": dt.fromtimestamp(trans["timestamp"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "category": trans["category"],
            }

            if trans["title"] == "Item market sell":
                ind_dict.update(
                    {
                        "buyer": trans["data"]["buyer"],
                        "anonymous": trans["data"]["anonymous"],
                        "ItemID": trans["data"]["items"][0]["id"],
                        "quantity": trans["data"]["items"][0]["qty"],
                        "cost_total": trans["data"]["cost_total"],
                        "fee": trans["data"]["fee"],
                        "cost_each": trans["data"]["cost_each"],
                    }
                )

                item_sale.append(ind_dict)
            elif trans["title"] == "Item market buy":
                ind_dict.update(
                    {
                        "seller": trans["data"]["seller"],
                        "anonymous": trans["data"]["anonymous"],
                        "ItemID": trans["data"]["items"][0]["id"],
                        "quantity": trans["data"]["items"][0]["qty"],
                        "cost_total": trans["data"]["cost_total"],
                        "cost_each": trans["data"]["cost_each"],
                    }
                )
                item_purchase.append(ind_dict)
            elif trans["title"] == "Item market add":
                ind_dict.update(
                    {
                        "anonymous": trans["data"]["anonymous"],
                        "ItemID": trans["data"]["items"][0]["id"],
                        "quantity": trans["data"]["items"][0]["qty"],
                        "price": trans["data"]["price"],
                    }
                )
                item_add.append(ind_dict)
            elif trans["title"] == "Item market remove":
                ind_dict.update(
                    {
                        "ItemID": trans["data"]["items"][0]["id"],
                        "quantity": trans["data"]["items"][0]["qty"],
                    }
                )
            elif trans["title"] == "Item market price edit":
                ind_dict.update(
                    {
                        "ItemID": trans["data"]["items"][0]["id"],
                        "quantity": trans["data"]["items"][0]["qty"],
                        "price_before": trans["data"]["price_before"],
                        "price_after": trans["data"]["price_after"],
                    }
                )
            else:
                raise Exception(f"Invalid Travel title: {trans['title']}")

        return item_sale, item_purchase, item_add

    def full_log_data_clean(self, api_data: dict):
        final_list = []
        for id in api_data:
            clean_dict = {
                "id": id,
                "log": api_data[id]["log"],
                "title": api_data[id]["title"],
                "timestamp": api_data[id]["timestamp"],
                "time_stamp_utc": dt.fromtimestamp(api_data[id]["timestamp"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "category": api_data[id]["category"],
            }

            try:
                clean_dict.update({"data": api_data[id]["data"]})
            except KeyError:
                pass
            final_list.append(clean_dict)

        return final_list

    def faction_attack_log_clean(self, api_data: dict):
        final_list = []
        for attack_id in api_data["attacks"]:
            ind_attack = attack_id
            clean_dict = {
                "id": ind_attack["id"],
                "code": ind_attack["code"],
                "started": ind_attack["started"],
                "started_clean": dt.fromtimestamp(ind_attack["started"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "ended": ind_attack["ended"],
                "ended_clean": dt.fromtimestamp(ind_attack["ended"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "result": ind_attack["result"],
                "respect_gain": ind_attack["respect_gain"],
                "respect_loss": ind_attack["respect_loss"],
                "chain": ind_attack["chain"],
                "is_interrupted": ind_attack["is_interrupted"],
                "is_stealthed": ind_attack["is_stealthed"],
                "is_raid": ind_attack["is_raid"],
                "is_ranked_war": ind_attack["is_ranked_war"],
                "fair_fight_modifier": ind_attack["modifiers"]["fair_fight"],
                "war_modifier": ind_attack["modifiers"]["war"],
                "retaliation_modifier": ind_attack["modifiers"]["retaliation"],
                "group_modifier": ind_attack["modifiers"]["group"],
                "overseas_modifier": ind_attack["modifiers"]["overseas"],
                "chain_modifier": ind_attack["modifiers"]["chain"],
                "warlord_modifier": ind_attack["modifiers"]["warlord"],
            }

            if ind_attack["attacker"] is not None:
                clean_dict.update(
                    {
                        "attacker_id": ind_attack["attacker"]["id"],
                        "attacker_name": ind_attack["attacker"]["name"],
                        "attacker_level": ind_attack["attacker"]["level"],
                    }
                )

                if ind_attack["attacker"]["faction"] is not None:
                    clean_dict.update(
                        {
                            "attacker_faction_id": ind_attack["attacker"]["faction"][
                                "id"
                            ],
                            "attacker_faction_name": ind_attack["attacker"]["faction"][
                                "name"
                            ],
                        }
                    )

            if "defender" in ind_attack.keys():
                clean_dict.update(
                    {
                        "defender_id": ind_attack["defender"]["id"],
                        "defender_name": ind_attack["defender"]["name"],
                        "defender_level": ind_attack["defender"]["level"],
                    }
                )

                if ind_attack["defender"]["faction"] is not None:
                    clean_dict.update(
                        {
                            "defender_faction_id": ind_attack["defender"]["faction"][
                                "id"
                            ],
                            "defender_faction_name": ind_attack["defender"]["faction"][
                                "name"
                            ],
                        }
                    )
            final_list.append(clean_dict)

        return final_list
