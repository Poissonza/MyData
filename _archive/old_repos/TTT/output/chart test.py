import pandas as pd
import matplotlib.pyplot as plt

ignore_list = ["Traitor", "Innocent", "Detective"]

data = pd.read_csv("role_play_counts.csv")

data["date"] = pd.to_datetime(data["date"])

plt.figure(figsize=(10, 15))
for role in set(data["role"]):
    if role in ignore_list:
        print("ignore")
    else:
        plt_data = data[data["role"] == role]
        plt_data = plt_data.drop("role", axis=1)
        plt_data = plt_data.resample("M", on="date").sum()
        plt_data["cum_sum"] = plt_data.cumsum()
        if max(plt_data["cum_sum"] > 200):
            plt.plot(
                plt_data.index,
                plt_data["cum_sum"],
                label=f"{role} ({max(plt_data['cum_sum'])})",
            )
plt.legend()
plt.savefig("test.jpg")
