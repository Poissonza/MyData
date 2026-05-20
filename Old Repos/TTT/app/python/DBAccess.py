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
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    Time,
    text,
    func,
)
from tqdm import tqdm
import os


class DBAccess:
    def __init__(
        self,
        videodata="data/videodata.json",
        rounddata="data/rounddata.json",
        playerdata="data/players.json",
        roledata="data/role.json",
        playdata="data/playdata.json",
        winchartdata="data/WinnerChartColours.json",
    ):
        self.engine = create_engine(
            f'postgresql://{os.environ.get("db_user")}:{os.environ.get("db_pass")}@{os.environ.get("db_databaseserver")}:5432/{os.environ.get("db_database")}',
            echo=False,
        )
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

        self.videodata = videodata
        self.rounddata = rounddata
        self.playersdata = playerdata
        self.roledata = roledata
        self.playdata = playdata
        self.winchartdata = winchartdata

    def update_tables(self):
        self.fill_video(self.videodata)
        self.fill_win_chart(self.winchartdata)
        self.fill_round(self.rounddata)
        self.fill_player(self.playersdata)
        self.fill_role(self.roledata)
        self.fill_play(self.playdata)

    def getVideos(self):
        results = self.conn.execute(select(self.video))
        print(pd.DataFrame(results.fetchall()))

    def checkVideo(self, videoid):
        s = select(self.video).where(self.video.c.id == videoid)
        result = self.conn.execute(s).fetchone()
        return result

    def fill_video(self, datafile):
        json_location = pathlib.Path(datafile)
        if not json_location.is_file():
            raise ValueError("Could not find the file")
        data = json.loads(json_location.read_bytes())
        count = 0
        for entry in tqdm(data, desc="video"):
            if self.checkVideo(entry["id"]) is None:
                self.insertVideo(entry)
                count += 1
        print(f"Inserted {count} Videos")

    def insertVideo(self, video_data):
        ins = self.video.insert()
        if "date" in video_data.keys():
            split_string = video_data["date"].split("/")
            date = datetime.date(
                int(split_string[0]), int(split_string[1]), int(split_string[2])
            )
            video_data["date"] = date
        if "video_play_time" in video_data.keys():
            str_split = video_data["video_play_time"].split(":")
            time = datetime.time(
                int(str_split[0]), int(str_split[1]), int(str_split[2])
            )
            video_data["video_play_time"] = time

        self.conn.execute(ins, video_data)

    def fill_round(self, round_data):
        json_location = pathlib.Path(round_data)
        if not json_location.is_file():
            raise ValueError("could not find Round File")
        round_data = json.loads(json_location.read_bytes())
        count = 0
        for round in tqdm(round_data, desc="Rounds"):
            if self.get_round_id(round["round_number"], round["video_link"]) is None:
                if "time_stamp" in round:
                    time_split = round["time_stamp"].split(":")
                    round["time_stamp"] = datetime.time(
                        int(time_split[0]), int(time_split[1]), int(time_split[2])
                    )
                self.insert_round(round)
                count += 1
        print(f"Inserted {count} rounds")

    def insert_round(self, round_data):
        ins = self.round.insert()
        self.conn.execute(ins, round_data)

    def get_round_id(self, round_number, video_id):
        s = select(self.round.c.id).where(
            self.round.c.round_number == round_number,
            self.round.c.video_link == video_id,
        )
        result = self.conn.execute(s).fetchone()
        return result

    def check_player(self, player_name):
        s = select(self.player.c.id).where(self.player.c.name == player_name)
        result = self.conn.execute(s).fetchone()
        return result

    def fill_player(self, player_data):
        player_file = pathlib.Path(player_data)
        if not player_file.is_file():
            raise ValueError("The Player file does not exist")
        data = json.loads(player_file.read_bytes())
        count = 0
        for player in tqdm(data, desc="Players"):
            player_id = self.check_player(player["name"])
            if player_id is None:
                self.player_lookup.update({player["name"]: self.insert_player(player)})
                count += 1
            else:
                self.player_lookup.update({player["name"]: player_id[0]})
        print(f"Inserted {count} Players")

    def insert_player(self, player_data):
        ins = self.player.insert()
        result = self.conn.engine.execute(ins, player_data)
        return result.inserted_primary_key[0]

    def fill_role(self, role_data):
        json_file_location = pathlib.Path(role_data)
        if not json_file_location.is_file():
            raise ValueError("The Role File does not exist")
        data = json.loads(json_file_location.read_bytes())
        count = 0
        for role in tqdm(data, desc="Roles"):
            role_id = self.check_role(role["name"])
            if role_id is None:
                self.role_lookup.update({role["name"]: self.insert_role(role)})
                count += 1
            else:
                self.role_lookup.update({role["name"]: role_id[0]})
        print(f"Inserted {count} Roles")

    def insert_role(self, role_data):
        ins = self.role.insert()
        result = self.conn.execute(ins, role_data)
        return result.inserted_primary_key[0]

    def check_role(self, role_name):
        s = select(self.role.c.id).where(self.role.c.name == role_name)
        result = self.conn.execute(s).fetchone()
        return result

    def fill_play(self, play_data):
        json_file_location = pathlib.Path(play_data)
        if not json_file_location.is_file():
            raise ValueError("Could not find the play file")
        data = json.loads(json_file_location.read_bytes())
        count = 0
        for play in tqdm(data, "Plays"):
            round_id = self.get_round_id(
                play["round_id"]["round_number"], play["round_id"]["video_id"]
            )[0]
            for player in play["role_link"]:
                player_link = self.player_lookup[player]
                role_link = self.role_lookup[play["role_link"][player]]
                if self.check_play(round_id, player_link, role_link) is None:
                    self.insert_play(player_link, round_id, role_link)
                    count += 1
        print(f"Inserted {count} role links")

    def insert_play(self, player_link, round_link, role_link):
        ins = self.play.insert()
        insert_dict = {
            "player_link": player_link,
            "round_link": round_link,
            "role_link": role_link,
        }
        self.conn.execute(ins, insert_dict)

    def check_play(self, round, player, role):
        s = select(self.play).where(
            self.play.c.round_link == round,
            self.play.c.player_link == player,
            self.play.c.role_link == role,
        )
        result = self.conn.execute(s)
        return result.fetchone()

    def get_data(self):
        s = (
            select(self.player.c.name, self.role.c.name)
            .select_from(self.player)
            .join(self.play)
            .join(self.role)
        )
        result = self.conn.execute(s).fetchall()
        print(result)

    def fill_win_chart(self, chart_data):
        json_file = pathlib.Path(chart_data)
        if not json_file.is_file():
            raise ValueError("Chart Details file does not exist")
        data = json.loads(json_file.read_bytes())
        count = 0
        for detail in tqdm(data, desc="Detail"):
            if self.check_win_chart(detail["winner_id"]) is None:
                self.insert_win_chart(detail)
                count += 1
        print(f"Inserted {count} Win Chart Details")

    def insert_win_chart(self, win_chart_data):
        ins = self.winnerchartdetails.insert()
        self.conn.execute(ins, win_chart_data)

    def check_win_chart(self, winner_id):
        s = select(self.winnerchartdetails).where(
            self.winnerchartdetails.c.winner_id == winner_id
        )
        return self.conn.execute(s).fetchone()

    def team_win_ratio(self):
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
        result = self.conn.execute(s).fetchall()
        return pd.DataFrame(result, columns=["Count", "Team", "Colour", "Label"])

    def plot_teams(self, output_path):
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
        s = select(self.player_play_counts)
        return self.conn.execute(s).fetchall()

    def get_role_play_counts(self):
        s = select(self.role_play_counts)
        return self.conn.execute(s).fetchall()

    def close_conn(self):
        self.conn.close()
