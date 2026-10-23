import tabs
import streamlit as st

st.header("Endless Legend 2")
tab_ref = st.tabs(
    ["Reference Data"]
)

with tab_ref:
    tabs.reference_page()
