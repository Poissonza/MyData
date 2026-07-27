SELECT
    chains.id AS id,
    chains.chain AS chain,
    chains.respect AS respect,
    chains.start AS start,
    chains.end AS end
FROM (
    SELECT
        explode(chains) AS chains
    FROM delta.`/Volumes/torn/faction/faction_api_files/chains/`
)
