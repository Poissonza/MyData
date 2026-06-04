SELECT
    id,
    log,
    TO_TIMESTAMP(timestamp)     AS event_at,
    origin,
    destination,
    travel_method,
    duration
FROM {{ delta_source('torn/travel') }}
WHERE category = 'travel'
