from TornAPI.Torn import UserLog
from TornAPI.DataCleaning import DataCleaning

from TornAPI.Torn import TornAPI
import pandas as pd
import datetime as dt
import json
import time

import pathlib

api_key = "#####"

user = TornAPI(api_key)
user2 = UserLog(api_key)

data_clean = DataCleaning()
data = user.get_logcategories()

travel_folder = pathlib.Path("data") / "Travel"
torn_data_folder = pathlib.Path("data") / "Torn"
item_market_data_folder = pathlib.Path("data") / "Item Market"
output_folder = pathlib.Path("data") / "Output"

start_date = "01-01-2025"

item_data = user.get_items()
json.dump(
    item_data.json(), (torn_data_folder / "items.json").open("w", encoding="utf-8")
)

col_date = dt.datetime.strptime(start_date, "%d-%m-%Y")
error_count = 0
while col_date.date() <= dt.datetime.today().date():
    print(f"Errors: {error_count}")
    file_name = f"travel_log_{col_date.strftime('%d-%m-%Y')}.json"
    if error_count > 5:
        print("Greater than 5")
        break
    if not (travel_folder / file_name).exists():
        print(f"starting: {col_date.strftime('%d-%m-%Y')}")
        print("Does not exist")
        data = user2.get_travel_log(col_date)
        if "error" in data.json().keys():
            print(f"There is an error in  {file_name}")
            time.sleep(10)
            error_count = error_count + 1
        else:
            json.dump(
                data.json(), (travel_folder / file_name).open("w", encoding="utf-8")
            )
            error_count = 0
            col_date = col_date + dt.timedelta(days=1)
    else:
        col_date = col_date + dt.timedelta(days=1)

col_date = dt.datetime.strptime(start_date, "%d-%m-%Y")

travel_fin = pd.DataFrame()
purchase_fin = pd.DataFrame()
hunt_fin = pd.DataFrame()
rehab_fin = pd.DataFrame()

while col_date.date() <= (dt.datetime.today().date() - dt.timedelta(days=1)):
    file_name = f"travel_log_{col_date.strftime('%d-%m-%Y')}.json"
    json_data = json.load((travel_folder / file_name).open("r", encoding="utf-8"))
    if "error" in json_data.keys():
        raise Exception(f"There is an error in  {file_name}")
        break
    travel, purchase, hunt, rehab = data_clean.travel_data_clean(json_data["log"])

    travel_fin = pd.concat([travel_fin, pd.DataFrame(travel)], ignore_index=True)
    purchase_fin = pd.concat([purchase_fin, pd.DataFrame(purchase)], ignore_index=True)
    hunt_fin = pd.concat([hunt_fin, pd.DataFrame(hunt)], ignore_index=True)
    rehab_fin = pd.concat([rehab_fin, pd.DataFrame(rehab)], ignore_index=True)

    col_date = col_date + dt.timedelta(days=1)

print(travel_fin)
print(rehab_fin["timestamp_conv"])

print(purchase_fin.columns)

col_list = ["timestamp_conv", "item", "quantity", "cost_each", "cost_total"]

item_df = pd.DataFrame(data_clean.item_data_clean(item_data.json()))

item_df.to_csv((output_folder / "item_data.csv"), index=False)

report = purchase_fin[col_list]

report = report.merge(item_df[["id", "name"]], left_on="item", right_on="id")
report.loc[:, "source"] = "Travel"

report.drop(["item"], axis=1, inplace=True)

report = report[
    ["timestamp_conv", "name", "quantity", "cost_each", "cost_total", "source"]
]

col_names = {
    "timestamp_conv": "Date",
    "name": "Item",
    "quantity": "Quantity",
    "cost_each": "Price",
    "cost_total": "Total cost",
    "source": "Source",
}

report.rename(col_names, axis=1, inplace=True)

report.to_csv((output_folder / "purchase_report.csv"), index=False)


start_date = "01-01-2025"
col_date = dt.datetime.strptime(start_date, "%d-%m-%Y")

error_count = 0
while col_date.date() <= (dt.datetime.today() - dt.timedelta(days=1)).date():
    print(col_date.strftime("%d-%m-%Y"))
    file_name = f"item_market_log_{col_date.strftime('%d-%m-%Y')}.json"
    if error_count > 5:
        print(error_count)
        print("Greater than 5")
        break
    if not (item_market_data_folder / file_name).exists():
        item_market_input = user2.get_item_market_log(col_date).json()
        if "error" in item_market_input.keys():
            print(f"There is an error in  {file_name}")
            time.sleep(10)
            error_count = error_count + 1
        else:
            json.dump(
                item_market_input,
                (item_market_data_folder / file_name).open("w", encoding="utf-8"),
            )
            error_count = 0
            col_date = col_date + dt.timedelta(days=1)
    else:
        error_count = 0
        col_date = col_date + dt.timedelta(days=1)

# data_clean.item_market_data_clean(item_market_input["log"])

col_date = dt.datetime.strptime(start_date, "%d-%m-%Y")

item_sale_df = pd.DataFrame()
item_purchase_df = pd.DataFrame()

while col_date.date() <= (dt.datetime.today() - dt.timedelta(days=1)).date():
    print(col_date.strftime("%d-%m-%Y"))
    file_name = f"item_market_log_{col_date.strftime('%d-%m-%Y')}.json"
    item_market_data = json.load((item_market_data_folder / file_name).open())
    print(item_market_data)
    item_sale, item_purchase, item_add = data_clean.item_market_data_clean(
        item_market_data["log"]
    )

    item_sale_df = pd.concat([item_sale_df, pd.DataFrame(item_sale)], ignore_index=True)
    item_purchase_df = pd.concat(
        [item_purchase_df, pd.DataFrame(item_purchase)], ignore_index=True
    )
    col_date = col_date + dt.timedelta(days=1)

    pass


item_sale_df.to_csv((output_folder / "item_sale_data.csv"), index=False)
item_purchase_df.to_csv((output_folder / "item_market_purchase_data.csv"), index=False)

rep_im = item_purchase_df[
    ["timestamp_conv", "ItemID", "quantity", "cost_each", "cost_total"]
]

rep_im = rep_im.merge(item_df[["id", "name"]], left_on="ItemID", right_on="id")

rep_im = rep_im[["timestamp_conv", "name", "quantity", "cost_each", "cost_total"]]

rep_im.rename(col_names, axis=1, inplace=True)
rep_im["Source"] = "Torn Item Market"

final_purchase_report = pd.concat([rep_im, report], ignore_index=True)

final_purchase_report.sort_values("Date").to_csv(
    output_folder / "purchase_report.csv", index=False
)

col_date = dt.datetime.strptime(start_date, "%d-%m-%Y")
