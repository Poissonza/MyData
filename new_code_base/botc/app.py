"""Blood on the Clocktower data entry — Streamlit app.

Reads and writes the relational tables in data/ (one YAML file per table).
Every row is added and saved on its own, so a game can be captured as it is
watched and completed later.

Run with:  uv run streamlit run botc/app.py
"""

import os
import re
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

DATA_DIR = Path(__file__).parent / "data"

TEAMS = ("Good", "Evil")
WIN_TEAMS = ("Good", "Evil", "Either")
CHARACTER_TYPES = ("Townsfolk", "Outsider", "Minion", "Demon", "Traveller", "Fabled")
DEFAULT_TEAM = {"Townsfolk": "Good", "Outsider": "Good", "Minion": "Evil", "Demon": "Evil"}
TIMINGS = ("Night", "Day")
CAUSE_TYPES = ("Demon", "Execution", "Ability", "Other")
# What a nomination result does to the block (who will be executed at the end of the day)
BLOCK_EFFECTS = ("marks", "clears", "none", "executes_nominator")


# ─── Table definitions ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class Col:
    name: str
    kind: str = "text"  # id | text | long_text | int | bool | choice | ref | date | duration
    ref: str | None = None
    choices: tuple = ()
    required: bool = False
    in_game: bool = False  # player/role ref limited to the players or roles in this game
    label: str | None = None

    @property
    def title(self) -> str:
        if self.label:
            return self.label
        if self.name == "id":
            return "ID"
        return self.name.removesuffix("_id").replace("_", " ").capitalize()


ID = Col("id", "id")

TABLES: dict[str, list[Col]] = {
    "players": [ID, Col("name", required=True)],
    "roles": [
        ID,
        Col("name", required=True),
        Col("character_type", "choice", choices=CHARACTER_TYPES, required=True),
        Col("alignment", "choice", choices=TEAMS, label="Default team"),
        Col("set"),
        Col("description", "long_text"),
    ],
    "nomination_results": [
        ID,
        Col("name", required=True),
        Col("block_effect", "choice", choices=BLOCK_EFFECTS, required=True),
    ],
    "win_conditions": [
        ID,
        Col("name", required=True),
        Col("winning_team", "choice", choices=WIN_TEAMS, required=True),
        Col("role_id", "ref", ref="roles"),
        Col("description", "long_text"),
    ],
    "videos": [
        ID,
        Col("name", required=True),
        Col("date", "date", required=True),
        Col("length", "duration"),
        Col("members", "bool", label="Members only"),
    ],
    "games": [
        ID,
        Col("game_number", "int", label="Game number in video"),
        Col("video_id", "ref", ref="videos", required=True),
    ],
    "game_players": [
        ID,
        Col("player_id", "ref", ref="players", required=True),
        Col("starting_role_id", "ref", ref="roles"),
        Col("game_id", "ref", ref="games", required=True),
        Col("seat", "int"),
        Col("believed_role_id", "ref", ref="roles", label="Believes they are"),
    ],
    "game_results": [
        ID,
        Col("game_id", "ref", ref="games", required=True),
        Col("winning_team", "choice", choices=TEAMS),
        Col("win_condition_id", "ref", ref="win_conditions", required=True),
    ],
    "deaths": [
        ID,
        Col("game_id", "ref", ref="games", required=True),
        Col("day", "int", required=True),
        Col("player_id", "ref", ref="players", in_game=True, required=True),
        Col("timing", "choice", choices=TIMINGS),
        Col("cause_type", "choice", choices=CAUSE_TYPES),
        Col("cause_role_id", "ref", ref="roles", in_game=True, label="Caused by role"),
    ],
    "nominations": [
        ID,
        Col("game_id", "ref", ref="games", required=True),
        Col("day", "int", required=True),
        Col("nominator_id", "ref", ref="players", in_game=True, required=True),
        Col("nominee_id", "ref", ref="players", in_game=True, required=True),
        Col("votes", "int"),
        Col("ghost_votes", "int"),
        Col("result_id", "ref", ref="nomination_results"),
    ],
    "night_actions": [
        ID,
        Col("game_id", "ref", ref="games", required=True),
        Col("day", "int", required=True),
        Col("role_id", "ref", ref="roles", in_game=True, required=True),
        Col("player_id", "ref", ref="players", in_game=True, label="Used by"),
        Col("target_player_id", "ref", ref="players", in_game=True, label="Target player"),
        Col("target_role_id", "ref", ref="roles", label="Target role"),
    ],
    "extra_info": [
        ID,
        Col("game_id", "ref", ref="games", required=True),
        Col("day", "int", required=True),
        Col("role_id", "ref", ref="roles", in_game=True),
        Col("info", "long_text", required=True),
    ],
    "role_swaps": [
        ID,
        Col("game_id", "ref", ref="games", required=True),
        Col("day", "int", required=True),
        Col("player_id", "ref", ref="players", in_game=True, required=True),
        Col("new_role_id", "ref", ref="roles"),
        Col("new_team", "choice", choices=TEAMS),
        Col("cause"),
    ],
}

SINGULAR = {
    "players": "player", "roles": "role", "nomination_results": "nomination result",
    "win_conditions": "win condition", "videos": "video", "games": "game",
    "game_players": "player to game", "game_results": "result", "deaths": "death",
    "nominations": "nomination", "night_actions": "night action",
    "extra_info": "extra info", "role_swaps": "role swap",
}
EVENT_TABLES = ["deaths", "nominations", "night_actions", "extra_info", "role_swaps"]
UNIQUE_NAME_TABLES = {"players", "roles", "nomination_results", "win_conditions"}


def col(table: str, name: str) -> Col:
    return next(c for c in TABLES[table] if c.name == name)


# ─── Storage ─────────────────────────────────────────────────────────────────

def load_table(name: str) -> list[dict]:
    path = DATA_DIR / f"{name}.yml"
    if not path.exists():
        return []
    with open(path) as f:
        doc = yaml.safe_load(f) or {}
    return doc.get(name) or []


def load_db() -> dict[str, list[dict]]:
    return {name: load_table(name) for name in TABLES}


class _Dumper(yaml.SafeDumper):
    """Keeps dates and times like '2024-11-01' and '00:55:01' quoted, as in the hand-written files."""


def _represent_str(dumper: yaml.SafeDumper, value: str):
    style = "'" if re.fullmatch(r"[\d:\-]+", value) else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


_Dumper.add_representer(str, _represent_str)


def dump_table(name: str, rows: list[dict]) -> str:
    cols = [c.name for c in TABLES[name]]
    if not rows:
        return f"# columns: {', '.join(cols)}\n{name}: []\n"
    ordered = []
    for r in rows:
        o = {c: r.get(c) for c in cols}
        o.update({k: v for k, v in r.items() if k not in o})  # keep columns added by hand
        ordered.append(o)
    body = yaml.dump(ordered, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=1000, default_flow_style=False)
    return f"{name}:\n" + "\n".join(f"  {line}" for line in body.splitlines()) + "\n"


def save_table(name: str, rows: list[dict]) -> None:
    # Write to a temp file then rename, so a crash mid-save can't corrupt the table
    fd, tmp = tempfile.mkstemp(dir=DATA_DIR, prefix=f".{name}.", suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        f.write(dump_table(name, rows))
    os.replace(tmp, DATA_DIR / f"{name}.yml")


def next_id(rows: list[dict]) -> int:
    return max((r["id"] for r in rows if isinstance(r.get("id"), int)), default=0) + 1


def flash(msg: str) -> None:
    """Queue a success message that survives st.rerun()."""
    st.session_state["_flash"] = msg


def show_flash() -> None:
    if msg := st.session_state.pop("_flash", None):
        st.success(msg)


# ─── Lookups ─────────────────────────────────────────────────────────────────

def labels(db: dict, table: str) -> dict[int, str]:
    if table == "videos":
        return {v["id"]: f"{v.get('name') or 'Untitled'} ({v.get('date') or 'no date'})" for v in db["videos"]}
    if table == "games":
        videos = labels(db, "videos")
        per_video: dict = {}
        for g in db["games"]:
            per_video[g.get("video_id")] = per_video.get(g.get("video_id"), 0) + 1
        out = {}
        for g in db["games"]:
            text = videos.get(g.get("video_id"), "Unknown video")
            if per_video.get(g.get("video_id"), 0) > 1:
                text += f" — game {g.get('game_number') or '?'}"
            out[g["id"]] = text
        return out
    return {r["id"]: r.get("name") or f"#{r['id']}" for r in db[table]}


def formatter(names: dict[int, str]):
    return lambda v: "—" if v is None else names.get(v, f"#{v} (missing)")


def game_player_ids(db: dict, game_id) -> list[int]:
    return [gp["player_id"] for gp in db["game_players"] if gp.get("game_id") == game_id]


def game_role_ids(db: dict, game_id, day: int | None = None) -> list[int]:
    """Roles in play: starting and believed roles, plus roles gained through a swap on or before `day`
    (any day if `day` is None). Swapped-out roles stay in the list, since they can still come up."""
    ids = set()
    for gp in db["game_players"]:
        if gp.get("game_id") == game_id:
            ids.update(v for v in (gp.get("starting_role_id"), gp.get("believed_role_id")) if v is not None)
    ids.update(
        s["new_role_id"] for s in db["role_swaps"]
        if s.get("game_id") == game_id and s.get("new_role_id") is not None
        and (day is None or (s.get("day") or 0) <= day)
    )
    return list(ids)


def game_ids_for(db: dict, c: Col, game_id, day: int | None = None) -> list[int]:
    return game_role_ids(db, game_id, day) if c.ref == "roles" else game_player_ids(db, game_id)


def ref_options(db: dict, c: Col, game_id=None, day: int | None = None) -> list[int]:
    names = labels(db, c.ref)
    if c.in_game and game_id is not None:
        ids = game_ids_for(db, c, game_id, day)
    else:
        ids = list(names)
    return sorted(ids, key=lambda i: names.get(i, "").lower())


def game_rows(db: dict, table: str, game_id) -> list[dict]:
    return [r for r in db[table] if r.get("game_id") == game_id]


def max_day(db: dict, game_id) -> int | None:
    days = [r["day"] for t in EVENT_TABLES for r in game_rows(db, t, game_id) if isinstance(r.get("day"), int)]
    return max(days, default=None)


def games_by_date(db: dict) -> list[int]:
    videos = {v["id"]: v for v in db["videos"]}
    return [
        g["id"] for g in sorted(
            db["games"],
            key=lambda g: (str(videos.get(g.get("video_id"), {}).get("date") or ""), g.get("game_number") or 0),
            reverse=True,
        )
    ]


# ─── Executions ──────────────────────────────────────────────────────────────

def block_effects(db: dict) -> dict[int, str]:
    return {r["id"]: r.get("block_effect") for r in db["nomination_results"]}


def day_ended_by(db: dict, game_id, day, nominations: list[dict] | None = None) -> dict | None:
    """The first nomination that executed its nominator immediately (e.g. the Virgin), ending the day."""
    effects = block_effects(db)
    noms = nominations if nominations is not None else db["nominations"]
    enders = [n for n in noms if n.get("game_id") == game_id and n.get("day") == day
              and effects.get(n.get("result_id")) == "executes_nominator"]
    return min(enders, key=lambda n: n["id"], default=None)


def day_execution(db: dict, game_id, day) -> tuple[int | None, str | None]:
    """Who was executed on a day, worked out from the nominations, and how.

    An immediate execution (Virgin) ends the day: the nominator is executed. Otherwise the block
    is replayed in entry order: 'marks' puts the nominee on it, 'clears' empties it, and whoever
    is left at the end of the day is executed."""
    effects = block_effects(db)
    on_block = None
    for n in sorted(game_rows(db, "nominations", game_id), key=lambda n: n["id"]):
        if n.get("day") != day:
            continue
        effect = effects.get(n.get("result_id"))
        if effect == "executes_nominator":
            return n.get("nominator_id"), "immediate"
        if effect == "marks":
            on_block = n.get("nominee_id")
        elif effect == "clears":
            on_block = None
    return (on_block, "block") if on_block is not None else (None, None)


# ─── Validation ──────────────────────────────────────────────────────────────

def prepare(db: dict, table: str, row: dict) -> dict:
    """Fill values that can be worked out from other data."""
    if table == "roles" and not row.get("alignment"):
        row["alignment"] = DEFAULT_TEAM.get(row.get("character_type"))
    if table == "games" and row.get("game_number") is None and row.get("video_id") is not None:
        numbers = [g.get("game_number") or 0 for g in db["games"] if g.get("video_id") == row["video_id"] and g["id"] != row.get("id")]
        row["game_number"] = max(numbers, default=0) + 1
    if table == "game_results" and not row.get("winning_team"):
        wc = next((w for w in db["win_conditions"] if w["id"] == row.get("win_condition_id")), None)
        if wc and wc.get("winning_team") in TEAMS:
            row["winning_team"] = wc["winning_team"]
    return row


def validate(db: dict, table: str, row: dict, others: list[dict]) -> list[str]:
    """Errors for one row; `others` is the rest of the table (for uniqueness checks)."""
    errors = []
    for c in TABLES[table]:
        v = row.get(c.name)
        if v is None:
            if c.required:
                errors.append(f"{c.title} is required.")
            continue
        if c.kind == "ref" and v not in {r["id"] for r in db[c.ref]}:
            errors.append(f"{c.title}: #{v} doesn't exist in {c.ref}.")
        elif c.kind == "ref" and c.in_game and v not in game_ids_for(db, c, row.get("game_id"), row.get("day")):
            what = "a player in this game" if c.ref == "players" else f"in play on day {row.get('day')}"
            errors.append(f"{c.title}: {labels(db, c.ref).get(v, v)} isn't {what}.")
        if c.kind == "choice" and v not in c.choices:
            errors.append(f"{c.title}: '{v}' must be one of {', '.join(c.choices)}.")
        if c.kind == "int" and v < (1 if c.name in ("day", "seat", "game_number") else 0):
            errors.append(f"{c.title} can't be {v}.")
        if c.kind == "date":
            try:
                date.fromisoformat(v)
            except ValueError:
                errors.append(f"{c.title} must be YYYY-MM-DD.")
        if c.kind == "duration" and not re.fullmatch(r"\d{1,2}:\d{2}:\d{2}", v):
            errors.append(f"{c.title} must be HH:MM:SS.")

    if table in UNIQUE_NAME_TABLES and row.get("name"):
        if row["name"].lower() in {(o.get("name") or "").lower() for o in others}:
            errors.append(f"'{row['name']}' already exists.")
    if table == "games" and any(
        o.get("video_id") == row.get("video_id") and o.get("game_number") == row.get("game_number") for o in others
    ):
        errors.append(f"This video already has game {row.get('game_number')}.")
    if table == "game_players":
        same_game = [o for o in others if o.get("game_id") == row.get("game_id")]
        if row.get("player_id") in {o.get("player_id") for o in same_game}:
            errors.append("That player is already in this game.")
        if row.get("seat") is not None and row["seat"] in {o.get("seat") for o in same_game}:
            errors.append(f"Seat {row['seat']} is already taken.")
    if table == "game_results":
        if row.get("game_id") in {o.get("game_id") for o in others}:
            errors.append("This game already has a result.")
        if not row.get("winning_team"):
            errors.append("Winning team is required for this win condition.")
        wc = next((w for w in db["win_conditions"] if w["id"] == row.get("win_condition_id")), None)
        if wc and wc.get("winning_team") in TEAMS and row.get("winning_team") not in (None, wc["winning_team"]):
            errors.append(f"'{wc['name']}' is a {wc['winning_team']} win.")
    if table == "nominations":
        ender = day_ended_by(db, row.get("game_id"), row.get("day"), others)
        if ender is not None and row.get("id", 0) > ender["id"]:
            errors.append(f"Day {row.get('day')} already ended with an immediate execution (nomination #{ender['id']}).")
    if table == "role_swaps" and row.get("new_role_id") is None and row.get("new_team") is None:
        errors.append("A role swap needs a new role, a new team, or both.")
    return errors


def references_to(db: dict, table: str, row_id: int) -> list[str]:
    """Tables that still point at this row (blocks deleting it)."""
    found = []
    for other, cols in TABLES.items():
        for c in cols:
            if c.kind == "ref" and c.ref == table:
                n = sum(1 for r in db[other] if r.get(c.name) == row_id)
                if n:
                    found.append(f"{other}.{c.name} ({n})")
    # Events point at the player, not the game_players row, so check that player within the game
    if table == "game_players":
        gp = next((r for r in db["game_players"] if r["id"] == row_id), {})
        for other in EVENT_TABLES:
            for c in TABLES[other]:
                if c.in_game:
                    if c.ref != "players":
                        continue
                    n = sum(1 for r in game_rows(db, other, gp.get("game_id")) if r.get(c.name) == gp.get("player_id"))
                    if n:
                        found.append(f"{other}.{c.name} ({n})")
    return found


# ─── Widgets ─────────────────────────────────────────────────────────────────

def input_widget(db: dict, c: Col, container, key: str, game_id=None, day: int | None = None):
    title = c.title + (" *" if c.required else "")
    if c.kind == "ref":
        options = ref_options(db, c, game_id, day)
        return container.selectbox(title, [None, *options], format_func=formatter(labels(db, c.ref)), key=key)
    if c.kind == "choice":
        return container.selectbox(title, [None, *c.choices], format_func=lambda v: "—" if v is None else v, key=key)
    if c.kind == "int":
        v = container.number_input(title, min_value=0, value=None, step=1, key=key)
        return int(v) if v is not None else None
    if c.kind == "bool":
        return container.checkbox(title, key=key)
    placeholder = {"date": "YYYY-MM-DD", "duration": "HH:MM:SS"}.get(c.kind)
    if c.kind == "long_text":
        v = container.text_area(title, key=key)
    else:
        v = container.text_input(title, placeholder=placeholder, key=key)
    return v.strip() or None


def entry_form(db: dict, table: str, key: str, fixed: dict | None = None) -> None:
    """Form that adds one row to `table` and saves it immediately."""
    fixed = fixed or {}
    cols = [c for c in TABLES[table] if c.kind != "id" and c.name not in fixed]
    short = [c for c in cols if c.kind != "long_text"]
    long = [c for c in cols if c.kind == "long_text"]
    game_id = fixed.get("game_id")
    day = fixed.get("day")

    with st.form(key, clear_on_submit=True):
        values = {}
        grid = st.columns(min(3, len(short))) if short else []
        for i, c in enumerate(short):
            values[c.name] = input_widget(db, c, grid[i % len(grid)], f"{key}_{c.name}", game_id, day)
        for c in long:
            values[c.name] = input_widget(db, c, st, f"{key}_{c.name}", game_id, day)
        submitted = st.form_submit_button(f"Add {SINGULAR[table]}", type="primary")

    if submitted:
        row = prepare(db, table, {"id": next_id(db[table]), **fixed, **values})
        errors = validate(db, table, row, db[table])
        for e in errors:
            st.error(e)
        if not errors:
            save_table(table, db[table] + [row])
            flash(f"Added {SINGULAR[table]} #{row['id']}.")
            st.rerun()


def column_config(db: dict, c: Col, game_id=None):
    if c.kind == "id":
        return st.column_config.NumberColumn("ID", disabled=True)
    if c.kind == "ref":
        return st.column_config.SelectboxColumn(
            c.title, options=ref_options(db, c, game_id), format_func=formatter(labels(db, c.ref)), required=c.required
        )
    if c.kind == "choice":
        return st.column_config.SelectboxColumn(c.title, options=list(c.choices), required=c.required)
    if c.kind == "int":
        return st.column_config.NumberColumn(c.title, min_value=0, step=1, required=c.required)
    if c.kind == "bool":
        return st.column_config.CheckboxColumn(c.title)
    width = "large" if c.kind == "long_text" else None
    return st.column_config.TextColumn(c.title, required=c.required, width=width)


def to_frame(rows: list[dict], cols: list[Col]) -> pd.DataFrame:
    data = {}
    for c in cols:
        values = [r.get(c.name) for r in rows]
        if c.kind in ("id", "int", "ref"):
            data[c.name] = pd.array(values, dtype="Int64")
        elif c.kind == "bool":
            data[c.name] = pd.array([bool(v) if v is not None else None for v in values], dtype="boolean")
        else:
            data[c.name] = pd.Series(values, dtype=object)
    return pd.DataFrame(data)


def from_cell(c: Col, v):
    if v is None or (not isinstance(v, (list, dict)) and pd.isna(v)):
        return None
    if c.kind in ("id", "int", "ref"):
        return int(v)
    if c.kind == "bool":
        return bool(v)
    v = str(v).strip()
    return v or None


def edit_grid(db: dict, table: str, rows: list[dict], key: str, hide: tuple = (), game_id=None) -> None:
    """Editable table: change cells or delete rows, then Save changes."""
    if not rows:
        st.caption("Nothing recorded yet.")
        return
    cols = [c for c in TABLES[table] if c.name not in hide]
    ver = st.session_state.get(f"_ver_{key}", 0)
    edited = st.data_editor(
        to_frame(rows, cols),
        column_config={c.name: column_config(db, c, game_id) for c in cols},
        column_order=[c.name for c in cols],
        num_rows="delete",
        hide_index=True,
        key=f"{key}_{ver}",
    )
    c1, c2 = st.columns([1, 5])
    if c1.button("Save changes", key=f"{key}_save_{ver}"):
        originals = {r["id"]: r for r in rows}
        kept = {}
        for rec in edited.to_dict("records"):
            rid = from_cell(ID, rec.get("id"))
            if rid in originals:
                kept[rid] = {**originals[rid], **{c.name: from_cell(c, rec.get(c.name)) for c in cols}}
        deleted = set(originals) - set(kept)

        errors = []
        for rid in deleted:
            if refs := references_to(db, table, rid):
                errors.append(f"Can't delete #{rid}: still used by {', '.join(refs)}.")
        new_rows = [kept.get(r["id"], r) for r in db[table] if r["id"] not in deleted]
        for rid, row in kept.items():
            if row != originals[rid]:
                prepare(db, table, row)
                others = [r for r in new_rows if r["id"] != rid]
                errors += [f"#{rid}: {e}" for e in validate(db, table, row, others)]
        for e in errors:
            c2.error(e)
        if not errors:
            save_table(table, new_rows)
            st.session_state[f"_ver_{key}"] = ver + 1
            changed = sum(1 for rid, row in kept.items() if row != originals[rid])
            flash(f"Saved {table}: {changed} changed, {len(deleted)} deleted.")
            st.rerun()


# ─── Game state & summaries ──────────────────────────────────────────────────

def final_states(db: dict, game_id) -> dict[int, dict]:
    """Each player's role and team after all role swaps, keyed by player_id."""
    team_of = {r["id"]: r.get("alignment") for r in db["roles"]}
    state = {
        gp["player_id"]: {"role_id": gp.get("starting_role_id"), "team": team_of.get(gp.get("starting_role_id"))}
        for gp in game_rows(db, "game_players", game_id)
    }
    swaps = sorted(game_rows(db, "role_swaps", game_id), key=lambda s: (s.get("day") or 0, s["id"]))
    for s in swaps:
        p = state.setdefault(s.get("player_id"), {"role_id": None, "team": None})
        if s.get("new_role_id") is not None:
            p["role_id"] = s["new_role_id"]
            p["team"] = team_of.get(s["new_role_id"])
        if s.get("new_team"):
            p["team"] = s["new_team"]
    return state


def result_of(db: dict, game_id) -> dict | None:
    return next((r for r in db["game_results"] if r.get("game_id") == game_id), None)


def integrity_problems(db: dict) -> list[str]:
    problems = []
    for table, rows in db.items():
        ids = [r.get("id") for r in rows]
        if None in ids or len(ids) != len(set(ids)):
            problems.append(f"{table}: missing or duplicate ids")
        for r in rows:
            for e in validate(db, table, r, [o for o in rows if o is not r]):
                problems.append(f"{table} #{r.get('id')}: {e}")
    return problems


def unfinished(db: dict) -> list[str]:
    games = labels(db, "games")
    out = []
    for gid in games_by_date(db):
        name = games[gid]
        gps = game_rows(db, "game_players", gid)
        if not gps:
            out.append(f"{name}: no players added")
        if missing := [gp for gp in gps if gp.get("seat") is None]:
            out.append(f"{name}: {len(missing)} player(s) with no seat")
        if missing := [gp for gp in gps if gp.get("starting_role_id") is None]:
            out.append(f"{name}: {len(missing)} player(s) with no role")
        noms = game_rows(db, "nominations", gid)
        if missing := [n for n in noms if n.get("result_id") is None]:
            out.append(f"{name}: {len(missing)} nomination(s) with no result")
        if missing := [n for n in noms if n.get("votes") is None]:
            out.append(f"{name}: {len(missing)} nomination(s) with no vote count")
        if missing := [d for d in game_rows(db, "deaths", gid) if d.get("cause_type") is None]:
            out.append(f"{name}: {len(missing)} death(s) with no cause")
        players = labels(db, "players")
        for d in range(1, (max_day(db, gid) or 0) + 1):
            executed, _ = day_execution(db, gid, d)
            exec_deaths = {x.get("player_id") for x in game_rows(db, "deaths", gid)
                           if x.get("day") == d and x.get("cause_type") == "Execution"}
            if executed is not None and executed not in exec_deaths:
                out.append(f"{name}: day {d} — {players.get(executed, '?')} was executed but has no death row "
                           f"(fine if they survived, e.g. Fool or Pacifist)")
            for pid in exec_deaths - {executed}:
                out.append(f"{name}: day {d} — {players.get(pid, '?')} died by execution, but the nominations "
                           f"don't put them on the block (check the nomination results)")
        if not result_of(db, gid):
            out.append(f"{name}: no result yet (in progress)")
    return out


def names_frame(db: dict, table: str, rows: list[dict], hide: tuple = ("id", "game_id")) -> pd.DataFrame:
    """Rows with ids swapped for names, for read-only display."""
    cols = [c for c in TABLES[table] if c.name not in hide]
    lookups = {c.name: labels(db, c.ref) for c in cols if c.kind == "ref"}
    return pd.DataFrame([
        {c.title: (lookups[c.name].get(r.get(c.name)) if c.name in lookups else r.get(c.name)) for c in cols}
        for r in rows
    ])


# ─── Page ────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="BotC Data Entry", layout="wide")
st.title("Blood on the Clocktower")
show_flash()

db = load_db()
player_names = labels(db, "players")
role_names = labels(db, "roles")
game_names = labels(db, "games")
result_names = labels(db, "nomination_results")
wc_names = labels(db, "win_conditions")

tab_entry, tab_summary, tab_videos, tab_ref, tab_checks = st.tabs(
    ["Game Entry", "Games Summary", "Videos & Games", "Reference", "Checks"]
)


# ─── Tab: Game Entry ─────────────────────────────────────────────────────────

with tab_entry:
    if not db["games"]:
        st.info("No games yet. Add a video and a game in **Videos & Games** first.")
    else:
        c1, c2, c3 = st.columns([4, 1, 2])
        game_id = c1.selectbox("Game", games_by_date(db), format_func=formatter(game_names), key="ge_game")
        day = int(c2.number_input("Current day", min_value=1, value=max_day(db, game_id) or 1, step=1, key=f"ge_day_{game_id}"))
        only_day = c3.toggle(f"Only show day {day} in tables", key=f"ge_only_{game_id}")

        gps = game_rows(db, "game_players", game_id)
        res = result_of(db, game_id)
        status = f"Result: **{res.get('winning_team')}** — {wc_names.get(res.get('win_condition_id'), '?')}" if res else "In progress"
        st.caption(f"{len(gps)} players · last day recorded: {max_day(db, game_id) or '—'} · {status}")

        def day_rows(table: str) -> list[dict]:
            rows = game_rows(db, table, game_id)
            return [r for r in rows if r.get("day") == day] if only_day else rows

        sub = st.tabs(["Players", "Deaths", "Nominations", "Night Actions", "Extra Info", "Role Swaps", "Result"])

        with sub[0]:
            st.subheader("Players in this game")
            st.caption("Add each player with their seat and starting role. Day actions only offer the roles entered here.")
            if not db["players"]:
                st.info("Add players in **Reference → Players** first.")
            entry_form(db, "game_players", f"f_gp_{game_id}", fixed={"game_id": game_id})
            edit_grid(db, "game_players", sorted(gps, key=lambda r: r.get("seat") or 99), f"g_gp_{game_id}", hide=("game_id",))

        for tab, table, hint in [
            (sub[1], "deaths", "Who died, when, and what killed them."),
            (sub[2], "nominations", "Record each vote's result as it happens: Marked, Tied, Not enough votes… Don't record 'Executed': "
                                    "the execution is worked out from the block at the end of the day, and its death goes on the Deaths tab."),
            (sub[3], "night_actions", "Who used an ability and who or what they chose."),
            (sub[4], "extra_info", "What a role learned, demon bluffs, or anything else worth noting."),
            (sub[5], "role_swaps", "Role or team changes: star-pass, Fang Gu jump, Pit-Hag, Goon… Use cause 'setup' for changes at the start."),
        ]:
            with tab:
                st.subheader(f"{SINGULAR[table].capitalize()}s — day {day}" if table != "extra_info" else f"Extra info — day {day}")
                st.caption(hint)
                if not gps and any(c.in_game for c in TABLES[table]):
                    st.warning("Add players to this game first.")
                elif any(c.in_game and c.ref == "roles" for c in TABLES[table]) and not game_role_ids(db, game_id):
                    st.warning("Role fields only offer roles in this game. Add starting roles on the Players tab first.")
                if table == "nominations":
                    executed, how = day_execution(db, game_id, day)
                    if how == "immediate":
                        st.info(f"Day {day} ended: **{player_names.get(executed, '?')}** was executed immediately. No more nominations today.")
                    elif executed is not None:
                        st.info(f"On the block: **{player_names.get(executed, '?')}**")
                    if not db["nomination_results"]:
                        st.warning("Add nomination results in **Reference → Nomination Results** first.")
                entry_form(db, table, f"f_{table}_{game_id}_{day}", fixed={"game_id": game_id, "day": day})
                rows = sorted(day_rows(table), key=lambda r: (r.get("day") or 0, r["id"]))
                edit_grid(db, table, rows, f"g_{table}_{game_id}", hide=("game_id",), game_id=game_id)

        with sub[6]:
            st.subheader("Result")
            st.caption("Add when the game ends. The winning team fills in from the win condition unless it can go either way.")
            if res:
                edit_grid(db, "game_results", [res], f"g_res_{game_id}", hide=("game_id",))
            else:
                entry_form(db, "game_results", f"f_res_{game_id}", fixed={"game_id": game_id})


# ─── Tab: Games Summary ──────────────────────────────────────────────────────

with tab_summary:
    if not db["games"]:
        st.info("No games yet.")
    else:
        videos = {v["id"]: v for v in db["videos"]}
        overview = []
        for gid in games_by_date(db):
            g = next(x for x in db["games"] if x["id"] == gid)
            v = videos.get(g.get("video_id"), {})
            res = result_of(db, gid)
            overview.append({
                "Game": game_names[gid],
                "Date": v.get("date"),
                "Length": v.get("length"),
                "Members": bool(v.get("members")),
                "Players": len(game_rows(db, "game_players", gid)),
                "Days": max_day(db, gid),
                "Winner": res.get("winning_team") if res else None,
                "Win condition": wc_names.get(res.get("win_condition_id")) if res else None,
                "Status": "Finished" if res else "In progress",
            })
        overview_df = pd.DataFrame(overview)

        finished = [gid for gid in games_by_date(db) if result_of(db, gid)]
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Games", len(overview_df))
        m2.metric("Finished", len(finished))
        m3.metric("Good wins", sum(1 for gid in finished if result_of(db, gid).get("winning_team") == "Good"))
        m4.metric("Evil wins", sum(1 for gid in finished if result_of(db, gid).get("winning_team") == "Evil"))
        days = [max_day(db, gid) for gid in finished if max_day(db, gid)]
        m5.metric("Avg days", f"{sum(days) / len(days):.1f}" if days else "—")

        s_games, s_players, s_roles, s_detail = st.tabs(["Games", "Players", "Roles & endings", "Game detail"])

        with s_games:
            st.dataframe(overview_df, hide_index=True, width="stretch")

        # One row per player per finished game, with their final team
        appearances = []
        for gid in finished:
            winner = result_of(db, gid).get("winning_team")
            states = final_states(db, gid)
            for gp in game_rows(db, "game_players", gid):
                st_ = states.get(gp["player_id"], {})
                appearances.append({
                    "player": player_names.get(gp["player_id"]),
                    "starting_role": role_names.get(gp.get("starting_role_id")),
                    "final_team": st_.get("team"),
                    "won": st_.get("team") is not None and st_.get("team") == winner,
                })
        app_df = pd.DataFrame(appearances)

        with s_players:
            if app_df.empty:
                st.caption("Stats appear once a game has a result.")
            else:
                stats = app_df.groupby("player").agg(
                    Games=("player", "size"),
                    Wins=("won", "sum"),
                    Evil=("final_team", lambda s: int((s == "Evil").sum())),
                )
                stats["Win %"] = (100 * stats["Wins"] / stats["Games"]).round(0)
                st.dataframe(stats.sort_values(["Games", "Win %"], ascending=False), width="stretch")
                st.caption("Team is the player's final team, after any role swaps.")

        with s_roles:
            c1, c2 = st.columns(2)
            if not app_df.empty:
                role_stats = (
                    app_df.dropna(subset=["starting_role"])
                    .groupby("starting_role")
                    .agg(Played=("starting_role", "size"), Wins=("won", "sum"))
                    .sort_values("Played", ascending=False)
                )
                c1.write("**Starting roles**")
                c1.dataframe(role_stats, width="stretch")
            ends = pd.Series([wc_names.get(result_of(db, gid).get("win_condition_id")) for gid in finished])
            if not ends.empty:
                c2.write("**How games ended**")
                c2.dataframe(ends.value_counts().rename_axis("Win condition").rename("Games"), width="stretch")

        with s_detail:
            gid = st.selectbox("Game", games_by_date(db), format_func=formatter(game_names), key="sum_game")
            g = next(x for x in db["games"] if x["id"] == gid)
            v = videos.get(g.get("video_id"), {})
            res = result_of(db, gid)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Date", v.get("date") or "—")
            c2.metric("Length", v.get("length") or "—")
            c3.metric("Winner", res.get("winning_team") if res else "In progress")
            c4.metric("Days", max_day(db, gid) or "—")
            if res:
                st.caption(f"Ended by: {wc_names.get(res.get('win_condition_id'), '?')}")

            states = final_states(db, gid)
            deaths = game_rows(db, "deaths", gid)
            players_df = pd.DataFrame([
                {
                    "Seat": gp.get("seat"),
                    "Player": player_names.get(gp["player_id"]),
                    "Starting role": role_names.get(gp.get("starting_role_id")),
                    "Believes they are": role_names.get(gp.get("believed_role_id")),
                    "Final role": role_names.get(states.get(gp["player_id"], {}).get("role_id")),
                    "Final team": states.get(gp["player_id"], {}).get("team"),
                    "Died": ", ".join(
                        f"day {d.get('day')} {(d.get('timing') or '').lower()}".strip()
                        for d in deaths if d.get("player_id") == gp["player_id"]
                    ) or None,
                }
                for gp in sorted(game_rows(db, "game_players", gid), key=lambda r: r.get("seat") or 99)
            ])
            st.dataframe(players_df, hide_index=True, width="stretch")

            # Derived day table: alive count, deaths and nominations per day
            last = max_day(db, gid) or 0
            n_players = len(game_rows(db, "game_players", gid))
            day_summary = []
            for d in range(1, last + 1):
                died = [x for x in deaths if x.get("day") == d]
                noms = [n for n in game_rows(db, "nominations", gid) if n.get("day") == d]
                day_summary.append({
                    "Day": d,
                    "Deaths": ", ".join(player_names.get(x.get("player_id"), "?") for x in died) or None,
                    "Nominations": len(noms),
                    "Executed": (lambda e: f"{player_names.get(e[0], '?')}" + (" (immediate)" if e[1] == "immediate" else "")
                                 if e[0] is not None else None)(day_execution(db, gid, d)),
                    "Alive at end": n_players - sum(1 for x in deaths if (x.get("day") or 0) <= d),
                })
            if day_summary:
                st.dataframe(pd.DataFrame(day_summary), hide_index=True, width="stretch")

            for d in range(1, last + 1):
                with st.expander(f"Day {d}"):
                    for table, title in [("deaths", "Deaths"), ("nominations", "Nominations"),
                                         ("night_actions", "Night actions"), ("extra_info", "Extra info"),
                                         ("role_swaps", "Role swaps")]:
                        rows = [r for r in game_rows(db, table, gid) if r.get("day") == d]
                        if rows:
                            st.write(f"**{title}**")
                            st.dataframe(names_frame(db, table, rows, hide=("id", "game_id", "day")), hide_index=True, width="stretch")


# ─── Tab: Videos & Games ─────────────────────────────────────────────────────

with tab_videos:
    v_tab, g_tab = st.tabs(["Videos", "Games"])
    with v_tab:
        st.caption("One row per video. Length as HH:MM:SS.")
        entry_form(db, "videos", "f_videos")
        edit_grid(db, "videos", db["videos"], "g_videos")
    with g_tab:
        st.caption("One row per game. Leave the game number empty for the next one in that video (usually 1).")
        entry_form(db, "games", "f_games")
        edit_grid(db, "games", db["games"], "g_games")


# ─── Tab: Reference ──────────────────────────────────────────────────────────

with tab_ref:
    ref_tabs = st.tabs(["Players", "Roles", "Nomination Results", "Win Conditions"])
    for tab, table, hint in [
        (ref_tabs[0], "players", "Everyone who has played. Names must be unique."),
        (ref_tabs[1], "roles", "Default team fills in from the character type if left empty."),
        (ref_tabs[2], "nomination_results", "Block effect: 'marks' puts the nominee on the block, 'clears' empties it (a tie), "
                                             "'none' changes nothing, 'executes_nominator' executes the nominator at once and ends the day (Virgin)."),
        (ref_tabs[3], "win_conditions", "Possible endings. Use 'Either' where the ending can go to both teams."),
    ]:
        with tab:
            st.caption(hint)
            entry_form(db, table, f"f_{table}")
            rows = sorted(db[table], key=lambda r: (r.get("name") or "").lower()) if table in ("players", "roles") else db[table]
            edit_grid(db, table, rows, f"g_{table}")


# ─── Tab: Checks ─────────────────────────────────────────────────────────────

with tab_checks:
    st.subheader("Data problems")
    st.caption("Broken references, duplicates or invalid values, e.g. from editing the YAML by hand.")
    problems = integrity_problems(db)
    if problems:
        for p in problems:
            st.error(p)
    else:
        st.success("No problems found.")

    st.subheader("Still to fill in")
    todo = unfinished(db)
    if todo:
        for t in todo:
            st.write(f"- {t}")
    else:
        st.success("Everything is filled in.")
