from pathlib import Path
import streamlit as st
import yaml
import pandas as pd
import constants
from data import load_table


EL_2_DIR = Path(__file__).parent
REFERENCE_DIR = EL_2_DIR / "reference"
GAME_DIR = EL_2_DIR / "data"

REFERENCE_TABLE_1 = [
    {
        "c1_label": "Speed Options",
        "c1_data": "speed",
        "c1_data_type": "df",
        "c2_label": "Difficulty",
        "c2_data": "difficulty",
        "c2_data_type": "df"
    },
    {
        "c1_label": "Map options",
        "c1_data": "map",
        "c1_data_type": "df",
        "c2_label": "World Size",
        "c2_data": "world_size",
        "c2_data_type": "df"
    }
]

REFERENCE_TABLE_2 = [
    {
        "c1_label": "AI Simultaneous Turns",
        "c1_data": "ai_simultaneos_turns",
        "c1_data_type": "list",
        "c2_label": "Fortress Instant Resolve",
        "c2_data": "allow_fortress_instant_resolve",
        "c2_data_type": "list"
    },
    {
        "c1_label": "Force Instant Resolve",
        "c1_data": "force_instant_resolve",
        "c1_data_type": "list",
        "c2_label": "Peaceful Mode",
        "c2_data": "peaceful_mode",
        "c2_data_type": "list"
    },
    {
        "c1_label": "Initial Peace Duration",
        "c1_data": "initial_peace_duration",
        "c1_data_type": "list",
        "c2_label": "Pre Founding Scouting Bonus",
        "c2_data": "pre_founding_scouting_bonus",
        "c2_data_type": "list"
    },
    {
        "c1_label": "Allow Optional Events",
        "c1_data": "allow_optional_events",
        "c1_data_type": "list",
        "c2_label": "Score Victory",
        "c2_data": "score_victory",
        "c2_data_type": "list"
    },
    {
        "c1_label": "Conquest Victory",
        "c1_data": "conquest_victory",
        "c1_data_type": "list",
        "c2_label": "Worship Victory Path",
        "c2_data": "worship_victory_path",
        "c2_data_type": "list"
    },
    {
        "c1_label": "Impress Victory Path",
        "c1_data": "impress_victory_path",
        "c1_data_type": "list",
        "c2_label": "Master Victory Path",
        "c2_data": "master_victory_path",
        "c2_data_type": "list"
    }
]

def create_columns(col1: st.columns, col2, col_data, reference_data):
    for row in col_data:
        col1.subheader(row["c1_label"])
        if row["c1_data_type"] == "df":
            col1.dataframe(pd.DataFrame(reference_data[row["c1_data"]]), hide_index=True, width="stretch")
        else:
            col1.table(reference_data[row["c1_data"]])
        col2.subheader(row["c2_label"])
        if row["c2_data_type"] == "df":
            col2.dataframe(pd.DataFrame(reference_data[row["c2_data"]]), hide_index=True, width="stretch")
        else:
            col2.table(reference_data[row["c2_data"]])


# @st.cache_data
def load_ref_data():
    with open(REFERENCE_DIR / "reference.yml") as f:
        return yaml.safe_load(f)

def load_game_data():
    with open(GAME_DIR / "games.yml") as f:
        return yaml.safe_load(f)

def faction_page():
    ref_data = load_ref_data()
    st.title("Factions")

    st.dataframe(pd.DataFrame(ref_data["faction"]), hide_index=True, width="stretch")

def game_page():
    ref_data = load_ref_data()
    game_data = load_game_data()["games"]

    st.header("Add new Game")

    st.table(game_data)



def ref_page_v2():
    
    tab_names = [tab.name for tab in constants.REFERENCE_TABS]
    
    ref_tab = st.tabs(tab_names)    
    # ref_tab = st.tabs(["Speed"])

    ref_num_tabs = len(ref_tab)

    for i in range(ref_num_tabs):
        with ref_tab[i]:
            reference_tabs(constants.REFERENCE_TABS[i].caption, load_table(GAME_DIR, constants.REFERENCE_TABS[i].data_name))
    
    


def reference_page():
    ref_data = load_ref_data()
    # st.title("Reference Data")

    # c1, c2 = st.columns(2)

    # create_columns(c1, c2, REFERENCE_TABLE_1, ref_data)

    # c1.subheader("Speed Options")
    # c1.dataframe(pd.DataFrame(ref_data["speed"]), hide_index=True, width="stretch")
    #
    # c2.subheader("Difficulty")
    # c2.dataframe(pd.DataFrame(ref_data["difficulty"]), hide_index=True, width="stretch")
    #
    # c1.subheader("Map options")
    # c1.dataframe(pd.DataFrame(ref_data["map"]), hide_index=True, width="stretch")
    #
    # c2.subheader("World Size")
    # c2.dataframe(pd.DataFrame(ref_data["world_size"]), hide_index=True, width="stretch")

    # st.subheader("General Settings")
    # c3, c4 = st.columns(2)

    # create_columns(c3, c4, REFERENCE_TABLE_2, ref_data)
        
def reference_tabs(caption, data):
    st.caption(caption)
    st.table(data)