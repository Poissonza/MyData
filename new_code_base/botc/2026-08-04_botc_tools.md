# BotC Data Entry Tools

Tools for entering Blood on the Clocktower game data into the per-game YAML schema.

## Folder structure

```
botc/
  games/          ← one .yml file per game (e.g. 240920.yml)
  reference/
    players.yml   ← master player list (add new players here)
    roles.yml     ← role definitions with alignment and set
  botc_cli.py     ← command-line entry tool
  app.py          ← Streamlit web UI entry tool
```

---

## Data entry workflow

Data for a game arrives in three waves. Both tools are built around these:

| Wave | When | What |
|------|------|------|
| **New Game** | Before/start of video | Video metadata, player names, seating positions |
| **Add Day** | As you watch | Night kills, executions, nominations, extra info per day |
| **Reveal** | End of video | Evil roles, minion/townsfolk actions, game result |

---

## CLI — `botc_cli.py`

A numbered-list terminal tool. Validates all player and role names against the reference files so no typos can slip through.

### Start

```bash
uv run python botc/botc_cli.py
```

### Commands

| Command | What it does |
|---------|-------------|
| `new-game` | Prompts for video info and players, creates a new `games/<id>.yml` with no days (start with Add Day for day 1) |
| `add-day` | Appends a new day entry to an existing game — night kill, execution, extra info, nominations, optional action scaffolds |
| `reveal` | Fills in end-of-game data on an existing game — evil player roles, minion/townsfolk actions, result |
| `quit` | Exits |

### How selection works

All player and role fields use a numbered list — type the number, not the name:

```
Pick a player:
  1. Ben
  2. Briony
  3. Nilsey
> 3
```

Fields marked `(Enter to skip)` accept a blank entry to leave a placeholder.

---

## Streamlit app — `app.py`

A browser-based form UI. Same three modes as the CLI, presented as tabs. Better for nominations (add rows with a button) and for reviewing existing values during a reveal.

### Start

```bash
uv run streamlit run botc/app.py
```

Opens at `http://localhost:8501` in your browser.

### Tabs

| Tab | What it does |
|-----|-------------|
| **New Game** | Form for video metadata and player/role assignment. Click **Create Game** to write the file. |
| **Add Day** | Pick a game and day number, fill in night kill, execution, extra info rows, and nomination rows. Click **Save Day** to append. |
| **Reveal** | Pick a game, update player roles, fill in minion/townsfolk action placeholders, set the result. Click **Save Reveal** to write. |
| **Games** | Overview table of all captured games (video name, date, length, outcome), summary stats (win split, avg days, per-player and per-role win rates), and a per-game drill-down of players and days. |
| **Players** | Add a new player to `reference/players.yml` (duplicate names rejected, case-insensitive). |
| **Roles** | Add a new role (name, alignment, set, description) to `reference/roles.yml`. |

### Dynamic rows

Use the **+ Extra info row** and **+ Nomination row** buttons to add as many entries as needed before saving.

---

## Reference files

Add a new player (via the **Players** tab or by editing `reference/players.yml`) before creating a game that includes them — both tools load this list for validation.

Add a new role (via the **Roles** tab or by editing `reference/roles.yml`, with `alignment` and `set`) before using it in a game.
