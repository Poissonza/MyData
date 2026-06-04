SELECT
    descriptor                      AS game_name,
    version,
    CAST(start_date AS DATE)        AS start_date,
    CAST(end_date AS DATE)          AS end_date,
    seed,
    land_percentage,
    world_size,
    world_shape,
    continent_shape,
    climate,
    number_of_continents,
    difficulty,
    pace,
    end_conditions,
    natural_wonders,
    luxury_resources,
    'humankind'                     AS game
FROM {{ delta_source('gameanalysis/humankind') }}
