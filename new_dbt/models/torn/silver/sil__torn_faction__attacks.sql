{{
    config(
        materialized='table',
        schema='silver',
        alias='sil__torn_faction__attacks_test'
    )
}}
WITH rw AS (
SELECT * FROM {{ ref('ranked_wars') }} QUALIFY row_number() OVER(PARTITION BY id ORDER BY ts DESC) =1
)

SELECT
    fa.id,
      `code`,
      started,
      CAST(from_unixtime(started) AS TIMESTAMP) AS startedTimeStamp,
      ended,
      CAST(from_unixtime(ended) AS TIMESTAMP) AS endedTimeStamp,
      result AS Result,
      attacker.id AS AttackerID,
      attacker.name AS AttackerName,
      attacker.level AS AttackerLevel,
      attacker.faction.id AS AttackerFactionId,
      attacker.faction.name AS AttackerFactionName,
      defender.id AS DefenderID,
      defender.name AS DefenderName,
      defender.level AS DefenderLevel,
      defender.faction.id AS DefenderFactionId,
      defender.faction.name AS DefenderFactionName,
      respect_gain AS RespectGain,
      respect_loss AS RespectLoss,
      chain,
      is_interrupted AS IsInterrupted,
      is_stealthed AS IsStealthed,
      is_raid AS IsRaid,
      is_ranked_war AS IsRankedWar,
      modifiers.fair_fight as ModifiersFairFight,
      modifiers.war as ModifiersWar,
      modifiers.retaliation as ModifiersRetaliation,
      modifiers.`group` as ModifiersGroup,
      modifiers.overseas as ModifiersOverseas,
      modifiers.chain as ModifiersChain,
      modifiers.warlord as ModifiersWarlord,
      CAST(from_unixtime(rw.start) AS TIMESTAMP) as RankedWarStart
 FROM {{ ref('faction_attacks') }} as fa
 LEFT JOIN rw ON fa.started > rw.start and fa.started < rw.end