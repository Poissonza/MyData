SELECT
    p.round_link                    AS round_id,
    p.player_link                   AS player_id,
    p.role_link                     AS role_id,
    pl.name                         AS player_name,
    r.name                          AS role_name
FROM {{ source('ttt', 'play') }}        AS p
LEFT JOIN {{ source('ttt', 'player') }} AS pl ON p.player_link = pl.id
LEFT JOIN {{ source('ttt', 'role') }}   AS r  ON p.role_link   = r.id
