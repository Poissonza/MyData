# BotC Data Entry Tools

Tools for entering Blood on the Clocktower game data. The Streamlit app writes the relational tables in `data/`; the CLI still writes the older per-game files in `games/`.

## Folder structure

```
botc/
  data/           ← relational tables, one .yml per table (see "Data model"); used by the app
  games/          ← old format, one .yml per game (e.g. 240920.yml); used by the CLI only
  reference/      ← old player and role lists; used by the CLI only
  botc_cli.py     ← command-line entry tool (old format)
  app.py          ← Streamlit web UI entry tool
```

---

## Data entry workflow

Data for a game is captured one row at a time while watching, in roughly this order:

| When | What | Where in the app |
|------|------|------|
| Before the video | Video, game, and the players with their seats | **Videos & Games**, then **Game Entry → Players** |
| As you watch | Deaths, nominations (votes and result can follow), extra info | **Game Entry**, with the current day set at the top |
| At the reveal | Starting roles, believed roles, night actions, role swaps | **Game Entry** (edit the Players grid, add actions and swaps) |
| At the end | Winning team and win condition | **Game Entry → Result** |

---

## CLI — `botc_cli.py`

A numbered-list terminal tool. Validates all player and role names against the reference files so no typos can slip through.

> **Note:** the CLI still uses the old per-game format (`games/` and `reference/`), not the tables in `data/`.

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

A browser-based UI over the tables in `data/`. Every form adds and saves one row straight away, and every table can be fixed afterwards in an editable grid.

### Start

```bash
uv run streamlit run botc/app.py
```

Opens at `http://localhost:8501` in your browser.

### Tabs

| Tab | Sub-tabs | What it does |
|-----|----------|-------------|
| **Game Entry** | Players, Deaths, Nominations, Night Actions, Extra Info, Role Swaps, Result | Pick a game and the current day (defaults to the last day recorded). Each sub-tab has an **Add** form for one row and a grid of that game's rows. The toggle limits the grids to the current day. |
| **Games Summary** | Games, Players, Roles & endings, Game detail | Headline numbers (games, finished, Good/Evil wins, average days), an overview of every game, player win rates (using the final team after role swaps), starting-role stats, how games ended, and a per-game drill-down with a day-by-day table and expanders. |
| **Videos & Games** | Videos, Games | Add and edit videos, and the games in them. A game's number fills in as the next one for that video if left empty. |
| **Reference** | Players, Roles, Nomination Results, Win Conditions | Add and edit the lookup tables. A role's default team fills in from its character type if left empty. |
| **Checks** | | Data problems (broken references, duplicates, invalid values, e.g. from editing the YAML by hand) and a list of what is still to fill in (missing seats, roles, votes, results, causes of death, games with no result). |

### Forms and grids

- Fields marked `*` are required; everything else can be left empty and filled in later. Empty means "not entered yet"; enter 0 for zero.
- Player fields in event forms only offer the players in that game, so add players (with their starting roles) to the game first.
- The role on a night action, an extra info entry or a cause of death only offers roles in play on the current day: starting roles, believed roles (e.g. the Drunk's Townsfolk), and roles gained through a role swap on that day or earlier. Swapped-out roles stay in the list, since they can still come up (e.g. as the cause of that day's death). Grids show rows from several days, so their dropdowns list every role the game has had, but each row is checked against its own day when saved. A night action's target role and a role swap's new role still offer every role, because the Pit-Hag, Cerenovus and Philosopher can choose characters not in play.
- In a grid, edit cells or select rows and delete them, then click **Save changes**. Nothing is written until you save, and all rows are checked first.
- A row can't be deleted while something else still uses it (e.g. a player who has a nomination in that game).
- A role swap needs a new role, a new team, or both. A result's winning team fills in from the win condition, unless it is `Either`.
- Saves go to a temp file that is then renamed over the table, so a crash mid-save can't corrupt it.
- Saving a table rewrites the whole file, so comments inside a data file (e.g. the section headings in `win_conditions.yml`) are not kept.

---

## Data model (in progress)

The relational tables live in `data/`, one YAML file per table. As of 2026-10-19 they are built but only partly filled: game 1 (Vengeful Vigormortis, previously `games/241101.yml`) is being moved across first. The Streamlit app reads and writes `data/`. The CLI still uses the old per-game files in `games/` and the lists in `reference/`. The YAML files are the source for a local Delta Lake built with Spark.

### Decisions

- **One YAML file per table.** Each file covers all games, with `game_id` on every event row. The file's top-level key matches its file name (`videos.yml` → `videos:`).
- **One row at a time.** The app will add a single row (a nomination, a death, a piece of info) and save it straight away, instead of building a whole day. Rows can be completed later.
- **Day is the grain.** Day N covers the night before it plus the day (dusk is only nominations and executions). Days start at 1; there is no Day 0.
- **Day is not stored.** It is derived in silver (see below). A `days.yml` would only be worth adding to record facts about the day itself, such as the video time each day starts.
- **One video is one game.** The rare video with more than one game gets one Video row and a Game row per game (`game_number`), never a made-up second video.
- **A player's starting team comes from their role** (`roles.alignment`). No team column at setup. Any exception (a setup effect such as Bounty Hunter, or a Traveller if one ever appears) is recorded as a Day 1 role swap with `cause: setup`.
- **Extra information stays free text.** What is revealed, and how much, depends on the role, and it can refer to players or to roles. The player behind an entry can be found by joining its role to the player's role on that day. **A Drunk's (or Lunatic's, Marionette's) info is recorded under their real role** (e.g. `Drunk`, not `Empath`), so it always points at one player, even if the game also has a real Empath, and is clearly marked as unreliable. Their believed role is on `game_players.believed_role_id`.
- **No `seq` column.** Row IDs are assigned in entry order, so `id` already gives the order within a game and day. Add `seq` only if events ever need reordering after entry.
- **Fixed values are capitalised:** `Good` / `Evil` / `Either`, `Night` / `Day`, `Demon`.
- **Empty tables are `[]`**, with the columns listed in a comment at the top of the file, never a row of nulls.

### Tables

| File | Kind | Columns | References |
|---|---|---|---|
| `players.yml` | Reference | id, name | |
| `roles.yml` | Reference | id, name, character_type (Townsfolk / Outsider / Minion / Demon / Traveller / Fabled), alignment (Good / Evil, the default team), set, description | |
| `nomination_results.yml` | Reference | id, name, block_effect (marks / clears / none / executes_nominator) | |
| `win_conditions.yml` | Reference | id, name, winning_team (Good / Evil / Either), role_id, description | role_id → roles |
| `videos.yml` | Dimension | id, name, date, length, members | |
| `games.yml` | Dimension | id, game_number, video_id | video_id → videos |
| `game_players.yml` | Link | id, game_id, player_id, seat, starting_role_id, believed_role_id | games, players, roles |
| `game_results.yml` | Event | id, game_id, winning_team, win_condition_id | games, win_conditions |
| `deaths.yml` | Event | id, game_id, day, player_id, timing, cause_type, cause_role_id | games, players, roles |
| `nominations.yml` | Event | id, game_id, day, nominator_id, nominee_id, votes, ghost_votes, result_id | games, players, nomination_results |
| `night_actions.yml` | Event | id, game_id, day, role_id, player_id, target_player_id, target_role_id | games, roles, players |
| `extra_info.yml` | Event | id, game_id, day, role_id, info | games, roles |
| `role_swaps.yml` | Event | id, game_id, day, player_id, new_role_id, new_team, cause | games, players, roles |

Notes:

- **Game players:** one row per player per game; `seat` must be unique within a game. `believed_role_id` covers the Drunk, Lunatic and Marionette. Every player column in an event table must match a row here for that game, so nobody can be nominated, killed or targeted in a game they weren't in.
- **Game results:** one row per game, added when the game ends, so `games.yml` never needs editing after setup. A game with no result row is still in progress, and win-rate queries join to `game_results`, so unfinished games drop out instead of counting as losses. The final day is not stored; it is the highest `day` across the event tables for that game.
- **Win conditions:** 18 endings. 4 come from the core rules (demon executed, demon killed by an ability, demon died with no successor, final two), 13 from specific characters (with `role_id` set, e.g. Mayor, Saint, Klutz, Evil Twin, Vortox, Leviathan, Damsel, Goblin, Mastermind, Atheist, Cult Leader, Fiddler), plus `Other`. `winning_team` is the usual winner for that ending; where it is `Either`, the result row's `winning_team` decides. The Heretic isn't listed because it flips the result rather than being an ending: record the actual ending and the real winner.
- **Deaths** replace the single `night_kill` / `execution` fields, so several deaths in a night, ability deaths (Slayer, Virgin, Lunatic), resurrections and failed kills can all be recorded. `cause_type` is how they died (Demon / Execution / Ability); `cause_role_id` is the role responsible, where there is one.
- **Night actions:** `player_id` is who used the ability. `target_role_id` is for abilities that choose a role (Pit-Hag, Cerenovus, Philosopher).
- **Role swaps** cover role changes (Imp star-pass, Fang Gu jump, Pit-Hag, Barber, Snake Charmer) and team-only changes (Goon, Cult Leader), so `new_role_id` and `new_team` are both optional. A derived **player_state** table (`valid_from_day` / `valid_to_day`, built with a `lead()` window, the SCD2 pattern) gives each player's role and team on any day. Win stats should use the final state, not the starting role.
- **Nomination results** record what happened at that vote, never "Executed", so a nomination row is written once and never updated. Each result has a `block_effect`:

  | block_effect | Meaning | Results |
  |---|---|---|
  | `marks` | The nominee goes on the block, replacing anyone already there | Marked |
  | `clears` | The block is emptied | Tied |
  | `none` | No change | Not Enough Votes (add others such as a Slayer shot ending the game here) |
  | `executes_nominator` | The nominator is executed at once and the day ends | Virgin triggered |

- **Executions are worked out, not stored.** If a day has an `executes_nominator` nomination, its nominator was executed and no nominations may follow it that day. Otherwise the day's nominations are replayed in entry order: `marks` puts the nominee on the block, `clears` empties it, and whoever is on the block at the end of the day was executed. A player marked and then out-voted is just two Marked rows; the last one wins.
- **Execution and death are separate.** The execution comes from the nominations; whether the player died goes in `deaths.yml` (`cause_type: Execution`, with `cause_role_id` set to the Virgin for a Virgin execution). Some executed players don't die (Fool, Pacifist, Zombuul, Sailor, a Tea Lady neighbour), so an execution with no death row is flagged for checking rather than treated as an error. A death by execution of someone the nominations don't put on the block is flagged too.
- **Not executions:** a Witch-cursed nominator *dies* (`cause_type: Ability`, `cause_role_id` Witch) and the nomination carries on normally. A Virgin that doesn't trigger (non-Townsfolk nominator, Virgin drunk, poisoned or already used) is an ordinary nomination.

Example rows:

```yaml
# nominations.yml
nominations:
  - id: 1
    game_id: 1
    day: 3
    nominator_id: 1
    nominee_id: 1
    votes: 1
    ghost_votes: null        # not entered yet; 0 would mean zero
    result_id: 1

# deaths.yml
deaths:
  - id: 1
    game_id: 1
    day: 2
    player_id: 2
    timing: Night
    cause_type: Demon
    cause_role_id: 121       # Vigormortis
```

### IDs

- **Every table has an integer `id`**, assigned as max + 1 when a row is added. IDs never change and are never reused.
- **Role IDs are fixed.** `roles.yml` holds 135 roles: Acrobat (1) and Recluse (2), then the rest of `reference/roles.yml` in alphabetical order, then Fiddler (135, Fabled). New roles are added at the end, never renumbered.
- **Each event row has its own ID** rather than a composite key. The app can find a row to edit or delete by one value, it still works if the row's day changes, and some combinations aren't unique (a player can die twice through a resurrection, or swap roles twice in a day).
- **Max + 1 is safe while one person enters the data.** It would only clash if two copies of the files were edited at the same time and then merged.
- **Integer video IDs** avoid the old problem of date-based IDs colliding (`240920` and `2409202` were separate videos released the same day). They don't stop the same video being entered twice, so consider a `youtube_id` or `url` column on `videos.yml` as a unique natural key.
- **The data stores IDs, not names.** The app will show names in its dropdowns but save IDs.
- **In Spark,** avoid `monotonically_increasing_id()`, because keys change on every rerun. The YAML IDs are used as the keys.

### Partial rows

- **Each table defines its required columns:** only the keys and the minimum that makes the row mean something. For nominations that's `game_id, day, nominator_id, nominee_id`; `votes`, `ghost_votes` and `result_id` can be added later by editing the same row.
- **Empty means "not entered yet"; 0 means zero.** This matters most for votes and ghost votes.
- **Show what's unfinished rather than storing a status.** The app lists incomplete rows (e.g. "3 nominations with no result", "players with no seat"). The same check is a data-quality query in silver.
- **Order of entry:** the video, the game and its players must exist first. After that, deaths, nominations, info, night actions and role swaps can be added in any order. The game result is added last.

### Checks

Run these whenever data is added (a check script exists and passes on the current data):

- Each file's top-level key matches its file name.
- IDs are present and unique in every table.
- Every `*_id` column points at an existing row in the table it references.
- Every player in deaths, nominations, night actions and role swaps is in `game_players` for that game.
- Seats are unique within a game.
- No nomination follows an immediate execution (Virgin) on the same day.
- A Tied result only follows a Marked one on the same day (there must be someone on the block to tie with).
- Every nomination has a vote count, except an immediate execution (Virgin), which has no vote. Ghost votes are 0 when nobody voted from the dead, and empty only when not known.
- Flagged for checking: an executed player with no death row, and a death by execution of a player the nominations don't put on the block.

### YAML gotchas

- **Quote video lengths** (`length: '00:55:01'`). PyYAML reads an unquoted value of an hour or more, such as `1:05:42`, as a number of seconds (3942). Alternatively, store `length_seconds`.
- **Quote dates** (`'2024-11-01'`) so they always load as text and are cast explicitly in silver. The old hand-written files mix real dates and strings.

### Still to do

- Move the remaining games across from `games/` (240920, 2409202, 241018, 241115, 241129), then retire `games/`, `reference/` and the CLI (or move the CLI onto `data/`).
- Add the remaining players, any other nomination results you need, and game 1's events.
- **240920 and 2409202 still have a Day 0** with real first-night info; renumber or merge into Day 1 when moving them across.
- **241115:** Briony is stored as `role: Imp, drunk_role: Fortune Teller`, but there is no Imp in that game and Day 2 says the Drunk became the Fang Gu. Record this with a role swap when moving it.
- **Game 1's win condition** is 1 (Demon executed), but Kirsty (Vigormortis) was executed on Day 1 and the game ran to Day 3. Check whether "Demon killed by an ability" or another ending is right.
- **Old `result.number_of_days`** isn't carried over, because it is the highest day in the event tables.

### Ingestion into Delta (`delta-spark` / `pyspark` are already dependencies)

| Layer | Contents | Load pattern |
|---|---|---|
| Bronze | One table per YAML file: raw rows, file hash, `ingested_at` | Reload a table when its file hash changes |
| Silver | The tables above: typed, with the checks above applied | Start by overwriting each table from its file; later, `MERGE` on `id` with `whenNotMatchedBySource().delete()` to handle inserts, edits and deletes in one statement |
| Gold | `day` (days 1 to the last day per game via `sequence` + `explode`, with players alive, deaths, nominations, whether an execution happened), `player_state`, player and role win rates, win-condition frequency, demon bluff frequency, incomplete-row and unfinished-game checks | Rebuild from silver |

Optionally, check each row against a schema (e.g. pydantic) when the app saves it, so bad values are rejected at entry rather than at ingestion.
