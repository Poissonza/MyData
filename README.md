# MyData

Personal data collection and analysis project. Pulls data from game APIs and static JSON files, stores everything in Delta Lake, and exposes it for analysis via Jupyter notebooks.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Storage | Delta Lake (local via Docker, or DBFS/Unity Catalog in prod) |
| Processing | PySpark 3.5 |
| Notebooks | Jupyter (PySpark kernel) |
| API clients | Python (`requests`) |

---

## Setup

### 1. Environment variables

Copy `.env.example` to `.env` and fill in your values:

```
APP_ENV=dev
DELTA_BASE_PATH=file:///data/delta

TORN_API_KEY=your_torn_api_key
```

The `DB_*` variables (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`) are legacy and only needed if using the old SQLAlchemy-based `dbaccess.py` directly. TTT data is now loaded via Delta Lake.

### 2. Start services

```bash
docker-compose up
```

This starts:
- **spark** — Spark master (`apache/spark:3.5.0`) at `spark://localhost:7077`, UI at http://localhost:8080
- **jupyter** — Jupyter with PySpark kernel at http://localhost:8888
- **md-python** — plain Python container for running scripts

### 3. Install dependencies (local development)

```bash
uv sync
```

---

## Project structure

```
app/
├── storage/
│   ├── delta.py        # DeltaWriter base class (write + read)
│   └── loader.py       # JsonDeltaLoader base class (load JSON → Delta)
│
├── torn/
│   ├── api.py          # TornAPI base (wraps v2 REST API)
│   ├── user.py         # User endpoints (attacks, logs, basic, etc.)
│   ├── faction.py      # Faction endpoints (attacks, wars, etc.)
│   ├── travel.py       # TravelDataCleaning — parse user travel logs
│   └── storage.py      # TornUserWriter, TornFactionWriter, TornTravelWriter
│
├── gameanalysis/
│   ├── civ6/           # Civilization 6
│   ├── galciv4/        # Galactic Civilizations 4
│   ├── galciv4_supernova/
│   ├── humankind/      # Humankind
│   ├── aow4/           # Age of Wonders 4
│   └── northgard/      # Northgard
│       └── (each has loader.py + data/*.json)
│
├── boardgamegeek/      # BGG XML API
├── ttt/                # TTT (Trouble in Terrorist Town) session data
└── pcgaming/           # PC game collection (Steam/GOG)

notebooks/              # Jupyter notebooks for analysis
```

---

## Fetching Torn data

The old notebooks manually defined Spark schemas, managed deduplication, and wrote directly to Spark tables. The module classes handle all of that — notebooks become much shorter.

### User data

```python
from app.torn.user import User
from app.torn.storage import TornUserWriter

user = User()  # reads TORN_API_KEY from env

# --- fetch and store ---
writer = TornUserWriter()

# Fetch any endpoint and store the raw response
writer.write_response("attacks",    user.get_attacks(sort="ASC"))
writer.write_response("basic",      user.get_basic())
writer.write_response("battlestats", user.get_battlestats())
writer.write_response("bounties",   user.get_bounties())
writer.write_response("education",  user.get_education())
writer.write_response("hof",        user.get_hof())
writer.write_response("honors",     user.get_honors())
writer.write_response("jobpoints",  user.get_job_points())

# --- read back ---
df = writer.read()
df.filter(df.endpoint == "attacks").select("data.*").show()
```

### Incremental fetch (attacks example)

```python
import datetime
from app.torn.user import User
from app.torn.storage import TornUserWriter

user   = User()
writer = TornUserWriter()

df = writer.read()
if df is not None:
    last_ts = df.filter(df.endpoint == "attacks") \
                .agg({"retrieved_at": "max"}) \
                .collect()[0][0]
    ts_from = int(datetime.datetime.fromisoformat(last_ts).timestamp())
else:
    ts_from = 1681484237  # fallback epoch

attacks = user.get_attacks(ts_from=ts_from, sort="ASC")
writer.write_response("attacks", attacks)
```

### Faction data

```python
from app.torn.faction import Faction
from app.torn.storage import TornFactionWriter

faction = Faction()
writer  = TornFactionWriter()

writer.write_response("attacks", faction.get_attacks(sort="ASC"))
writer.write_response("basic",   faction.get_basic())
writer.write_response("wars",    faction.get_wars())

df = writer.read()
df.filter(df.endpoint == "attacks").select("data.*").show()
```

### Travel log data

```python
from app.torn.user import User
from app.torn.travel import TravelDataCleaning
from app.torn.storage import TornTravelWriter

user    = User()
cleaner = TravelDataCleaning()
writer  = TornTravelWriter()

raw_logs = user.get_logs(category=4)  # category 4 = travel
cleaned  = cleaner.clean(raw_logs["log"])

writer.write_travel_data(cleaned)

# read back a specific category
df = writer.read()
df.filter(df.category == "travel").show()
```

---

## Loading game analysis data

Each game domain has a `loader.py` with a single class. All loaders share the same interface: `load(*paths)` reads the JSON files and writes to the domain's Delta table.

```python
import pathlib
from app.gameanalysis.civ6.loader         import Civ6Loader
from app.gameanalysis.galciv4.loader      import GalCiv4Loader
from app.gameanalysis.humankind.loader    import HumankindLoader
from app.gameanalysis.aow4.loader         import AOW4Loader
from app.gameanalysis.northgard.loader    import NorthgardLoader

data = pathlib.Path("app/gameanalysis")

Civ6Loader().load(
    data / "civ6/data/game_played.json"
)

GalCiv4Loader().load(
    data / "galciv4/data/play_data.json"
)

HumankindLoader().load(
    data / "humankind/data/games_played.json"
)

AOW4Loader().load(
    data / "aow4/data/game_played.json"
)

NorthgardLoader().load(
    data / "northgard/data/games_played.json"
)
```

To add a new game, add the JSON data to `data/` and create a `loader.py` that extends `JsonDeltaLoader` and implements `_parse()`.

### Reading game data back

```python
from app.gameanalysis.civ6.loader import Civ6Loader

df = Civ6Loader().read()
df.show()
```

---

## Loading TTT data

TTT (Trouble in Terrorist Town) session data lives in `app/ttt/data/` as static JSON files. Run the loader to write all tables to Delta Lake:

```bash
# Inside the md-python container
docker exec -e PYTHONPATH=/ md-python python -m app.ttt.update
```

Or from a local Python environment with `PYTHONPATH` set to the repo root:

```bash
PYTHONPATH=. python -m app.ttt.update
```

This writes six Delta tables (all under `ttt/`):

| Table | Rows (approx) | Notes |
|-------|--------------|-------|
| `ttt/video` | 672 | One row per YouTube video |
| `ttt/rounds` | 4,104 | One row per round, partitioned by `video_link` |
| `ttt/players` | 30 | Player roster |
| `ttt/roles` | 49 | Role definitions (name, team, description) |
| `ttt/winnerchartdetails` | 20 | Colours/labels for the win-rate chart |
| `ttt/plays` | 13,950 | Flattened: `(video_id, round_number, player, role)`, partitioned by `video_id` |

The loader always runs with `mode="overwrite"` — safe to re-run.

### Reading TTT data back

```python
from app.ttt.storage import TTTPlaysWriter, TTTVideoWriter

plays = TTTPlaysWriter().read()
plays.show(5)

videos = TTTVideoWriter().read()
videos.show(5)
```

---

## Delta Lake table paths

All tables are stored under `DELTA_BASE_PATH` (default `file:///data/delta`).

| Domain | Table path |
|--------|-----------|
| Torn user | `torn/user` |
| Torn faction | `torn/faction` |
| Torn travel | `torn/travel` |
| Civilization 6 | `gameanalysis/civ6` |
| Galactic Civilizations 4 | `gameanalysis/galciv4` |
| GalCiv4 Supernova | `gameanalysis/galciv4_supernova` |
| Humankind | `gameanalysis/humankind` |
| Age of Wonders 4 | `gameanalysis/aow4` |
| Northgard | `gameanalysis/northgard` |
| TTT videos | `ttt/video` |
| TTT rounds | `ttt/rounds` |
| TTT players | `ttt/players` |
| TTT roles | `ttt/roles` |
| TTT winner chart | `ttt/winnerchartdetails` |
| TTT plays | `ttt/plays` |

---

## dbt transformations

The `dbt/` directory contains the transformation layer. Raw Delta Lake data is staged and cleaned, then aggregated into mart models for analysis.

### Setup

```bash
cd dbt
pip install dbt-core dbt-duckdb dbt-databricks
dbt deps
```

`profiles.yml` is in `dbt/` and has two targets:

| Target | Adapter | When to use |
|--------|---------|-------------|
| `dev` (default) | `dbt-duckdb` | Local development — reads Delta files directly via DuckDB |
| `prod` | `dbt-databricks` | Databricks — reads Unity Catalog tables |

Set `DATABRICKS_HOST`, `DATABRICKS_HTTP_PATH`, and `DATABRICKS_TOKEN` in `.env` for the prod target.

### Running models

```bash
cd dbt

# Run everything
dbt run

# Run a specific domain
dbt run --select staging.torn
dbt run --select marts.games

# Run a single model
dbt run --select stg__torn_user__attacks

# Test
dbt test
```

### Model structure

```
dbt/models/
├── staging/
│   ├── torn/       # Unnest raw Torn API responses by endpoint
│   ├── games/      # Passthrough + type casting for flat game data
│   └── ttt/        # Stage TTT Delta Lake tables into clean views
└── marts/
    ├── torn/       # War attacks, travel spend analysis
    └── games/      # Win rates and difficulty breakdown across all games
```

The `delta_source('path')` macro handles the difference between DuckDB (`delta_scan(...)`) and Databricks (Unity Catalog reference) automatically based on the active target.
