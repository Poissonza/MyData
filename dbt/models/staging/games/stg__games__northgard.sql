SELECT
    game_name,
    CAST(date AS DATE)              AS game_date,
    clan,
    military,
    color,
    difficulty,
    map_size,
    military_path,
    events,
    opponents,
    outcome_condition,
    outcome_year,
    outcome_month,
    MAKE_DATE(outcome_year, 1, 1)   AS outcome_date,
    'northgard'                     AS game
FROM {{ delta_source('gameanalysis/northgard') }}
