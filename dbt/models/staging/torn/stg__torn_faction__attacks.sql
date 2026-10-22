WITH raw AS (
    SELECT
        retrieved_at,
        UNNEST(data.attacks) AS attack
    FROM {{ delta_source('torn/faction') }}
    WHERE endpoint = 'attacks'
)

SELECT
    attack.id                               AS attack_id,
    attack.code,
    attack.started                          AS started_epoch,
    TO_TIMESTAMP(attack.started)            AS started_at,
    attack.ended                            AS ended_epoch,
    TO_TIMESTAMP(attack.ended)              AS ended_at,
    attack.result,
    attack.attacker.id                      AS attacker_id,
    attack.attacker.name                    AS attacker_name,
    attack.attacker.level                   AS attacker_level,
    attack.attacker.faction.id              AS attacker_faction_id,
    attack.attacker.faction.name            AS attacker_faction_name,
    attack.defender.id                      AS defender_id,
    attack.defender.name                    AS defender_name,
    attack.defender.level                   AS defender_level,
    attack.defender.faction.id              AS defender_faction_id,
    attack.defender.faction.name            AS defender_faction_name,
    attack.respect_gain,
    attack.respect_loss,
    attack.chain,
    attack.is_interrupted,
    attack.is_stealthed,
    attack.is_raid,
    attack.is_ranked_war,
    attack.modifiers.fair_fight             AS modifier_fair_fight,
    attack.modifiers.war                    AS modifier_war,
    attack.modifiers.retaliation            AS modifier_retaliation,
    attack.modifiers.group                  AS modifier_group,
    attack.modifiers.overseas               AS modifier_overseas,
    attack.modifiers.chain                  AS modifier_chain,
    attack.modifiers.warlord                AS modifier_warlord,
    retrieved_at
FROM raw
