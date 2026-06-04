WITH trips AS (
    SELECT
        destination,
        travel_method,
        COUNT(*)                    AS trip_count
    FROM {{ ref('stg__torn_travel__trips') }}
    GROUP BY destination, travel_method
),

purchases AS (
    SELECT
        destination,
        item,
        SUM(quantity)               AS total_quantity,
        SUM(cost_total)             AS total_spend,
        COUNT(*)                    AS purchase_count
    FROM {{ ref('stg__torn_travel__purchases') }}
    GROUP BY destination, item
)

SELECT
    p.destination,
    p.item,
    p.total_quantity,
    p.total_spend,
    p.purchase_count,
    t.trip_count,
    ROUND(p.total_spend / NULLIF(t.trip_count, 0), 2) AS avg_spend_per_trip
FROM purchases AS p
LEFT JOIN trips AS t USING (destination)
ORDER BY p.total_spend DESC
