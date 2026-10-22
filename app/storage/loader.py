from __future__ import annotations

import json
import pathlib

from app.storage.delta import DeltaWriter


class JsonDeltaLoader(DeltaWriter):
    """Base class for loading JSON files into a Delta Lake table.

    Subclasses implement _parse() to transform raw JSON into rows.
    """

    def load(self, *paths: pathlib.Path, mode: str = "overwrite") -> None:
        data = [json.loads(p.read_text()) for p in paths]
        rows = self._parse(*data)
        self.write(rows, mode=mode)

    def _parse(self, *data) -> list[dict]:
        raise NotImplementedError
