from pathlib import Path
from typing import Any

import yaml


class SessionStore:
    def __init__(self, sessions_dir: Path):
        self.sessions_dir = sessions_dir
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def list_sessions(self, game: str | None = None) -> list[str]:
        sessions = sorted(p.stem for p in self.sessions_dir.glob("*.yml"))
        if game:
            sessions = [s for s in sessions if s.lower().startswith(game.lower())]
        return sessions

    def load(self, session_id: str) -> dict:
        with open(self.sessions_dir / f"{session_id}.yml") as f:
            return yaml.safe_load(f)

    def save(self, session_id: str, data: dict) -> None:
        with open(self.sessions_dir / f"{session_id}.yml", "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def exists(self, session_id: str) -> bool:
        return (self.sessions_dir / f"{session_id}.yml").exists()


def write_delta(session_data: dict, delta_base: Path) -> None:
    """Flatten session actions into a Delta table. No-op if deltalake is not installed."""
    try:
        import pandas as pd
        from deltalake import write_deltalake
    except ImportError:
        return

    rows = _extract_actions(session_data)
    if not rows:
        return

    df = pd.DataFrame(rows)
    table_path = str(delta_base / session_data["game"].lower().replace(" ", "_"))
    write_deltalake(table_path, df, mode="append", schema_mode="merge")


def _extract_actions(session: dict) -> list[dict[str, Any]]:
    rows = []
    base = {
        "session_id": session.get("session_id", ""),
        "game": session.get("game", ""),
        "platform": session.get("platform"),
        "date": session.get("date"),
    }
    for era in session.get("eras", []):
        for action in era.get("actions", []):
            rows.append({
                **base,
                "era": era.get("era_number"),
                "player": action.get("player"),
                "action_type": action.get("action_type"),
                "module": action.get("module"),
                "module_level": action.get("module_level"),
                "choice": action.get("choice"),
                "notes": action.get("notes"),
            })
    return rows
