import tabs
import streamlit as st

st.header("Endless Legend 2")
tab_ref, tab_test = st.tabs(
    ["Reference Data", "testing"]
)

with tab_ref:
    tabs.reference_page()

# with tab_test:
#     tabs.ref_page_v2()