WITH base AS (
    SELECT game, difficulty, score, turns, victory_condition AS outcome FROM {{ ref('stg__games__civ6') }}
    UNION ALL
    SELECT game, difficulty, score, turns, victory_condition AS outcome FROM {{ ref('stg__games__galciv4') }}
    UNION ALL
    SELECT game, difficulty, score, turns, victory_condition AS outcome FROM {{ ref('stg__games__galciv4_supernova') }}
    UNION ALL
    SELECT game, difficulty, NULL AS score, NULL AS turns, NULL AS outcome FROM {{ ref('stg__games__humankind') }}
    UNION ALL
    SELECT game, difficulty, NULL AS score, NULL AS turns, NULL AS outcome FROM {{ ref('stg__games__aow4') }}
    UNION ALL
    SELECT game, difficulty, NULL AS score, NULL AS turns, outcome_condition AS outcome FROM {{ ref('stg__games__northgard') }}
)

SELECT
    game,
    difficulty,
    COUNT(*)                        AS games_played,
    ROUND(AVG(score), 0)            AS avg_score,
    MIN(score)                      AS min_score,
    MAX(score)                      AS max_score,
    ROUND(AVG(turns), 0)            AS avg_turns
FROM base
GROUP BY game, difficulty
ORDER BY game, difficulty
