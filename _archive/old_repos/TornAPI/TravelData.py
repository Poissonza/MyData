from TornAPI.Torn import UserLog
from TornAPI.DataCleaning import DataCleaning

import pandas as pd
import datetime as dt
import json
import time

import pathlib

api_key = "###"

api_log = UserLog(api_key)
data_clean = DataCleaning()

start_date = "01-10-2018"

travel_folder = pathlib.Path("data") / "Travel"
travel_clean_folder = pathlib.Path("data") / "TravelClean"

col_date = dt.datetime.strptime(start_date, "%d-%m-%Y")
error_count = 0
while col_date.date() <= (dt.datetime.today().date() - dt.timedelta(days=1)):
    file_name = f"travel_log_{col_date.strftime('%d-%m-%Y')}.json"
    if error_count > 5:
        print("Greater than 5")
        break
    if not (travel_folder / file_name).exists():
        print(f"starting: {col_date.strftime('%d-%m-%Y')}")
        print("Does not exist")
        data = api_log.get_travel_log(col_date)
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
travel_fee_fin = pd.DataFrame()
fortune_teller_fin = pd.DataFrame()

while col_date.date() <= (dt.datetime.today().date() - dt.timedelta(days=1)):
    print(col_date.strftime("%d-%m-%Y"))
    file_name = f"travel_log_{col_date.strftime('%d-%m-%Y')}.json"
    json_data = json.load((travel_folder / file_name).open("r", encoding="utf-8"))
    if "error" in json_data.keys():
        raise Exception(f"There is an error in  {file_name}")
        break
    (
        travel,
        purchase,
        hunt,
        rehab,
        travelFee,
        fortuneTeller,
    ) = data_clean.travel_data_clean(json_data["log"])

    travel_fin = pd.concat([travel_fin, pd.DataFrame(travel)], ignore_index=True)
    purchase_fin = pd.concat([purchase_fin, pd.DataFrame(purchase)], ignore_index=True)
    hunt_fin = pd.concat([hunt_fin, pd.DataFrame(hunt)], ignore_index=True)
    rehab_fin = pd.concat([rehab_fin, pd.DataFrame(rehab)], ignore_index=True)
    travel_fee_fin = pd.concat(
        [travel_fee_fin, pd.DataFrame(travelFee)], ignore_index=True
    )
    fortune_teller_fin = pd.concat(
        [fortune_teller_fin, pd.DataFrame(fortuneTeller)], ignore_index=True
    )
    col_date = col_date + dt.timedelta(days=1)

travel_fin.to_csv(travel_clean_folder / "Travel.csv", index=False)
purchase_fin.to_csv(travel_clean_folder / "Purchase.csv", index=False)
hunt_fin.to_csv(travel_clean_folder / "Hunt.csv", index=False)
rehab_fin.to_csv(travel_clean_folder / "Rehab.csv", index=False)
travel_fee_fin.to_csv(travel_clean_folder / "TravelFee.csv", index=False)
