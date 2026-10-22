{{
    config(
        materialized = 'incremental',
        unique_id = 'id',
        alias ='faction_armory'
    )
}}
SELECT news.id AS id,
news.text as news_text,
news.timestamp as timestamp
FROM (
SELECT EXPLODE(news) as news FROM delta.`/Volumes/torn/faction/faction_api_files/news`
)
{% if is_incremental() %}
WHERE news.timestamp > (SELECT max(timestamp) FROM {{this}})
{% endif %}