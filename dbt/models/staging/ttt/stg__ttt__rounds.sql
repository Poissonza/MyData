SELECT
    r.id                            AS round_id,
    r.round_number,
    r.video_link,
    r.winner,
    r.time_stamp,
    v.date                          AS video_date,
    v.server_type,
    w.colour                        AS winner_colour,
    w.label                         AS winner_label
FROM {{ source('ttt', 'round') }}       AS r
LEFT JOIN {{ source('ttt', 'video') }}  AS v ON r.video_link = v.id
LEFT JOIN {{ source('ttt', 'winnerchartdetails') }} AS w ON r.winner = w.winner_id
