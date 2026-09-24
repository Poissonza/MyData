{{
    config(
        materialized='table',
        schema='gold',
    )
}}

WITH current_members as (
    SELECT fm.id as xid,
        fm.name as name
    FROM {{ref('members')}} AS fm WHERE ts = (SELECT max(ts) FROM {{ref('members')}})
),
attacks(
    SELECT * FROM {{ref('sil__torn_faction__attacks')}} as attacks
    WHERE startedTimeStamp >= '2026-08-09'
    AND startedTimeStamp <= '2026-08-11'
)

SELECT CM.xid,
    CM.name,
    count(attacks.id) FILTER (WHERE attacks.Respectgain >0 AND attacks.isRankedWar is true) as hits,
    count(attacks.id) FILTER (WHERE attacks.Result = 'Assist' and attacks.isRankedWar is true) as assists,
    count(attacks.id) FILTER (WHERE attacks.Result NOT IN  ('Assist', 'Interrupted') and attacks.isRankedWar is true AND attacks.RespectGain =0) as loss,
    count(attacks.id) FILTER (WHERE attacks.Result IN  ('Interrupted') and attacks.isRankedWar is true AND attacks.RespectGain =0) as interupts
 FROM current_members as CM
LEFT JOIN attacks AS attacks ON attacks.AttackerID = CM.xid
GROUP BY xid, name
;



