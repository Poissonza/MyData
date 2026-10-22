
  
    
        create or replace table `torn`.`staging`.`stg__user__attacks`
      
      
  using delta
      
      
      
      
      
      
      
      as
      SELECT id,
  code,
  started,
  CAST(from_unixtime(started) AS TIMESTAMP) AS started_timestamp,
  ended,
  from_unixtime(ended) AS ended_timestamp,
  result,
  attacker.id AS AttackerID,
  attacker.name AS AttackerName,
  attacker.level AS AttackerLevel,
  attacker.faction.id AS AttackerFactionID,
  attacker.faction.name AS AttackerFactionName,
  defender.id AS DefenderID,
  defender.name AS DefenderName,
  defender.level AS DefenderLevel,
  defender.faction.id AS DefenderFactionID,
  defender.faction.name AS DefenderFactionName
 FROM `torn`.`user`.`attacks`
  