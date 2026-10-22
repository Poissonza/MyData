WITH raw AS (
    SELECT
        retrieved_at,
        UNNEST(data.news) AS entry
    FROM {{ delta_source('torn/faction') }}
    WHERE endpoint = 'news_armoury_action'
)

SELECT
    entry.id,
    entry.text,
    TO_TIMESTAMP(entry.timestamp)           AS event_at,
    REGEXP_EXTRACT(entry.text, '^(\w+)', 1) AS member,
    CASE
        WHEN entry.text ILIKE '%loaned%'    THEN 'loaned'
        WHEN entry.text ILIKE '%used%'      THEN 'used'
        WHEN entry.text ILIKE '%returned%'  THEN 'returned'
    END                                     AS action,
    REGEXP_EXTRACT(
        entry.text,
        '(Xanax|Blood Bag|Bottle of Beer|Morphine|Ipecac Syrup)',
        1
    )                                       AS item,
    retrieved_at
FROM raw
