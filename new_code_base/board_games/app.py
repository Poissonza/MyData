"""Board game action tracker — Streamlit app.

Run with:  streamlit run board_games/app.py
"""

from pathlib import Path

import streamlit as st
import yaml

from storage import SessionStore, write_delta

BG_DIR = Path(__file__).parent
SESSIONS_DIR = BG_DIR / "sessions"
GAMES_REF_DIR = BG_DIR / "reference" / "games"
PLAYERS_REF = BG_DIR / "reference" / "players.yml"
DELTA_BASE = BG_DIR.parent / "data" / "delta" / "board_games"

store = SessionStore(SESSIONS_DIR)


def load_self() -> str:
    with open(PLAYERS_REF) as f:
        players = yaml.safe_load(f)["players"]
    return players[0] if players else "Adam"


@st.cache_data
def load_game_defs() -> dict[str, dict]:
    defs = {}
    for p in GAMES_REF_DIR.glob("*.yml"):
        with open(p) as f:
            data = yaml.safe_load(f)
            defs[data["game"]] = data
    return defs


def none_if_empty(val: str | None) -> str | None:
    return val if val else None


def _find_or_create_era(sdata: dict, era_number: int) -> dict:
    era_list = sdata.setdefault("eras", [])
    era_obj = next((e for e in era_list if e["era_number"] == era_number), None)
    if era_obj is None:
        era_obj = {"era_number": era_number, "actions": [], "end_of_era": {}}
        era_list.append(era_obj)
        era_list.sort(key=lambda e: e["era_number"])
    return era_obj


def _session_status(sdata: dict, max_eras: int) -> list[dict]:
    """Return a status row per era for display."""
    era_map = {e["era_number"]: e for e in sdata.get("eras", [])}
    rows = []
    for era_n in range(1, max_eras + 1):
        era = era_map.get(era_n)
        n_actions = len(era["actions"]) if era else 0
        eoe = era.get("end_of_era", {}) if era else {}
        rows.append({
            "era": era_n,
            "actions": n_actions,
            "category": eoe.get("category_scored", "—"),
            "eoe_recorded": bool(eoe.get("scores")),
        })
    result = sdata.get("result", {})
    return rows, bool(result.get("final_scores"))


# ─── Page setup ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="Board Game Tracker", layout="wide")
st.title("Board Game Tracker")

self_name = load_self()
game_defs = load_game_defs()

if not game_defs:
    st.error("No game definitions found in reference/games/")
    st.stop()

tab_new, tab_status, tab_action, tab_era, tab_final = st.tabs(
    ["New Session", "Status", "Log Actions", "End of Era", "Final Score"]
)


# ─── Tab: New Session ─────────────────────────────────────────────────────────

with tab_new:
    st.header("New Session")

    c1, c2 = st.columns(2)
    game_name = c1.selectbox("Game", list(game_defs.keys()), key="ns_game")
    game_def = game_defs[game_name]

    platform = c2.text_input("Platform (e.g. BGA, TTS, Physical)", key="ns_platform")
    date_str = c1.text_input("Date (YYYY-MM-DD)", key="ns_date")
    session_id = c2.text_input(
        "Session ID",
        value="",
        placeholder="e.g. 20260828_civolution_1",
        key="ns_id",
    )

    st.subheader("Players")
    n_players = st.number_input(
        "Number of players",
        min_value=game_def.get("min_players", 1),
        max_value=game_def.get("max_players", 4),
        value=game_def.get("min_players", 2),
        key="ns_n",
    )
    player_attrs = game_def.get("player_attributes", [])

    player_rows = []
    for i in range(int(n_players)):
        st.markdown(f"**Player {i + 1}**")
        cols = st.columns([3] + [2] * len(player_attrs))
        default_name = self_name if i == 0 else f"Player {i + 1}"
        p_name = cols[0].text_input("Name", value=default_name, key=f"ns_p{i}_name")
        entry: dict = {"name": p_name or default_name}
        for j, attr in enumerate(player_attrs):
            akey = f"ns_p{i}_attr_{attr['name']}"
            if attr["type"] == "choice":
                val = cols[j + 1].selectbox(
                    attr["label"], [""] + attr["options"], key=akey
                )
                entry[attr["name"]] = none_if_empty(val)
            else:
                val = cols[j + 1].text_input(attr["label"], key=akey)
                entry[attr["name"]] = none_if_empty(val)
        player_rows.append(entry)

    if st.button("Create Session", key="ns_save"):
        if not session_id:
            st.error("Session ID is required.")
        elif store.exists(session_id):
            st.error(f"Session {session_id!r} already exists.")
        else:
            data = {
                "session_id": session_id,
                "game": game_name,
                "platform": none_if_empty(platform),
                "date": none_if_empty(date_str),
                "players": player_rows,
                "eras": [],
                "result": {},
            }
            store.save(session_id, data)
            st.success(f"Created session {session_id!r}")


# ─── Tab: Status ──────────────────────────────────────────────────────────────

with tab_status:
    st.header("Session Status")
    st.caption("Overview of what has been recorded — useful when returning to an in-progress game.")

    sessions = store.list_sessions()
    if not sessions:
        st.info("No sessions yet.")
    else:
        sel_s = st.selectbox("Session", sessions, key="st_session")
        sdata_s = store.load(sel_s)
        gdef_s = game_defs.get(sdata_s["game"], {})
        max_eras_s = gdef_s.get("eras", 4)

        st.markdown(
            f"**Game:** {sdata_s['game']} &nbsp;|&nbsp; "
            f"**Platform:** {sdata_s.get('platform') or '—'} &nbsp;|&nbsp; "
            f"**Date:** {sdata_s.get('date') or '—'} &nbsp;|&nbsp; "
            f"**Players:** {', '.join(p['name'] for p in sdata_s.get('players', []))}"
        )
        st.divider()

        era_rows, final_done = _session_status(sdata_s, max_eras_s)
        for row in era_rows:
            eoe_icon = "✅" if row["eoe_recorded"] else "⏳"
            action_str = f"{row['actions']} action{'s' if row['actions'] != 1 else ''} logged"
            cat_str = f"Category: {row['category']}" if row["eoe_recorded"] else "End of era not recorded"
            st.markdown(
                f"**Era {row['era']}** — {action_str} &nbsp;|&nbsp; {eoe_icon} {cat_str}"
            )

        st.divider()
        final_icon = "✅" if final_done else "⏳"
        result = sdata_s.get("result", {})
        if final_done:
            scores_str = ", ".join(
                f"{p}: {s}" for p, s in result.get("final_scores", {}).items()
            )
            st.markdown(
                f"**Final score** {final_icon} — Winner: **{result.get('winner', '—')}** | {scores_str}"
            )
        else:
            st.markdown(f"**Final score** {final_icon} — Not yet recorded")


# ─── Tab: Log Actions ─────────────────────────────────────────────────────────

with tab_action:
    st.header("Log Actions")
    st.caption("Record turns during the Action Phase (Phase 4). You can add to any era at any time.")

    sessions = store.list_sessions()
    if not sessions:
        st.warning("No sessions found — create one first.")
        st.stop()

    sel = st.selectbox("Session", sessions, key="la_session")
    sdata = store.load(sel)
    gdef = game_defs.get(sdata["game"], {})
    sp = [p["name"] for p in sdata.get("players", [])]
    max_era = gdef.get("eras", 4)

    era_num = st.number_input(
        "Era", min_value=1, max_value=max_era, value=1, key=f"la_era_{sel}"
    )

    st.divider()

    existing_era = next(
        (e for e in sdata.get("eras", []) if e["era_number"] == int(era_num)), None
    )
    existing_actions = existing_era.get("actions", []) if existing_era else []

    if existing_actions:
        st.subheader(f"Era {int(era_num)} actions so far ({len(existing_actions)})")
        for idx, act in enumerate(existing_actions):
            if act["action_type"] == "reset":
                label = f"**{act['player']}** — Reset"
            elif act["action_type"] == "sleep":
                label = f"**{act['player']}** — Sleep module"
            elif act["action_type"] == "feature":
                label = f"**{act['player']}** — Feature: {act.get('module', '')}"
            else:
                choice_str = f" ({act.get('choice', '')})" if act.get("choice") else ""
                lvl = act.get("module_level", "")
                label = f"**{act['player']}** — {act.get('module', '')} Lvl {lvl}{choice_str}"
            if act.get("notes"):
                label += f" — *{act['notes']}*"
            st.markdown(f"{idx + 1}. {label}")
        st.divider()

    st.subheader("Add action")

    main_modules = gdef.get("main_modules", [])
    feature_modules = gdef.get("feature_modules", [])
    levels = gdef.get("module_levels", ["I", "II", "III"])
    choices = gdef.get("action_choices", ["A", "B", "Both A & B"])

    c1, c2 = st.columns(2)
    action_player = c1.selectbox("Player", [""] + sp, key=f"la_player_{sel}")
    action_type = c2.radio(
        "Action type",
        ["Module", "Reset", "Sleep", "Feature"],
        horizontal=True,
        key=f"la_type_{sel}",
    )

    module_name = None
    module_level = None
    choice = None

    if action_type == "Module":
        c1, c2, c3 = st.columns(3)
        module_name = c1.selectbox("Module", [""] + main_modules, key=f"la_mod_{sel}")
        module_level = c2.radio("Level", levels, horizontal=True, key=f"la_lvl_{sel}")
        choice = c3.radio("Choice", choices, horizontal=True, key=f"la_choice_{sel}")
    elif action_type == "Feature":
        module_name = st.selectbox(
            "Feature module", [""] + feature_modules, key=f"la_feat_{sel}"
        )

    notes = st.text_input("Notes (optional)", key=f"la_notes_{sel}")

    if st.button("Add Action", key="la_add"):
        if not action_player:
            st.error("Select a player.")
        else:
            entry: dict = {
                "player": action_player,
                "action_type": action_type.lower(),
                "module": none_if_empty(module_name),
                "module_level": module_level if action_type == "Module" else None,
                "choice": choice if action_type == "Module" else None,
                "notes": none_if_empty(notes),
            }
            era_obj = _find_or_create_era(sdata, int(era_num))
            era_obj["actions"].append(entry)
            store.save(sel, sdata)
            write_delta(sdata, DELTA_BASE)
            st.success(f"Action added for {action_player}")
            st.rerun()


# ─── Tab: End of Era ──────────────────────────────────────────────────────────

with tab_era:
    st.header("End of Era")
    st.caption(
        "Record the scoring category, scores, and resource snapshot. "
        "Can be saved independently of action logging — fill in what you have."
    )

    sessions = store.list_sessions()
    if not sessions:
        st.warning("No sessions found.")
        st.stop()

    sel_e = st.selectbox("Session", sessions, key="ee_session")
    sdata_e = store.load(sel_e)
    gdef_e = game_defs.get(sdata_e["game"], {})
    sp_e = [p["name"] for p in sdata_e.get("players", [])]
    scoring_cats = gdef_e.get("scoring_categories", [])
    max_era_e = gdef_e.get("eras", 4)

    era_num_e = st.selectbox(
        "Era", list(range(1, max_era_e + 1)), key=f"ee_era_{sel_e}"
    )

    era_obj_e = next(
        (e for e in sdata_e.get("eras", []) if e["era_number"] == era_num_e), None
    )
    existing_eoe = era_obj_e.get("end_of_era", {}) if era_obj_e else {}

    checkpoint_def = gdef_e.get("era_checkpoint", {})
    track_defs = checkpoint_def.get("progress_tracks", [])
    resource_defs = checkpoint_def.get("resources", [])

    st.subheader("Era scoring")
    cat_idx = (
        scoring_cats.index(existing_eoe.get("category_scored"))
        if existing_eoe.get("category_scored") in scoring_cats
        else 0
    )
    category_scored = st.selectbox(
        "Category scored this era", scoring_cats, index=cat_idx, key=f"ee_cat_{sel_e}"
    )

    st.subheader("Scores after this era")
    scores: dict = dict(existing_eoe.get("scores", {}))
    for p in sp_e:
        scores[p] = st.number_input(
            f"{p}", min_value=0, value=int(scores.get(p, 0)),
            key=f"ee_score_{sel_e}_{p}",
        )

    player_resources: dict = {}
    if track_defs or resource_defs:
        st.subheader("Player resources at end of era")
        existing_resources = existing_eoe.get("resources", {})

        for p in sp_e:
            st.markdown(f"**{p}**")
            p_existing = existing_resources.get(p, {})
            p_data: dict = {}

            if track_defs:
                track_cols = st.columns(len(track_defs))
                for col, td in zip(track_cols, track_defs):
                    p_data[td["name"]] = col.number_input(
                        td["label"],
                        min_value=0,
                        max_value=td.get("max", 12),
                        value=int(p_existing.get(td["name"], 0)),
                        key=f"ee_{sel_e}_{p}_{td['name']}",
                    )

            if resource_defs:
                res_cols = st.columns(len(resource_defs))
                for col, rd in zip(res_cols, resource_defs):
                    p_data[rd["name"]] = col.number_input(
                        rd["label"],
                        min_value=0,
                        value=int(p_existing.get(rd["name"], 0)),
                        key=f"ee_{sel_e}_{p}_{rd['name']}",
                    )

            player_resources[p] = p_data

    if st.button("Save End of Era", key="ee_save"):
        era_obj_e = _find_or_create_era(sdata_e, era_num_e)
        eoe: dict = {
            "category_scored": category_scored,
            "scores": scores,
        }
        if track_defs or resource_defs:
            eoe["resources"] = player_resources
        era_obj_e["end_of_era"] = eoe
        store.save(sel_e, sdata_e)
        st.success(f"Era {era_num_e} saved.")


# ─── Tab: Final Score ─────────────────────────────────────────────────────────

with tab_final:
    st.header("Final Score")

    sessions = store.list_sessions()
    if not sessions:
        st.warning("No sessions found.")
        st.stop()

    sel_f = st.selectbox("Session", sessions, key="fs_session")
    sdata_f = store.load(sel_f)
    sp_f = [p["name"] for p in sdata_f.get("players", [])]
    existing_result = sdata_f.get("result", {})

    st.subheader("Final scores")
    final_scores: dict = dict(existing_result.get("final_scores", {}))
    for p in sp_f:
        final_scores[p] = st.number_input(
            f"{p}", min_value=0, value=int(final_scores.get(p, 0)),
            key=f"fs_score_{sel_f}_{p}",
        )

    winner_idx = 0
    if existing_result.get("winner") in sp_f:
        winner_idx = sp_f.index(existing_result["winner"])
    winner = (
        st.selectbox("Winner", sp_f, index=winner_idx, key=f"fs_winner_{sel_f}")
        if sp_f
        else None
    )

    if st.button("Save Final Score", key="fs_save"):
        sdata_f["result"] = {
            "winner": winner,
            "final_scores": final_scores,
        }
        store.save(sel_f, sdata_f)
        write_delta(sdata_f, DELTA_BASE)
        st.success(f"Final score saved. Winner: {winner}")
