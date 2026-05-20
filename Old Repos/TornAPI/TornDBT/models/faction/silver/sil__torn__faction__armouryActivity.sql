SELECT
  id,
  text,
  CAST(from_unixtime(timestamp) AS TIMESTAMP) AS convertedTimeStamp,
  regexp_extract(text, '^([\\w]+)', 1) AS member,
  CASE WHEN regexp_extract(text, 'loaned.',0) != '' THEN 'Loaned'
    WHEN regexp_extract(text, 'used.',0) != '' then 'used'
    WHEN regexp_extract(text, 'returned',0) != '' THEN 'returned'
    ELSE NULL
  END as armouryAction,
  regexp_extract(text, '(Xanax|Blood Bag|Bottle of Beer|Morphine|Ipecac Syrup)', 1) as item
FROM {{ source('torn_faction', 'armouryusage')}};