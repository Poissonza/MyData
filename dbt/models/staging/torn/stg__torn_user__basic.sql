WITH raw AS (
    SELECT
        retrieved_at,
        data
    FROM {{ delta_source('torn/user') }}
    WHERE endpoint = 'basic'
)

SELECT
    data.id,
    data.name,
    data.level,
    data.gender,
    data.status.state                   AS status_state,
    data.status.description             AS status_description,
    data.status.details                 AS status_details,
    data.status.color                   AS status_color,
    data.faction.faction_id             AS faction_id,
    data.faction.faction_name           AS faction_name,
    data.faction.position               AS faction_position,
    TO_TIMESTAMP(data.last_action.timestamp) AS last_action_at,
    data.last_action.status             AS last_action_status,
    retrieved_at
FROM raw
