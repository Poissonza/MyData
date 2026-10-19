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

---

## Possible improvements

Target data model from a review of the data (2026-10-19). Nothing here is implemented yet, and the table definitions are still being drafted. The YAML files stay the source of truth and will be ingested into a local Delta Lake with Spark.

### Decisions so far

- **One YAML file per table.** Each file covers all games, with `game_id` on every row, the same pattern `players.yml` and `roles.yml` already use. This replaces the nested one-file-per-game layout, so the source matches the target model and ingestion is close to a straight copy.
- **One row at a time.** The app adds a single row (a nomination, a death, a piece of info) and saves it straight away, instead of building a whole day first. Rows can be completed later.
- **Day is the grain.** Day N covers the night before it plus the day (dusk is only nominations and executions). Days start at 1; there is no Day 0.
- **One video is one game.** The rare video with more than one game gets one Video row and a Game row per game, never a made-up second video.
- **A player's team comes from their role.** No team column at setup. Any exception (a setup effect such as Bounty Hunter, or a Traveller if one ever appears) is recorded as a Day 1 role swap with `cause: setup`.
- **Extra information stays free text.** What is revealed, and how much, depends on the role, and it can refer to players or to roles. The player behind an entry can be found by joining its role to the player's role on that day; a Drunk's info joins on their *believed* role.

### Tables

| File | Kind | Key | Columns |
|---|---|---|---|
| `players.yml` | Reference | `player_id` | name |
| `roles.yml` | Reference | `role_id` | name, character_type (Townsfolk / Outsider / Minion / Demon / Traveller), edition, description |
| `nomination_results.yml` | Reference | `result_id` | name, counts_as_execution |
| `win_conditions.yml` | Reference | `win_condition_id` | name, winning_team (Good / Evil / either) |
| `videos.yml` | Dimension | `video_id` | name, date, length, members |
| `games.yml` | Dimension | `game_id` | video_id, game_number |
| `game_results.yml` | Event | `game_id` | winning_team, win_condition_id. One row per game, added when the game ends. |
| `game_players.yml` | Link | `game_id, player_id` | seat (unique per game), starting_role_id, believed_role_id (Drunk / Lunatic / Marionette) |
| *Day* | Derived | `game_id, day` | not stored. Built in silver from the `day` values: players_alive, execution_happened, deaths |
| `role_swaps.yml` | Event | `role_swap_id` | game_id, day, player_id, new_role_id (optional), new_team (optional), cause |
| `night_actions.yml` | Event | `night_action_id` | game_id, day, seq, role_id, player_id (who used it), target_player_id |
| `nominations.yml` | Event | `nomination_id` | game_id, day, seq, nominator_id, nominee_id, votes, ghost_votes, result_id |
| `deaths.yml` | Event | `death_id` | game_id, day, player_id, timing (night / day), cause (demon, execution, or the role whose ability caused it) |
| `extra_info.yml` | Event | `extra_info_id` | game_id, day, seq, role_id, info (free text). Demon bluffs live here. |

Notes:

- Every player column in an event table must match a row in `game_players.yml` for that game, so nobody can be nominated, killed or targeted in a game they weren't in. The app enforces this by offering only that game's players in its dropdowns.
- **Role swaps** covers role changes (Imp star-pass, Fang Gu jump, Pit-Hag, Barber, Snake Charmer) and team-only changes (Goon, Cult Leader), so new_role_id and new_team are both optional. A derived **player_state** table (`valid_from_day` / `valid_to_day`, built with a `lead()` window, the SCD2 pattern) gives each player's role and team on any day. Win stats should use the final state, not the starting role.
- **Deaths** replaces the single `night_kill` / `execution` fields, which can't record several deaths in a night, ability deaths (Slayer, Virgin, Lunatic), resurrections or a failed kill.
- **Game results** is a separate table rather than a `winning_team` column on `games.yml`, because the result is only known at the very end. It is one insert when the game finishes, so `games.yml` never needs editing after setup. A game with no results row is still in progress, and win-rate queries join to `game_results`, so unfinished games drop out instead of counting as losses. The final day is not stored: it is the highest `day` across the event tables for that game.
- **Win conditions** lists the possible endings, so they can be counted: e.g. demon executed, demon killed at night (Slayer), final two alive, Saint executed, Mayor win, Evil Twin, a good player executed by a Virgin… `winning_team` on the reference row is the usual winner for that ending. It can be `either` where an ending can go to both teams, and in that case the result row's `winning_team` decides.
- **Nomination results** fixes the free-text values in use today, e.g. `Not Enough Votes` (15) vs `Not enough votes` (1), plus `Marked`, `Tied`, `Executed`, `Virgin Execution` and `Disrupted by a Slayer shot on the Demon`.
- In `roles.yml`, `alignment` becomes `character_type`; it holds the character type, not the team.

Example rows:

```yaml
# nominations.yml
nominations:
  - nomination_id: 42
    game_id: <video_id>
    day: 2
    seq: 1
    nominator_id: duncan
    nominee_id: zylus
    votes: 3
    ghost_votes: 0
    result_id: marked

# role_swaps.yml
role_swaps:
  - role_swap_id: 3
    game_id: <video_id>
    day: 2
    player_id: briony
    new_role_id: fanggu
    new_team: null           # role-only change
    cause: Fang Gu jump
```

### IDs

| Table | Key | How it's set |
|---|---|---|
| Player | `player_id` | Assigned by the Players tab when the player is added: an integer (max + 1) or a slug. Never changes. |
| Roles | `role_id` | The official lowercase character ID (`fortuneteller`, `scarletwoman`, `fanggu`, `pithag`). |
| Nomination Results | `result_id` | A slug (`executed`, `not_enough_votes`, `tied`). |
| Win Conditions | `win_condition_id` | A slug (`demon_executed`, `final_two`, `saint_executed`, `mayor_win`). |
| Video | `video_id` | The YouTube video ID (the `v=` part of the URL); release date kept as its own column. |
| Game | `game_id` | Equal to `video_id`; `<video_id>-2`, `-3`, … for the rare video with more than one game. |
| Game Player | `game_id, player_id` | Natural key. |
| Event tables | `<table>_id` | An integer per table (max + 1), assigned by the app on insert. |

- **Why the YouTube ID:** today's IDs are dates, so two videos released the same day collide. `240920` and `2409202` are separate videos, kept apart only by a trailing `2`, and loaded as numbers `2409202` sorts after `241129`.
- **Role IDs** follow the official app's custom-script format: lowercase with spaces and punctuation removed (its example is `"id": "widow"`; see [release.botc.app](https://release.botc.app/)). The full list can be copied from Townsquare's character file ([roles.json](https://raw.githubusercontent.com/bra1n/townsquare/develop/src/roles.json)), the community app for running games online. Using these IDs means official role data and script JSON can be loaded later without a mapping table.
- **Each event row has its own ID** rather than a composite key. The app can find a row to edit or delete by one value, it still works if the row's day or order changes, and some combinations aren't unique (a player can die twice through a resurrection, or swap roles twice in a day).
- `game_id`, `day` and `seq` stay on event rows as normal columns. `seq` is the order within the day, set to the highest seq for that game and day plus 1, and editable to reorder.
- Max + 1 is safe while one person enters the data. It would only clash if two copies of the files were edited at the same time and then merged.
- Game files stop holding names. The app shows names in its dropdowns but saves IDs. Existing data is converted once by mapping names to IDs; an unknown name fails the conversion.
- Avoid `monotonically_increasing_id()` in Spark, because keys change on every rerun. If a numeric surrogate is wanted for a string key, use a deterministic hash, e.g. `xxhash64(player_id)`.

### Partial rows

- **Each table defines its required columns:** only the keys and the minimum that makes the row mean something. For nominations that's `game_id, day, nominator_id, nominee_id`; `votes`, `ghost_votes` and `result_id` can be added later by editing the same row (found by `nomination_id`).
- **Empty means "not entered yet"; 0 means zero.** This matters most for votes and ghost votes. Today's data has `ghost_votes: null` where 0 was probably meant, which can't be told apart from "unknown".
- **Show what's unfinished rather than storing a status.** The app lists incomplete rows (e.g. "3 nominations with no result", "players with no role" after the reveal). The same check is a data-quality query in silver. A separate status column would drift out of step with the data.
- **Order of entry:** a game and its players must exist first. After that, nominations, deaths, info, night actions and role swaps can be added in any order. The game result is added last.

### Streamlit changes

- Replace the New Game / Add Day / Reveal tabs with one **Game** page: pick a game and a current day (defaults to the latest).
- Each table gets a small form whose **Add** button saves that one row immediately.
- Below each form, an `st.data_editor` grid shows that game's rows for fixing or deleting, with dropdown columns (`SelectboxColumn`) for players, roles and results so values stay valid.
- Reveal becomes ordinary editing: set roles in the game players grid, and add night actions and role swaps whenever they're learned.
- **Safe saves:** each insert rewrites one table's file, so write to a temp file and rename it over the original. A crash mid-save then can't corrupt the file.

### Data clean-up before converting

- **Types differ between files.** 240920 and 2409202 were written by hand, so YAML reads their `id` as a number and `date` as a real date. Files created with the app or the CLI store both as quoted strings. The conversion and ingestion should cast explicitly rather than trust YAML types, and trim text (the 241115 video name has a leading space).
- **240920 and 2409202 still have a Day 0** with real first-night info; to be fixed by hand.
- **241115:** Briony is stored as `role: Imp, drunk_role: Fortune Teller`, but there is no Imp in that game and Day 2 says the Drunk became the Fang Gu. Check this once role swaps exist.
- `result.outcome` moves to `game_results.yml`; each existing game needs a win condition added by hand. `result.number_of_days` isn't carried over, because it is the highest day in the event tables.

### Ingestion into Delta (`delta-spark` / `pyspark` are already dependencies)

| Layer | Contents | Load pattern |
|---|---|---|
| Bronze | One table per YAML file: raw rows, file hash, `ingested_at` | Reload a table when its file hash changes |
| Silver | The tables above: typed, IDs checked against the reference tables and `game_players` | Start by overwriting each table from its file; later, `MERGE` on the row ID with `whenNotMatchedBySource().delete()` to handle inserts, edits and deletes in one statement |
| Gold | `day`, `player_state`, player and role win rates, win-condition frequency, demon bluff frequency, incomplete-row and unfinished-game checks | Rebuild from silver |

Optionally, check each row against a schema (e.g. pydantic) when the app saves it, so bad values are rejected at entry rather than at ingestion.
