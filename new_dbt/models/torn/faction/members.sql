{{
    config(
        alias="faction_members"
    )
}}
SELECT 
    member.days_in_faction as days_in_faction,
    member.has_early_discharge as has_early_discharge,
    member.id as id,
    member.is_in_oc as is_in_oc,
    member.is_on_wall as is_on_wall,
    member.is_revivable as is_revivable,
    member.last_action as last_action,
    member.level as level,
    member.name as name,
    member.position as position,
    member.revive_setting as revive_setting,
    member.status as status,
    ts
 FROM (
    SELECT 
    explode(members) as member,
    ts 
    FROM delta.`/Volumes/torn/faction/faction_api_files/members`
)