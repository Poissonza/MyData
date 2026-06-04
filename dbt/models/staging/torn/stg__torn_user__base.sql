WITH raw AS (
    SELECT
        retrieved_at,
        data
    FROM {{ delta_source('torn/user') }}
    WHERE endpoint = ''
)

SELECT
    data.id,
    data.name,
    data.level,
    data.gender,
    data.rank,
    data.role,
    data.age,
    data.awards,
    data.donator_status,
    data.forum_posts,
    data.friends,
    data.enemies,
    data.honor_id,
    data.image,
    data.karma,
    data.revivable,
    data.faction_id,
    data.life.current                   AS life_current,
    data.life.maximum                   AS life_maximum,
    data.last_action.status             AS last_action_status,
    data.last_action.relative           AS last_action_relative,
    TO_TIMESTAMP(data.last_action.timestamp) AS last_action_at,
    TO_TIMESTAMP(data.signed_up)        AS signed_up_at,
    data.spouse.id                      AS spouse_id,
    data.spouse.name                    AS spouse_name,
    data.spouse.status                  AS spouse_status,
    data.spouse.days_married            AS spouse_days_married,
    retrieved_at
FROM raw
