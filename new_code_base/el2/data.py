from dataclasses import dataclass
import pathlib
import json


@dataclass(frozen=True)
class Col:
    name: str
    type: str = "text"
    unique: bool = False
    required: bool = False
    label: str = ""
    choices: list[str] | None = None


def load_table(data_path: pathlib.Path, table_name: str) -> list:
    final_path = data_path / f"{table_name}.json"
    if not final_path.exists():
        return []
    else:
        with open(data_path / f"{table_name}.json") as f:
            data = json.load(f)
        return data


def store_table(data_path: pathlib.Path, data: list[dict], table_name: str) -> None:
    with open(data_path / f"{table_name}.json", "w") as f:
        json.dump(data, f)


@dataclass(frozen=True)
class Tab:
    name: str
    caption: str
    data_name: str


def validate(data: list[dict], cols: list[Col], values: dict) -> list:
    errors = []
    for col in cols:
        if col.unique and data != []:
            current_val = [r[col.name] for r in data]
            if values[col.name] in current_val:
                errors.append(
                    f"Duplicate value found in column: {col.name} with value: {values[col.name]}"
                )
        if col.required and values.get(col.name) is None:
            errors.append(f"Missing required value for column: {col.name}")

    return errors


# def load_db(data_path: pathlib.Path, table_names: [str]) -> dict[list]:
#     result = {}
#     for table in table_names:
#         with open(data_path / f"{table}.yml") as f:
#             data = yaml.safe_load(f)
#         result[table] = data
#     return result
