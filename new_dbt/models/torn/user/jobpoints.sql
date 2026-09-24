{{
    config(
        alias="user_jobpoints"
    )
}}
SELECT 
jobpoints.companies,
jobpoints.jobs,
ts
FROM delta.`/Volumes/torn/user/user_api_files/jobpoints`