SELECT 
rankedwars.end,
rankedwars.factions, 
rankedwars.id,
rankedwars.start,
rankedwars.target,
rankedwars.winner,
ts
FROM (
SELECT 
explode(rankedwars) as rankedwars,
ts
FROM delta.`/Volumes/torn/faction/faction_api_files/rankedwars`)