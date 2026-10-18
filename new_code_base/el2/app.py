import tabs
import streamlit as st

st.header("Endless Legend 2")
tab_ref, tab_faction = st.tabs(["Reference Data", "Factions"])
# Reference data page
with tab_ref:
    tabs.reference_page()

with tab_faction:
    tabs.faction_page()


