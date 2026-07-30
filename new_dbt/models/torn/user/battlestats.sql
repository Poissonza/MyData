{{
    config(
        alias = "user_battlestats"
    )
}}
SELECT 
battlestats.defense,
battlestats.dexterity,
battlestats.speed,
battlestats.strength,
battlestats.total,
ts
FROM delta.`/Volumes/torn/user/user_api_files/battlestats`