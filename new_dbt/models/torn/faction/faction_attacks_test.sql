SELECT
    attack.attacker.faction.id as attacker_faction_id,
    attack.attacker.faction.name as attacker_faction_name
FROM (
  SELECT explode(attacks) as attack
  FROM delta.`/Volumes/torn/faction/faction_api_files/faction_attacks/`
)