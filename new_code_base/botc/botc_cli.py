#!/usr/bin/env python3
"""Blood on the Clocktower data entry CLI.

Usage:
    python botc_cli.py
"""

import sys
import yaml
from pathlib import Path

BOTC_DIR = Path(__file__).parent
GAMES_DIR = BOTC_DIR / "games"
REF_DIR = BOTC_DIR / "reference"


# ─── Helpers ─────────────────────────────────────────────────────────────────

def load_ref() -> tuple[list, list]:
    with open(REF_DIR / "players.yml") as f:
        players = yaml.safe_load(f)["players"]
    with open(REF_DIR / "roles.yml") as f:
        roles = [r["name"] for r in yaml.safe_load(f)["roles"]]
    return players, roles


def load_game(game_id: str) -> dict:
    with open(GAMES_DIR / f"{game_id}.yml") as f:
        return yaml.safe_load(f)


def save_game(game_id: str, data: dict) -> None:
    path = GAMES_DIR / f"{game_id}.yml"
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    print(f"  Saved → {path.relative_to(BOTC_DIR)}")


def list_game_ids() -> list[str]:
    return sorted(p.stem for p in GAMES_DIR.glob("*.yml"))


def pick(options: list, prompt: str, allow_blank: bool = False):
    """Numbered list selection. Returns None if blank is allowed and user skips."""
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    if allow_blank:
        print("  (Enter to skip)")
    while True:
        raw = input(f"{prompt}: ").strip()
        if allow_blank and raw == "":
            return None
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print("  Invalid — enter a number from the list.")


def ask(prompt: str, allow_blank: bool = True) -> str | None:
    raw = input(f"{prompt}: ").strip()
    return raw if raw else None


def int_or_none(val: str | None) -> int | None:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


# ─── Commands ────────────────────────────────────────────────────────────────

def cmd_new_game(players_ref: list, roles_ref: list) -> None:
    print("\n=== New Game ===")

    video_id = ask("Video ID (e.g. 240920)", allow_blank=False)
    if GAMES_DIR / f"{video_id}.yml" in GAMES_DIR.iterdir():
        print(f"  Game {video_id} already exists.")
        return

    name = ask("Video name")
    date = ask("Date (YYYY-MM-DD)")
    length = ask("Length (HH:MM:SS)")
    members_raw = input("Members only? (y/n): ").strip().lower()
    members = members_raw == "y"

    n_players = int(input("Number of players: ").strip())
    players = []
    for i in range(n_players):
        print(f"\nPlayer {i + 1}:")
        name_p = pick(players_ref, "  Name")
        position = int(input("  Seating position: ").strip())
        role = pick(roles_ref, "  Role (Enter to skip)", allow_blank=True)
        entry: dict = {"name": name_p, "position": position}
        if role:
            entry["role"] = role
            if role == "Drunk":
                drunk_role = pick(roles_ref, "  Drunk thinks they are")
                entry["drunk_role"] = drunk_role
        players.append(entry)

    data = {
        "video": {
            "id": video_id,
            "name": name,
            "date": date,
            "length": length,
            "members": members,
        },
        "result": {"outcome": None, "number_of_days": None},
        "players": players,
        "days": [
            {"day": 0, "extra_info": [{"role": None, "info": None}]}
        ],
    }
    save_game(video_id, data)


def cmd_add_day(players_ref: list, roles_ref: list) -> None:
    print("\n=== Add Day ===")

    game_ids = list_game_ids()
    if not game_ids:
        print("No games found. Create one first.")
        return

    game_id = pick(game_ids, "Select game")
    data = load_game(game_id)
    game_players = [p["name"] for p in data["players"]]

    existing_days = [d["day"] for d in data["days"]]
    next_day = max(existing_days) + 1 if existing_days else 1
    day_raw = input(f"Day number [{next_day}]: ").strip()
    day_num = int(day_raw) if day_raw else next_day

    night_kill = pick(game_players, "Night kill (Enter to skip)", allow_blank=True)
    execution = pick(game_players, "Execution (Enter to skip)", allow_blank=True)

    # extra_info
    extra_info = []
    print("\nExtra info (role ability results). Enter blank role to stop:")
    while True:
        role = pick(roles_ref, "  Role (Enter to finish)", allow_blank=True)
        if role is None:
            break
        info = ask("  Info")
        extra_info.append({"role": role, "info": info})

    # nominations
    nominations = []
    if input("\nAdd nominations? (y/n): ").strip().lower() == "y":
        while True:
            print("\nNomination (Enter nominee blank to finish):")
            nominate = pick(game_players, "  Nominate", allow_blank=True)
            if nominate is None:
                break
            nominator = pick(game_players, "  Nominator", allow_blank=True)
            votes = int_or_none(ask("  Votes (Enter to skip)"))
            ghost_votes = int_or_none(ask("  Ghost votes (Enter to skip)"))
            result = ask("  Result (Enter to skip)")
            nominations.append({
                "nominate": nominate,
                "nominator": nominator,
                "votes": votes,
                "ghost_votes": ghost_votes,
                "result": result,
            })

    day_entry: dict = {
        "day": day_num,
        "night_kill": night_kill,
        "execution": execution,
    }
    if extra_info:
        day_entry["extra_info"] = extra_info
    if nominations:
        day_entry["nominations"] = nominations
    # Minion actions
    minion_actions = []
    if input("\nAdd minion actions? (y/n): ").strip().lower() == "y":
        while True:
            print("\nMinion action (Enter role blank to finish):")
            role = pick(roles_ref, "  Role (Enter to finish)", allow_blank=True)
            if role is None:
                break
            player = pick(game_players, "  Player (Enter to skip)", allow_blank=True)
            minion_actions.append({"role": role, "player": player})
    if minion_actions:
        day_entry["minion_action"] = minion_actions

    # Townsfolk actions
    townsfolk_actions = []
    if input("Add townsfolk actions? (y/n): ").strip().lower() == "y":
        while True:
            print("\nTownsfolk action (Enter role blank to finish):")
            role = pick(roles_ref, "  Role (Enter to finish)", allow_blank=True)
            if role is None:
                break
            player = pick(game_players, "  Player (Enter to skip)", allow_blank=True)
            townsfolk_actions.append({"role": role, "player": player})
    if townsfolk_actions:
        day_entry["townsfolk_action"] = townsfolk_actions

    data["days"].append(day_entry)
    save_game(game_id, data)


def cmd_reveal(players_ref: list, roles_ref: list) -> None:
    print("\n=== End of Game Reveal ===")

    game_ids = list_game_ids()
    if not game_ids:
        print("No games found.")
        return

    game_id = pick(game_ids, "Select game")
    data = load_game(game_id)
    game_players = [p["name"] for p in data["players"]]

    # Fill in missing player roles
    print("\nPlayer roles (Enter to keep existing):")
    for player in data["players"]:
        current = player.get("role")
        label = f"  {player['name']} [{current or 'unknown'}]"
        role = pick(roles_ref, f"{label} → role (Enter to skip)", allow_blank=True)
        if role:
            player["role"] = role
            if role == "Drunk" and not player.get("drunk_role"):
                drunk_role = pick(roles_ref, "  Drunk thinks they are")
                player["drunk_role"] = drunk_role

    # Fill in night actions on existing scaffolds
    for day_entry in data["days"]:
        day_num = day_entry["day"]

        if "minion_action" in day_entry:
            print(f"\nDay {day_num} — Minion actions:")
            for action in day_entry["minion_action"]:
                if not action.get("role"):
                    action["role"] = pick(roles_ref, "  Role (Enter to skip)", allow_blank=True)
                if not action.get("player"):
                    action["player"] = pick(game_players, "  Player (Enter to skip)", allow_blank=True)

        if "townsfolk_action" in day_entry:
            print(f"\nDay {day_num} — Townsfolk actions:")
            for action in day_entry["townsfolk_action"]:
                if not action.get("role"):
                    action["role"] = pick(roles_ref, "  Role (Enter to skip)", allow_blank=True)
                if not action.get("player"):
                    action["player"] = pick(game_players, "  Player (Enter to skip)", allow_blank=True)

        if day_num == 0:
            print(f"\nDay 0 — Add reveal extra info (e.g. Imp bluffs)?")
            while input("Add entry? (y/n): ").strip().lower() == "y":
                role = pick(roles_ref, "  Role", allow_blank=True)
                if role:
                    info = ask("  Info")
                    day_entry.setdefault("extra_info", []).append({"role": role, "info": info})

    # Result
    print("\nGame result:")
    outcome = pick(["Good", "Evil"], "Outcome")
    n_days = int_or_none(ask("Number of days"))
    data["result"] = {"outcome": outcome, "number_of_days": n_days}

    save_game(game_id, data)


# ─── Main loop ───────────────────────────────────────────────────────────────

def main() -> None:
    print("\nBlood on the Clocktower — Data Entry")
    print("=====================================")

    players_ref, roles_ref = load_ref()
    commands = ["new-game", "add-day", "reveal", "quit"]

    while True:
        print()
        cmd = pick(commands, "Command")
        if cmd == "new-game":
            cmd_new_game(players_ref, roles_ref)
        elif cmd == "add-day":
            cmd_add_day(players_ref, roles_ref)
        elif cmd == "reveal":
            cmd_reveal(players_ref, roles_ref)
        elif cmd == "quit":
            print("Bye.")
            sys.exit(0)


if __name__ == "__main__":
    main()
