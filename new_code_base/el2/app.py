import tabs
import streamlit as st

st.header("Endless Legend 2")
tab_game, tab_ref, tab_faction = st.tabs(["New Game", "Reference Data", "Factions"])
# Reference data page
with tab_game:
    tabs.game_page()

with tab_ref:
    tabs.reference_page()

with tab_faction:
    tabs.faction_page()


