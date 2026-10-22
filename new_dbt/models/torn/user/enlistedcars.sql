{{
    config(
        alias = "user_enlistedcars"
    )
}}

SELECT  
    enlistedcars.acceleration AS acceleration,
    enlistedcars.braking AS braking,
    enlistedcars.car_item_id AS car_item_id,
    enlistedcars.car_item_name AS car_item_name,
    enlistedcars.car_name AS car_name,
    enlistedcars.class AS class,
    enlistedcars.dirt AS dirt,
    enlistedcars.handling AS handling,
    enlistedcars.id AS id,
    enlistedcars.is_removed as is_removed,
    enlistedcars.parts AS parts,
    enlistedcars.points_spent AS points_spent,
    enlistedcars.races_entered AS races_entered,
    enlistedcars.races_won AS races_won,
    enlistedcars.safety AS safety,
    enlistedcars.tarmac AS tarmac,
    enlistedcars.top_speed AS top_speed,
    enlistedcars.worth AS worth,
    ts
FROM (
    SELECT 
    EXPLODE(enlistedcars) AS enlistedcars,
    ts
    FROM delta.`/Volumes/torn/user/user_api_files/enlistedcars`
)