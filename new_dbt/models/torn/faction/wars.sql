{{
    config(
        materialized='incremental',
        unique_key= 'war_id'
    )
}}

SELECT 
 wars.ranked.end AS end,
 wars.ranked.factions AS factions,
 wars.ranked.start AS start,
 wars.ranked.target AS target,
 wars.ranked.war_id AS war_id,
 wars.ranked.winner AS winner
FROM delta.`/Volumes/torn/faction/faction_api_files/wars`
{% if is_incremental() %}
 WHERE wars.ranked.war_id NOT IN (SELECT war_id FROM {{this}} )
{% endif%}

