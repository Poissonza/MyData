from pathlib import Path
import streamlit as st
import constants
from data import store_table, validate, Col


EL_2_DIR = Path(__file__).parent
REFERENCE_DIR = EL_2_DIR / "reference"
GAME_DIR = EL_2_DIR / "data"


def events_page(data: dict):
    tab_creation("The list of events", data["events"], "events")


def reference_page(data: dict):
    tab_names = [tab.name for tab in constants.REFERENCE_TABS]
    ref_tab = st.tabs(tab_names)

    ref_num_tabs = len(ref_tab)

    for i in range(ref_num_tabs):
        with ref_tab[i]:
            tab_creation(
                constants.REFERENCE_TABS[i].caption,
                data[constants.REFERENCE_TABS[i].data_name],
                constants.REFERENCE_TABS[i].data_name,
            )


def tab_creation(caption: str, data: list[dict], form_key: str) -> None:
    st.caption(caption)
    input_forms(form_key, data)
    st.table(data)


def input_field(col: Col):
    if col.type == "int":
        return st.number_input(label=col.label, value=None)
    elif col.type == "bool":
        return st.checkbox(label=col.label)
    elif col.type == "choice":
        if col.label is not None:
            return st.selectbox(label=col.label, options=col.choices)
        else:
            st.error("Errors in the choice matrix")
    else:
        return st.text_input(label=col.label, value=None)


def input_forms(form_key: str, data: list[dict]):
    cols = [c for c in constants.TABLES[form_key] if c.name != "id"]

    short_cols = [c for c in cols if c.type != "long_text"]
    long_cols = [c for c in cols if c.type == "long_text"]

    num_cols = len(short_cols)

    with st.form(key=f"f_{form_key}", clear_on_submit=True):
        values = {"id": len(data) + 1}
        f_cols = st.columns(min(3, num_cols))
        for i, c in enumerate(short_cols):
            with f_cols[i % len(f_cols)]:
                values[c.name] = input_field(c)
        for c in long_cols:
            values[c.name] = input_field(c)
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            data_check = validate(data, cols, values)
            if not data_check:
                data.append(values)
                store_table(GAME_DIR, data, form_key)
            else:
                for error in data_check:
                    st.error(error)
