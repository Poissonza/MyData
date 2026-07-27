SELECT
    crimes.created_at AS created_at,
    crimes.difficulty AS difficulty,
    crimes.executed_at AS executed_at,
    crimes.expired_at AS expired_at,
    crimes.id AS id,
    crimes.name AS name,
    crimes.planning_at AS planning_at,
    crimes.previous_crime_id AS previous_crime_id,
    crimes.ready_at AS ready_at,
    crimes.rewards AS rewards,
    crimes.slots AS slots,
    crimes.status AS status
FROM (
    SELECT
        EXPLODE(crimes) AS crimes
    FROM delta.`/Volumes/torn/faction/faction_api_files/crimes/`
)