import datetime
import json
import pathlib

import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import (
    create_engine,
    Table,
    MetaData,
    select,
    func,
)
from tqdm import tqdm

from app.config import Config


class DBAccess:
    DATA_DIR = pathlib.Path(__file__).parent / "data"

    def __init__(
        self,
        videodata: str = None,
        rounddata: str = None,
        playerdata: str = None,
        roledata: str = None,
        playdata: str = None,
        winchartdata: str = None,
    ):
        self.engine = create_engine(Config.db_url(), echo=False)
        self.metadata = MetaData()

        self.video = Table(
            "video", self.metadata, autoload_with=self.engine, schema="ttt"
        )
        self.round = Table(
            "round", self.metadata, autoload_with=self.engine, schema="ttt"
        )
        self.player = Table(
            "player", self.metadata, autoload_with=self.engine, schema="ttt"
        )
        self.role = Table(
            "role", self.metadata, autoload_with=self.engine, schema="ttt"
        )
        self.play = Table(
            "play", self.metadata, autoload_with=self.engine, schema="ttt"
        )
        self.winnerchartdetails = Table(
            "winnerchartdetails", self.metadata, autoload_with=self.engine, schema="ttt"
        )
        self.player_play_counts = Table(
            "player_play_counts", self.metadata, autoload_with=self.engine, schema="ttt"
        )
        self.role_play_counts = Table(
            "role_play_counts", self.metadata, autoload_with=self.engine, schema="ttt"
        )

        self.conn = self.engine.connect()
        self.player_lookup = {}
        self.role_lookup = {}

        self.videodata = videodata or str(self.DATA_DIR / "videodata.json")
        self.rounddata = rounddata or str(self.DATA_DIR / "rounddata.json")
        self.playersdata = playerdata or str(self.DATA_DIR / "players.json")
        self.roledata = roledata or str(self.DATA_DIR / "role.json")
        self.playdata = playdata or str(self.DATA_DIR / "playdata.json")
        self.winchartdata = winchartdata or str(
            self.DATA_DIR / "WinnerChartColours.json"
        )

    def update_tables(self) -> None:
        self.fill_video(self.videodata)
        self.fill_win_chart(self.winchartdata)
        self.fill_round(self.rounddata)
        self.fill_player(self.playersdata)
        self.fill_role(self.roledata)
        self.fill_play(self.playdata)

    def get_videos(self) -> pd.DataFrame:
        return pd.DataFrame(self.conn.execute(select(self.video)).fetchall())

    def check_video(self, video_id):
        s = select(self.video).where(self.video.c.id == video_id)
        return self.conn.execute(s).fetchone()

    def fill_video(self, datafile: str) -> None:
        data = json.loads(pathlib.Path(datafile).read_bytes())
        count = 0
        for entry in tqdm(data, desc="video"):
            if self.check_video(entry["id"]) is None:
                self._insert_video(entry)
                count += 1
        print(f"Inserted {count} Videos")

    def _insert_video(self, video_data: dict) -> None:
        if "date" in video_data:
            parts = video_data["date"].split("/")
            video_data["date"] = datetime.date(
                int(parts[0]), int(parts[1]), int(parts[2])
            )
        if "video_play_time" in video_data:
            parts = video_data["video_play_time"].split(":")
            video_data["video_play_time"] = datetime.time(
                int(parts[0]), int(parts[1]), int(parts[2])
            )
        self.conn.execute(self.video.insert(), video_data)

    def fill_round(self, round_data: str) -> None:
        data = json.loads(pathlib.Path(round_data).read_bytes())
        count = 0
        for rnd in tqdm(data, desc="Rounds"):
            if self.get_round_id(rnd["round_number"], rnd["video_link"]) is None:
                if "time_stamp" in rnd:
                    parts = rnd["time_stamp"].split(":")
                    rnd["time_stamp"] = datetime.time(
                        int(parts[0]), int(parts[1]), int(parts[2])
                    )
                self.conn.execute(self.round.insert(), rnd)
                count += 1
        print(f"Inserted {count} rounds")

    def get_round_id(self, round_number, video_id):
        s = select(self.round.c.id).where(
            self.round.c.round_number == round_number,
            self.round.c.video_link == video_id,
        )
        return self.conn.execute(s).fetchone()

    def check_player(self, player_name: str):
        s = select(self.player.c.id).where(self.player.c.name == player_name)
        return self.conn.execute(s).fetchone()

    def fill_player(self, player_data: str) -> None:
        data = json.loads(pathlib.Path(player_data).read_bytes())
        count = 0
        for player in tqdm(data, desc="Players"):
            player_id = self.check_player(player["name"])
            if player_id is None:
                result = self.conn.execute(self.player.insert(), player)
                self.player_lookup[player["name"]] = result.inserted_primary_key[0]
                count += 1
            else:
                self.player_lookup[player["name"]] = player_id[0]
        print(f"Inserted {count} Players")

    def check_role(self, role_name: str):
        s = select(self.role.c.id).where(self.role.c.name == role_name)
        return self.conn.execute(s).fetchone()

    def fill_role(self, role_data: str) -> None:
        data = json.loads(pathlib.Path(role_data).read_bytes())
        count = 0
        for role in tqdm(data, desc="Roles"):
            role_id = self.check_role(role["name"])
            if role_id is None:
                result = self.conn.execute(self.role.insert(), role)
                self.role_lookup[role["name"]] = result.inserted_primary_key[0]
                count += 1
            else:
                self.role_lookup[role["name"]] = role_id[0]
        print(f"Inserted {count} Roles")

    def fill_play(self, play_data: str) -> None:
        data = json.loads(pathlib.Path(play_data).read_bytes())
        count = 0
        for play in tqdm(data, "Plays"):
            round_id = self.get_round_id(
                play["round_id"]["round_number"], play["round_id"]["video_id"]
            )[0]
            for player, role_name in play["role_link"].items():
                player_link = self.player_lookup[player]
                role_link = self.role_lookup[role_name]
                if self.check_play(round_id, player_link, role_link) is None:
                    self.conn.execute(
                        self.play.insert(),
                        {
                            "player_link": player_link,
                            "round_link": round_id,
                            "role_link": role_link,
                        },
                    )
                    count += 1
        print(f"Inserted {count} role links")

    def check_play(self, round_id, player_id, role_id):
        s = select(self.play).where(
            self.play.c.round_link == round_id,
            self.play.c.player_link == player_id,
            self.play.c.role_link == role_id,
        )
        return self.conn.execute(s).fetchone()

    def fill_win_chart(self, chart_data: str) -> None:
        data = json.loads(pathlib.Path(chart_data).read_bytes())
        count = 0
        for detail in tqdm(data, desc="Detail"):
            if self.check_win_chart(detail["winner_id"]) is None:
                self.conn.execute(self.winnerchartdetails.insert(), detail)
                count += 1
        print(f"Inserted {count} Win Chart Details")

    def check_win_chart(self, winner_id):
        s = select(self.winnerchartdetails).where(
            self.winnerchartdetails.c.winner_id == winner_id
        )
        return self.conn.execute(s).fetchone()

    def team_win_ratio(self) -> pd.DataFrame:
        s = (
            select(
                func.count(self.round.c.id).label("Count"),
                self.round.c.winner,
                self.winnerchartdetails.c.colour,
                self.winnerchartdetails.c.label,
            )
            .select_from(self.round)
            .join(self.video)
            .join(self.winnerchartdetails)
            .group_by(
                self.round.c.winner,
                self.winnerchartdetails.c.colour,
                self.winnerchartdetails.c.label,
            )
            .where(self.video.c.server_type == 1)
        )
        return pd.DataFrame(
            self.conn.execute(s).fetchall(),
            columns=["Count", "Team", "Colour", "Label"],
        )

    def plot_teams(self, output_path: str) -> None:
        data = self.team_win_ratio()
        data_small = data[data["Count"] < 50]
        data = data[data["Count"] >= 50]
        data = pd.concat(
            [
                data,
                pd.DataFrame(
                    {
                        "Count": data_small["Count"].sum(),
                        "Team": "Other",
                        "Colour": "darkblue",
                        "Label": "Other",
                    },
                    index=[0],
                ),
            ],
            ignore_index=True,
        )
        plt.figure(figsize=(10, 10), dpi=500)
        plt.pie(
            data["Count"],
            labels=(data["Label"] + " (" + data["Count"].astype(str) + ")"),
            autopct="%1.1f%%",
            colors=data["Colour"],
            textprops={"color": "w"},
        )
        plt.legend(loc=8, ncol=4)
        plt.annotate("Number of rounds: " + str(data["Count"].sum()), xy=(1, 1))
        plt.title("Win Rate between the teams")
        plt.savefig(output_path, dpi=500)

    def get_player_play_counts(self):
        return self.conn.execute(select(self.player_play_counts)).fetchall()

    def get_role_play_counts(self):
        return self.conn.execute(select(self.role_play_counts)).fetchall()

    def close_conn(self) -> None:
        self.conn.close()
