{{
    config(
        alias = 'faction_balance',
        materialization = 'incremental',
    )
}}

SELECT exploded_member.id AS id,
exploded_member.money AS money,
exploded_member.points AS points,
exploded_member.username AS username,
ts AS ts
FROM (
  SELECT explode(balance.members) AS exploded_member, ts
  FROM delta.`/Volumes/torn/faction/faction_api_files/balance`
)
{% if is_incremental() %}
WHERE ts > (SELECT max(ts) FROM {{ this }}
{% endif %}