from __future__ import annotations

import json
import pathlib

from app.ttt.storage import (
    TTTVideoWriter,
    TTTRoundsWriter,
    TTTPlayersWriter,
    TTTRolesWriter,
    TTTWinnerChartWriter,
    TTTPlaysWriter,
)

DATA_DIR = pathlib.Path(__file__).parent / "data"


def _load_json(filename: str) -> list[dict]:
    return json.loads((DATA_DIR / filename).read_bytes())


def load_all(mode: str = "overwrite") -> None:
    _load_video(mode)
    _load_winnerchartdetails(mode)
    _load_rounds(mode)
    _load_players(mode)
    _load_roles(mode)
    _load_plays(mode)


def _load_video(mode: str) -> None:
    data = _load_json("videodata.json")
    TTTVideoWriter().write(data, mode=mode)
    print(f"Wrote {len(data)} video rows")


def _load_winnerchartdetails(mode: str) -> None:
    data = _load_json("WinnerChartColours.json")
    TTTWinnerChartWriter().write(data, mode=mode)
    print(f"Wrote {len(data)} winnerchartdetails rows")


def _load_rounds(mode: str) -> None:
    data = _load_json("rounddata.json")
    TTTRoundsWriter().write(data, mode=mode)
    print(f"Wrote {len(data)} round rows")


def _load_players(mode: str) -> None:
    data = _load_json("players.json")
    TTTPlayersWriter().write(data, mode=mode)
    print(f"Wrote {len(data)} player rows")


def _load_roles(mode: str) -> None:
    data = _load_json("role.json")
    TTTRolesWriter().write(data, mode=mode)
    print(f"Wrote {len(data)} role rows")


def _load_plays(mode: str) -> None:
    data = _load_json("playdata.json")
    rows = []
    for entry in data:
        video_id = entry["round_id"]["video_id"]
        round_number = entry["round_id"]["round_number"]
        for player, role in entry["role_link"].items():
            rows.append(
                {
                    "video_id": video_id,
                    "round_number": round_number,
                    "player": player,
                    "role": role,
                }
            )
    TTTPlaysWriter().write(rows, mode=mode)
    print(f"Wrote {len(rows)} play rows")
