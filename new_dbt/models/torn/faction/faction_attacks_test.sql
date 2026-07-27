SELECT
    attack.id as id,
    attack.code as code,
    attack.started as started,
    attack.ended as ended,
    attack.result as result,
    attack.attacker as attacker,
    attack.defender as defender,
    attack.respect_gain as respect_gain,
    attack.respect_loss as respect_loss,
    attack.chain as chain,
    attack.is_interrupted as is_interrupted,
    attack.is_raid as is_raid,
    attack.is_ranked_war as is_ranked_war,
    attack.is_stealthed as is_stealthed,
    attack.modifiers as modifiers
FROM (
  SELECT explode(attacks) as attack
  FROM delta.`/Volumes/torn/faction/faction_api_files/attacks/`
)
