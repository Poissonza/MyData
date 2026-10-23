import tabs
import streamlit as st

st.header("Endless Legend 2")
tab_game, tab_ref, tab_faction, tab_test = st.tabs(
    ["New Game", "Reference Data", "Factions", "testing"]
)
# Reference data page
# with tab_game:
#     tabs.game_page()

# with tab_ref:
# tabs.reference_page()

# with tab_faction:
#     tabs.faction_page()

with tab_test:
    tabs.ref_page_v2()
