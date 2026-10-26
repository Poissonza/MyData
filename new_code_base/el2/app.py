import tabs
import streamlit as st

st.header("Endless Legend 2")
tab_event, tab_ref = st.tabs(["Events", "Reference Data"])

with tab_ref:
    tabs.reference_page()


with tab_event:
    tabs.events_page()