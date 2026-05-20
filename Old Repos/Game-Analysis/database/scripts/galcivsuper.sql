\c galciv4super galcivsuper

CREATE TABLE galaxy_difficulty(
    id serial PRIMARY KEY,
    galaxy_difficulty VARCHAR(255)
);

CREATE TABLE game_pacing(
    id serial PRIMARY KEY,
    game_pacing VARCHAR(255)
);

CREATE TABLE research_rate(
    id serial PRIMARY KEY,
    research_rate VARCHAR(255)
);

CREATE TABLE minor_races(
    id serial PRIMARY KEY,
    minor_races VARCHAR(255)
);