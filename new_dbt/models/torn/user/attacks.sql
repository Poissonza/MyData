{{
    config(
        alias = "user_attacks",
        schema = "user",
        materialized = "incremental"
    )
}}

SELECT 
    attacks.attacker as attacker,
    attacks.chain as chain,
    attacks.code as code,
    attacks.defender as defender,
    attacks.ended as ended,
    attacks.finishing_hit_effects as finishing_hit_effects,
    attacks.id as id,
    attacks.is_interrupted as is_interrupted,
    attacks.is_raid as is_raid,
    attacks.is_ranked_war as is_ranked_war,
    attacks.is_stealthed as is_stealthed,
    attacks.is_territory_war as is_territory_war,
    attacks.modifiers as modifiers,
    attacks.respect_gain as respect_gain,
    attacks.respect_loss as respect_loss,
    attacks.result as result,
    attacks.started as started,
    attacks.territory_war_id as territory_war_id
FROM (
    SELECT 
    EXPLODE(attacks) as attacks
    FROM delta.`/Volumes/torn/user/user_api_files/attacks`
)
{% if is_incremental() %}
WHERE attacks.started > (select max(started) from {{this}})
{% endif %}