import tabs
import streamlit as st
from data import load_db
from pathlib import Path
from constants import TABLES

EL_2_DIR = Path(__file__).parent
REFERENCE_DIR = EL_2_DIR / "reference"
GAME_DIR = EL_2_DIR / "data"

st.header("Endless Legend 2")
tab_event, tab_ref = st.tabs(["Events", "Reference Data"])

db_data = load_db(GAME_DIR, TABLES)

with tab_ref:
    tabs.reference_page(data=db_data)


with tab_event:
    tabs.events_page(data=db_data)
