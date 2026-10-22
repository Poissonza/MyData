
  
    
        create or replace table `torn`.`staging`.`stg__user__basic`
      
      
  using delta
      
      
      
      
      
      
      
      as
      SELECT gender,
  id,
  level,
  name,
  status.description AS StatusDescription,
  status.details AS StatusDetails,
  status.state AS StatusState,
  status.until AS StatusUntil,
  status.color AS StatusColor,
  timeStamp
FROM `torn`.`user`.`basic`
  