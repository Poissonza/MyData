SELECT
    name                            AS game_name,
    realm,
    player_distance,
    players,
    difficulty,
    turn_system,
    faction,
    opponents,
    'aow4'                          AS game
FROM {{ delta_source('gameanalysis/aow4') }}
