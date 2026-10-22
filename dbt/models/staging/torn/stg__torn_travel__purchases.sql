SELECT
    id,
    log,
    TO_TIMESTAMP(timestamp)     AS event_at,
    destination,
    item,
    quantity,
    cost_each,
    cost_total
FROM {{ delta_source('torn/travel') }}
WHERE category = 'purchase'
