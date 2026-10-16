"""Blood on the Clocktower data entry — Streamlit app.

Run with:  streamlit run botc/app.py
"""

from copy import deepcopy
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

BOTC_DIR = Path(__file__).parent
GAMES_DIR = BOTC_DIR / "games"
REF_DIR = BOTC_DIR / "reference"


# ─── Data helpers ────────────────────────────────────────────────────────────

ALIGNMENTS = ["Townsfolk", "Outsider", "Minion", "Demon", "Traveller", "Fabled"]
GOOD_ALIGNMENTS = {"Townsfolk", "Outsider"}
EVIL_ALIGNMENTS = {"Minion", "Demon"}


@st.cache_data
def load_roles_full() -> list[dict]:
    with open(REF_DIR / "roles.yml") as f:
        return yaml.safe_load(f)["roles"]


@st.cache_data
def load_ref() -> tuple[list, list]:
    with open(REF_DIR / "players.yml") as f:
        players = yaml.safe_load(f)["players"]
    roles = [r["name"] for r in load_roles_full()]
    return players, roles


def save_players(players: list[str]) -> None:
    lines = [f"  - {p}" for p in sorted(players, key=str.lower)]
    with open(REF_DIR / "players.yml", "w") as f:
        f.write("players:\n" + "\n".join(lines) + "\n")
    load_ref.clear()


def save_roles(roles: list[dict]) -> None:
    # One block per role separated by blank lines, matching the hand-written file layout
    blocks = [
        yaml.dump([r], sort_keys=False, allow_unicode=True, width=1000).rstrip()
        for r in sorted(roles, key=lambda r: r["name"].lower())
    ]
    indented = ["\n".join(f"  {line}" for line in b.splitlines()) for b in blocks]
    with open(REF_DIR / "roles.yml", "w") as f:
        f.write("roles:\n" + "\n\n".join(indented) + "\n")
    load_roles_full.clear()
    load_ref.clear()


def flash(msg: str) -> None:
    """Queue a success message that survives st.rerun()."""
    st.session_state["_flash"] = msg


def show_flash() -> None:
    if msg := st.session_state.pop("_flash", None):
        st.success(msg)


def load_all_games() -> list[dict]:
    return [load_game(gid) for gid in list_game_ids()]


def player_team(player: dict, role_alignment: dict[str, str]) -> str | None:
    alignment = role_alignment.get(player.get("role") or "")
    if alignment in GOOD_ALIGNMENTS:
        return "Good"
    if alignment in EVIL_ALIGNMENTS:
        return "Evil"
    return None


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

show_flash()

tab_new, tab_day, tab_reveal, tab_games, tab_players, tab_roles = st.tabs(
    ["New Game", "Add Day", "Reveal", "Games", "Players", "Roles"]
)


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
        elif len({p["name"] for p in player_rows}) < len(player_rows):
            st.error("Each player can only appear once.")
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
                "days": [],
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
        night_kill = c1.selectbox("Night kill",  gp_blank, key=f"ad_nk_{sel_game}")
        execution  = c2.selectbox("Execution",   gp_blank, key=f"ad_ex_{sel_game}")

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
        for pi, player in enumerate(game_data_r["players"]):
            entry = deepcopy(player)
            current_role  = player.get("role", "")
            current_drunk = player.get("drunk_role", "")

            c1, c2, c3 = st.columns([2, 2, 2])
            c1.write(f"**{player['name']}** (pos {player['position']})")
            role = c2.selectbox(
                "Role",
                roles_blank,
                index=roles_blank.index(current_role) if current_role in roles_blank else 0,
                key=f"rev_{sel_game_r}_p{pi}_role",
            )
            if role:
                entry["role"] = role
            if role == "Drunk":
                drunk = c3.selectbox(
                    "Drunk thinks",
                    roles_blank,
                    index=roles_blank.index(current_drunk) if current_drunk in roles_blank else 0,
                    key=f"rev_{sel_game_r}_p{pi}_drunk",
                )
                if drunk:
                    entry["drunk_role"] = drunk
            updated_players.append(entry)

        # Night actions
        st.subheader("Night Actions")
        first_day = min((d["day"] for d in game_data_r["days"]), default=None)
        if first_day is None:
            st.info("No days recorded yet — use Add Day first to record bluffs / first-night info.")
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
                        key=f"rev_{sel_game_r}_d{day_num}_ma{j}_r",
                    )
                    player = c2.selectbox(
                        "Player",
                        gp_r_blank,
                        index=gp_r_blank.index(cur_player) if cur_player in gp_r_blank else 0,
                        key=f"rev_{sel_game_r}_d{day_num}_ma{j}_p",
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
                        key=f"rev_{sel_game_r}_d{day_num}_ta{j}_r",
                    )
                    player = c2.selectbox(
                        "Player",
                        gp_r_blank,
                        index=gp_r_blank.index(cur_player) if cur_player in gp_r_blank else 0,
                        key=f"rev_{sel_game_r}_d{day_num}_ta{j}_p",
                    )
                    updated["townsfolk_action"][j] = {
                        "role": none_if_empty(role),
                        "player": none_if_empty(player),
                    }

            if day_num == first_day:
                st.write(f"**Day {day_num} — Add reveal extra info (e.g. Imp bluffs)**")
                first_ei_key = f"rev_first_ei_n_{sel_game_r}"
                if first_ei_key not in st.session_state:
                    st.session_state[first_ei_key] = 0
                if st.button("+ Add entry", key="rev_first_ei_add"):
                    st.session_state[first_ei_key] += 1

                new_entries = []
                for k in range(st.session_state[first_ei_key]):
                    c1, c2 = st.columns([2, 4])
                    ei_role = c1.selectbox("Role", roles_blank, key=f"rev_{sel_game_r}_first_ei_{k}_r")
                    ei_info = c2.text_input("Info",             key=f"rev_{sel_game_r}_first_ei_{k}_i")
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
            key=f"rev_{sel_game_r}_outcome",
        )
        n_days = c2.number_input("Number of days", min_value=0, value=int(current_n_days), key=f"rev_{sel_game_r}_ndays")

        if st.button("Save Reveal", key="rev_save"):
            game_data_r["players"] = updated_players
            game_data_r["days"]    = updated_days
            game_data_r["result"]  = {
                "outcome":       none_if_empty(outcome),
                "number_of_days": int(n_days) if n_days else None,
            }
            save_game(sel_game_r, game_data_r)
            # Clear the new first-day rows so a second save doesn't append them again
            st.session_state[f"rev_first_ei_n_{sel_game_r}"] = 0
            flash(f"Reveal saved for {sel_game_r}")
            st.rerun()


# ─── Tab: Games ──────────────────────────────────────────────────────────────

with tab_games:
    st.header("Captured Games")

    all_games = load_all_games()
    if not all_games:
        st.warning("No games found.")
    else:
        role_alignment = {r["name"]: r["alignment"] for r in load_roles_full()}

        overview = pd.DataFrame([
            {
                "Video ID":  str(g["video"]["id"]),
                "Name":      g["video"].get("name"),
                "Date":      str(g["video"].get("date") or ""),
                "Length":    g["video"].get("length"),
                "Members":   bool(g["video"].get("members")),
                "Players":   len(g.get("players") or []),
                "Days":      (g.get("result") or {}).get("number_of_days"),
                "Outcome":   (g.get("result") or {}).get("outcome"),
            }
            for g in all_games
        ]).sort_values(["Date", "Video ID"], ascending=False)
        st.dataframe(overview, hide_index=True, width="stretch")

        # Summary statistics
        st.subheader("Summary")
        outcomes = overview["Outcome"].value_counts()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Games", len(overview))
        m2.metric("Good wins", int(outcomes.get("Good", 0)))
        m3.metric("Evil wins", int(outcomes.get("Evil", 0)))
        avg_days = overview["Days"].dropna().mean()
        m4.metric("Avg days", f"{avg_days:.1f}" if pd.notna(avg_days) else "—")

        appearances = pd.DataFrame([
            {
                "player":  p["name"],
                "role":    p.get("role"),
                "team":    player_team(p, role_alignment),
                "outcome": (g.get("result") or {}).get("outcome"),
            }
            for g in all_games
            for p in g.get("players") or []
        ])
        if not appearances.empty:
            appearances["won"] = appearances["team"].notna() & (appearances["team"] == appearances["outcome"])
            decided = appearances[appearances["outcome"].notna() & appearances["team"].notna()]

            c1, c2 = st.columns(2)
            player_stats = (
                appearances.groupby("player")
                .agg(Games=("player", "size"), Evil=("team", lambda s: (s == "Evil").sum()))
                .join(decided.groupby("player")["won"].agg(Wins="sum", Decided="size"))
                .fillna(0)
            )
            player_stats["Win %"] = (100 * player_stats["Wins"] / player_stats["Decided"].where(player_stats["Decided"] > 0)).round(0)
            player_stats = player_stats.drop(columns="Decided").astype({"Wins": int}).sort_values("Games", ascending=False)
            c1.write("**Players**")
            c1.dataframe(player_stats, width="stretch")

            role_stats = (
                appearances.dropna(subset=["role"])
                .groupby("role")
                .agg(Played=("role", "size"), Wins=("won", "sum"))
                .sort_values("Played", ascending=False)
            )
            role_stats.insert(0, "Alignment", role_stats.index.map(role_alignment))
            c2.write("**Roles**")
            c2.dataframe(role_stats, width="stretch")

        # Game detail
        st.subheader("Game Detail")
        games_by_id = {str(g["video"]["id"]): g for g in all_games}
        labels = {
            gid: f"{gid} — {g['video'].get('name') or 'Untitled'} ({g['video'].get('date') or 'no date'})"
            for gid, g in games_by_id.items()
        }
        sel_detail = st.selectbox("Game", list(labels), format_func=labels.get, key="gm_detail")
        g = games_by_id[sel_detail]
        video, result = g["video"], g.get("result") or {}

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Date", str(video.get("date") or "—"))
        c2.metric("Length", video.get("length") or "—")
        c3.metric("Outcome", result.get("outcome") or "—")
        c4.metric("Days", result.get("number_of_days") or "—")
        if video.get("members"):
            st.caption("Members-only video")

        players_df = pd.DataFrame([
            {
                "Position":   p.get("position"),
                "Name":       p["name"],
                "Role":       p.get("role"),
                "Drunk role": p.get("drunk_role"),
                "Alignment":  role_alignment.get(p.get("role") or ""),
            }
            for p in g.get("players") or []
        ]).sort_values("Position")
        st.dataframe(players_df, hide_index=True, width="stretch")

        for day in g.get("days") or []:
            with st.expander(f"Day {day['day']}"):
                c1, c2 = st.columns(2)
                c1.write(f"**Night kill:** {day.get('night_kill') or '—'}")
                c2.write(f"**Execution:** {day.get('execution') or '—'}")
                extra = [e for e in day.get("extra_info") or [] if e.get("role") or e.get("info")]
                if extra:
                    st.write("**Extra info**")
                    st.dataframe(pd.DataFrame(extra), hide_index=True, width="stretch")
                if day.get("nominations"):
                    st.write("**Nominations**")
                    st.dataframe(pd.DataFrame(day["nominations"]), hide_index=True, width="stretch")
                for key, title in [("minion_action", "Minion actions"), ("townsfolk_action", "Townsfolk actions")]:
                    if day.get(key):
                        st.write(f"**{title}**")
                        st.dataframe(pd.DataFrame(day[key]), hide_index=True, width="stretch")


# ─── Tab: Players ────────────────────────────────────────────────────────────

with tab_players:
    st.header("Players")

    with st.form("pl_add", clear_on_submit=True):
        new_player = st.text_input("New player name")
        submitted = st.form_submit_button("Add Player")
    if submitted:
        name = new_player.strip()
        if not name:
            st.error("Player name is required.")
        elif name.lower() in {p.lower() for p in players_ref}:
            st.error(f"{name} already exists.")
        else:
            save_players(players_ref + [name])
            flash(f"Added player {name}")
            st.rerun()

    st.dataframe(pd.DataFrame({"Player": players_ref}), hide_index=True, width="stretch")


# ─── Tab: Roles ──────────────────────────────────────────────────────────────

with tab_roles:
    st.header("Roles")

    roles_full = load_roles_full()
    existing_sets = sorted({r["set"] for r in roles_full if r.get("set")})

    with st.form("rl_add", clear_on_submit=True):
        c1, c2 = st.columns(2)
        r_name      = c1.text_input("Role name")
        r_alignment = c2.selectbox("Alignment", ALIGNMENTS)
        r_set       = c1.selectbox("Set", existing_sets + ["Other…"])
        r_set_new   = c2.text_input("New set name (if Other…)")
        r_desc      = st.text_area("Description")
        submitted_r = st.form_submit_button("Add Role")
    if submitted_r:
        name = r_name.strip()
        set_name = r_set_new.strip() if r_set == "Other…" else r_set
        if not name:
            st.error("Role name is required.")
        elif name.lower() in {r["name"].lower() for r in roles_full}:
            st.error(f"{name} already exists.")
        elif not set_name:
            st.error("Enter a set name.")
        else:
            save_roles(roles_full + [{
                "name":        name,
                "alignment":   r_alignment,
                "set":         set_name,
                "description": r_desc.strip() or None,
            }])
            flash(f"Added role {name}")
            st.rerun()

    st.dataframe(
        pd.DataFrame(roles_full).rename(columns=str.title),
        hide_index=True,
        width="stretch",
    )
