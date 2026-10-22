WITH civ6 AS (
    SELECT
        game,
        difficulty,
        victory_condition,
        score,
        turns,
        CASE WHEN victory_condition IS NOT NULL AND victory_condition != 'R' THEN 1 ELSE 0 END AS is_win
    FROM {{ ref('stg__games__civ6') }}
),

galciv4 AS (
    SELECT
        game,
        difficulty,
        victory_condition,
        score,
        turns,
        CASE WHEN victory_condition IS NOT NULL AND victory_condition != '' THEN 1 ELSE 0 END AS is_win
    FROM {{ ref('stg__games__galciv4') }}
),

galciv4_supernova AS (
    SELECT
        game,
        difficulty,
        victory_condition,
        score,
        turns,
        CASE WHEN victory_condition IS NOT NULL AND victory_condition != '' THEN 1 ELSE 0 END AS is_win
    FROM {{ ref('stg__games__galciv4_supernova') }}
),

humankind AS (
    SELECT
        game,
        difficulty,
        NULL                        AS victory_condition,
        NULL                        AS score,
        NULL                        AS turns,
        1                           AS is_win
    FROM {{ ref('stg__games__humankind') }}
),

aow4 AS (
    SELECT
        game,
        difficulty,
        NULL                        AS victory_condition,
        NULL                        AS score,
        NULL                        AS turns,
        1                           AS is_win
    FROM {{ ref('stg__games__aow4') }}
),

northgard AS (
    SELECT
        game,
        difficulty,
        outcome_condition           AS victory_condition,
        NULL                        AS score,
        NULL                        AS turns,
        1                           AS is_win
    FROM {{ ref('stg__games__northgard') }}
),

all_games AS (
    SELECT * FROM civ6
    UNION ALL SELECT * FROM galciv4
    UNION ALL SELECT * FROM galciv4_supernova
    UNION ALL SELECT * FROM humankind
    UNION ALL SELECT * FROM aow4
    UNION ALL SELECT * FROM northgard
)

SELECT
    game,
    difficulty,
    COUNT(*)                        AS games_played,
    SUM(is_win)                     AS wins,
    ROUND(
        100.0 * SUM(is_win) / NULLIF(COUNT(*), 0), 1
    )                               AS win_pct,
    ROUND(AVG(score), 0)            AS avg_score,
    ROUND(AVG(turns), 0)            AS avg_turns
FROM all_games
GROUP BY game, difficulty
ORDER BY game, difficulty
