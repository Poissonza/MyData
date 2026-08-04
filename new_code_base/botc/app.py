"""Blood on the Clocktower data entry — Streamlit app.

Run with:  streamlit run botc/app.py
"""

from copy import deepcopy
from pathlib import Path

import streamlit as st
import yaml

BOTC_DIR = Path(__file__).parent
GAMES_DIR = BOTC_DIR / "games"
REF_DIR = BOTC_DIR / "reference"


# ─── Data helpers ────────────────────────────────────────────────────────────

@st.cache_data
def load_ref() -> tuple[list, list]:
    with open(REF_DIR / "players.yml") as f:
        players = yaml.safe_load(f)["players"]
    with open(REF_DIR / "roles.yml") as f:
        roles = [r["name"] for r in yaml.safe_load(f)["roles"]]
    return players, roles


def list_game_ids() -> list[str]:
    return sorted(p.stem for p in GAMES_DIR.glob("*.yml"))


def load_game(game_id: str) -> dict:
    with open(GAMES_DIR / f"{game_id}.yml") as f:
        return yaml.safe_load(f)


def save_game(game_id: str, data: dict) -> None:
    path = GAMES_DIR / f"{game_id}.yml"
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def none_if_empty(val: str) -> str | None:
    return val if val else None


def int_or_none(val: str) -> int | None:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


# ─── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="BotC Data Entry", layout="wide")
st.title("Blood on the Clocktower — Data Entry")

players_ref, roles_ref = load_ref()
roles_blank = [""] + roles_ref
players_blank = [""] + players_ref

tab_new, tab_day, tab_reveal = st.tabs(["New Game", "Add Day", "Reveal"])


# ─── Tab: New Game ────────────────────────────────────────────────────────────

with tab_new:
    st.header("New Game")

    c1, c2 = st.columns(2)
    video_id   = c1.text_input("Video ID", key="ng_id")
    video_name = c1.text_input("Video name", key="ng_name")
    video_date = c1.text_input("Date (YYYY-MM-DD)", key="ng_date")
    video_len  = c2.text_input("Length (HH:MM:SS)", key="ng_len")
    members    = c2.checkbox("Members only", key="ng_members")

    st.subheader("Players")
    n_players = st.number_input("Number of players", min_value=1, max_value=20, value=8, key="ng_n")

    player_rows = []
    for i in range(int(n_players)):
        cols = st.columns([3, 3, 1, 3])
        p_name  = cols[0].selectbox(f"Name {i+1}",     players_ref,  key=f"ng_p{i}_name")
        p_role  = cols[1].selectbox(f"Role {i+1}",     roles_blank,  key=f"ng_p{i}_role")
        p_pos   = cols[2].number_input(f"#{i+1}", min_value=1, max_value=20, value=i+1, key=f"ng_p{i}_pos")
        entry: dict = {"name": p_name, "position": int(p_pos)}
        if p_role:
            entry["role"] = p_role
        if p_role == "Drunk":
            p_drunk = cols[3].selectbox(f"Drunk thinks {i+1}", roles_blank, key=f"ng_p{i}_drunk")
            if p_drunk:
                entry["drunk_role"] = p_drunk
        player_rows.append(entry)

    if st.button("Create Game", key="ng_save"):
        if not video_id:
            st.error("Video ID is required.")
        elif (GAMES_DIR / f"{video_id}.yml").exists():
            st.error(f"Game {video_id} already exists.")
        else:
            data = {
                "video": {
                    "id": video_id,
                    "name": none_if_empty(video_name),
                    "date": none_if_empty(video_date),
                    "length": none_if_empty(video_len),
                    "members": members,
                },
                "result": {"outcome": None, "number_of_days": None},
                "players": player_rows,
                "days": [{"day": 0, "extra_info": [{"role": None, "info": None}]}],
            }
            save_game(video_id, data)
            st.success(f"Created games/{video_id}.yml")


# ─── Tab: Add Day ─────────────────────────────────────────────────────────────

with tab_day:
    st.header("Add Day")

    game_ids = list_game_ids()
    if not game_ids:
        st.warning("No games found — create one first.")
    else:
        sel_game = st.selectbox("Game", game_ids, key="ad_game")
        game_data = load_game(sel_game)
        gp = [p["name"] for p in game_data["players"]]
        gp_blank = [""] + gp

        # Auto-suggest next day number; key includes game name so it resets on game switch
        existing_days = [d["day"] for d in game_data["days"]]
        next_day = max(existing_days) + 1 if existing_days else 1
        day_num = st.number_input("Day number", min_value=1, value=next_day, key=f"ad_day_{sel_game}")

        c1, c2 = st.columns(2)
        night_kill = c1.selectbox("Night kill",  gp_blank, key="ad_nk")
        execution  = c2.selectbox("Execution",   gp_blank, key="ad_ex")

        # Extra info rows — key namespaced by game so row count resets on switch
        st.subheader("Extra Info")
        ei_key = f"ad_ei_n_{sel_game}"
        if ei_key not in st.session_state:
            st.session_state[ei_key] = 1
        if st.button("+ Extra info row", key="ad_ei_add"):
            st.session_state[ei_key] += 1

        extra_info = []
        for i in range(st.session_state[ei_key]):
            c1, c2 = st.columns([2, 4])
            ei_role = c1.selectbox("Role",  roles_blank, key=f"ad_ei{i}_r_{sel_game}")
            ei_info = c2.text_input("Info", key=f"ad_ei{i}_i_{sel_game}")
            if ei_role and ei_info:
                extra_info.append({"role": ei_role, "info": ei_info})

        # Nominations
        st.subheader("Nominations")
        nom_key = f"ad_nom_n_{sel_game}"
        if nom_key not in st.session_state:
            st.session_state[nom_key] = 1
        if st.button("+ Nomination row", key="ad_nom_add"):
            st.session_state[nom_key] += 1

        nominations = []
        for i in range(st.session_state[nom_key]):
            c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 1, 2])
            nom_nom  = c1.selectbox("Nominate",   gp_blank, key=f"ad_nom{i}_n_{sel_game}")
            nom_tor  = c2.selectbox("Nominator",  gp_blank, key=f"ad_nom{i}_t_{sel_game}")
            nom_v    = c3.text_input("Votes",                key=f"ad_nom{i}_v_{sel_game}")
            nom_gv   = c4.text_input("Ghost v.",             key=f"ad_nom{i}_gv_{sel_game}")
            nom_res  = c5.text_input("Result",               key=f"ad_nom{i}_r_{sel_game}")
            if nom_nom:
                nominations.append({
                    "nominate":    none_if_empty(nom_nom),
                    "nominator":   none_if_empty(nom_tor),
                    "votes":       int_or_none(nom_v),
                    "ghost_votes": int_or_none(nom_gv),
                    "result":      none_if_empty(nom_res),
                })

        # Minion actions
        st.subheader("Minion Actions")
        ma_key = f"ad_ma_n_{sel_game}"
        if ma_key not in st.session_state:
            st.session_state[ma_key] = 1
        if st.button("+ Minion action row", key="ad_ma_add"):
            st.session_state[ma_key] += 1

        minion_actions = []
        for i in range(st.session_state[ma_key]):
            c1, c2 = st.columns(2)
            ma_role   = c1.selectbox("Role",   roles_blank, key=f"ad_ma{i}_r_{sel_game}")
            ma_player = c2.selectbox("Player", gp_blank,    key=f"ad_ma{i}_p_{sel_game}")
            minion_actions.append({
                "role":   none_if_empty(ma_role),
                "player": none_if_empty(ma_player),
            })

        # Townsfolk actions
        st.subheader("Townsfolk Actions")
        ta_key = f"ad_ta_n_{sel_game}"
        if ta_key not in st.session_state:
            st.session_state[ta_key] = 1
        if st.button("+ Townsfolk action row", key="ad_ta_add"):
            st.session_state[ta_key] += 1

        townsfolk_actions = []
        for i in range(st.session_state[ta_key]):
            c1, c2 = st.columns(2)
            ta_role   = c1.selectbox("Role",   roles_blank, key=f"ad_ta{i}_r_{sel_game}")
            ta_player = c2.selectbox("Player", gp_blank,    key=f"ad_ta{i}_p_{sel_game}")
            townsfolk_actions.append({
                "role":   none_if_empty(ta_role),
                "player": none_if_empty(ta_player),
            })

        if st.button("Save Day", key="ad_save"):
            day_entry: dict = {
                "day":        int(day_num),
                "night_kill": none_if_empty(night_kill),
                "execution":  none_if_empty(execution),
            }
            if extra_info:
                day_entry["extra_info"] = extra_info
            if nominations:
                day_entry["nominations"] = nominations
            # Only write action sections if at least one row has a role filled in
            if any(a["role"] for a in minion_actions):
                day_entry["minion_action"] = minion_actions
            if any(a["role"] for a in townsfolk_actions):
                day_entry["townsfolk_action"] = townsfolk_actions

            game_data["days"].append(day_entry)
            save_game(sel_game, game_data)
            st.success(f"Day {int(day_num)} added to {sel_game}")


# ─── Tab: Reveal ─────────────────────────────────────────────────────────────

with tab_reveal:
    st.header("End of Game Reveal")

    game_ids = list_game_ids()
    if not game_ids:
        st.warning("No games found.")
    else:
        sel_game_r = st.selectbox("Game", game_ids, key="rev_game")
        game_data_r = load_game(sel_game_r)
        gp_r = [p["name"] for p in game_data_r["players"]]
        gp_r_blank = [""] + gp_r

        # Player roles
        st.subheader("Player Roles")
        updated_players = []
        for player in game_data_r["players"]:
            entry = deepcopy(player)
            current_role  = player.get("role", "")
            current_drunk = player.get("drunk_role", "")

            c1, c2, c3 = st.columns([2, 2, 2])
            c1.write(f"**{player['name']}** (pos {player['position']})")
            role = c2.selectbox(
                "Role",
                roles_blank,
                index=roles_blank.index(current_role) if current_role in roles_blank else 0,
                key=f"rev_{player['name']}_role",
            )
            if role:
                entry["role"] = role
            if role == "Drunk":
                drunk = c3.selectbox(
                    "Drunk thinks",
                    roles_blank,
                    index=roles_blank.index(current_drunk) if current_drunk in roles_blank else 0,
                    key=f"rev_{player['name']}_drunk",
                )
                if drunk:
                    entry["drunk_role"] = drunk
            updated_players.append(entry)

        # Night actions
        st.subheader("Night Actions")
        updated_days = []
        for day_entry in game_data_r["days"]:
            day_num = day_entry["day"]
            updated = deepcopy(day_entry)

            if "minion_action" in day_entry:
                st.write(f"**Day {day_num} — Minion Actions**")
                for j, action in enumerate(day_entry["minion_action"]):
                    cur_role   = action.get("role") or ""
                    cur_player = action.get("player") or ""
                    c1, c2 = st.columns(2)
                    role = c1.selectbox(
                        "Role",
                        roles_blank,
                        index=roles_blank.index(cur_role) if cur_role in roles_blank else 0,
                        key=f"rev_d{day_num}_ma{j}_r",
                    )
                    player = c2.selectbox(
                        "Player",
                        gp_r_blank,
                        index=gp_r_blank.index(cur_player) if cur_player in gp_r_blank else 0,
                        key=f"rev_d{day_num}_ma{j}_p",
                    )
                    updated["minion_action"][j] = {
                        "role": none_if_empty(role),
                        "player": none_if_empty(player),
                    }

            if "townsfolk_action" in day_entry:
                st.write(f"**Day {day_num} — Townsfolk Actions**")
                for j, action in enumerate(day_entry["townsfolk_action"]):
                    cur_role   = action.get("role") or ""
                    cur_player = action.get("player") or ""
                    c1, c2 = st.columns(2)
                    role = c1.selectbox(
                        "Role",
                        roles_blank,
                        index=roles_blank.index(cur_role) if cur_role in roles_blank else 0,
                        key=f"rev_d{day_num}_ta{j}_r",
                    )
                    player = c2.selectbox(
                        "Player",
                        gp_r_blank,
                        index=gp_r_blank.index(cur_player) if cur_player in gp_r_blank else 0,
                        key=f"rev_d{day_num}_ta{j}_p",
                    )
                    updated["townsfolk_action"][j] = {
                        "role": none_if_empty(role),
                        "player": none_if_empty(player),
                    }

            if day_num == 0:
                st.write("**Day 0 — Add reveal extra info (e.g. Imp bluffs)**")
                if "rev_ei0_n" not in st.session_state:
                    st.session_state.rev_ei0_n = 0
                if st.button("+ Add entry", key="rev_ei0_add"):
                    st.session_state.rev_ei0_n += 1

                new_entries = []
                for k in range(st.session_state.rev_ei0_n):
                    c1, c2 = st.columns([2, 4])
                    ei_role = c1.selectbox("Role", roles_blank, key=f"rev_ei0_{k}_r")
                    ei_info = c2.text_input("Info",             key=f"rev_ei0_{k}_i")
                    if ei_role and ei_info:
                        new_entries.append({"role": ei_role, "info": ei_info})
                if new_entries:
                    updated.setdefault("extra_info", []).extend(new_entries)

            updated_days.append(updated)

        # Result
        st.subheader("Result")
        current_outcome  = game_data_r.get("result", {}).get("outcome") or ""
        current_n_days   = game_data_r.get("result", {}).get("number_of_days") or 0
        outcomes_blank   = ["", "Good", "Evil"]
        c1, c2 = st.columns(2)
        outcome = c1.selectbox(
            "Outcome",
            outcomes_blank,
            index=outcomes_blank.index(current_outcome) if current_outcome in outcomes_blank else 0,
            key="rev_outcome",
        )
        n_days = c2.number_input("Number of days", min_value=0, value=int(current_n_days), key="rev_ndays")

        if st.button("Save Reveal", key="rev_save"):
            game_data_r["players"] = updated_players
            game_data_r["days"]    = updated_days
            game_data_r["result"]  = {
                "outcome":       none_if_empty(outcome),
                "number_of_days": int(n_days) if n_days else None,
            }
            save_game(sel_game_r, game_data_r)
            st.success(f"Reveal saved for {sel_game_r}")
