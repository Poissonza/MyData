{{
    config(
    alias = "user_basic",
    schema = "user"
    )
}}

SELECT 
profile.gender as gender,
profile.id as id,
profile.level as level,
profile.name as name,
profile.status as status,
ts
FROM delta.`/Volumes/torn/user/user_api_files/basic`