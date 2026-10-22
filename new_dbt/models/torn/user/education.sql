{{
    config(
        alias = "user_education"
    )
}}

SELECT 
education.complete as complete,
education.current as current,
ts
FROM delta.`/Volumes/torn/user/user_api_files/education`