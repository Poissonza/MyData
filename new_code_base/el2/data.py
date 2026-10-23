from dataclasses import dataclass
import pathlib
import json


@dataclass(frozen=True)
class Col:
    name: str
    type: str = "text"


def load_table(data_path: pathlib.Path, table_name: str) -> list:
    with open(data_path / f"{table_name}.json") as f:
        data = json.load(f)
    return data

def store_table(data_path: pathlib.Path, data: [dict], table_name: str) -> None:
    with open(data_path / f"{table_name}.json", "w") as f:
        json.dump(data, f)

@dataclass(frozen=True)
class Tab:
    name: str
    caption: str
    data_name: str


def load_db(data_path: pathlib.Path, table_names: [str]) -> dict[list]:
    result = {}
    for table in table_names:
        with open(data_path / f"{table}.yml") as f:
            data = yaml.safe_load(f)
        result[table] = data
    return result
