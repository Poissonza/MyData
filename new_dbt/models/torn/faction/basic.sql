{{
    config(
        alias = 'faction_basic'
    )
}}

SELECT 
basic.banner_image as banner_image,
basic.best_chain as best_chain,
basic.capacity as capacity,
basic.co_leader_id as co_leader_id,
basic.days_old as days_old,
basic.id as id,
basic.is_enlisted as is_enlisted,
basic.leader_id as leader_id,
basic.members as members,
basic.name as name,
basic.rank as rank,
basic.respect as respect,
basic.tag as tag,
basic.tag_image as tag_image,
ts
 FROM delta.`/Volumes/torn/faction/faction_api_files/basic`;