CREATE USER galciv WITH PASSWORD 'galciv' CREATEDB;
CREATE DATABASE galciv4
    WITH
    OWNER = galciv
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

CREATE USER galcivsuper WITH PASSWORD 'galcivsuper' CREATEDB;
CREATE DATABASE galciv4super
    WITH
    OWNER = galcivsuper
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

CREATE USER humankind WITH PASSWORD 'humankind';
CREATE DATABASE Humankind
    WITH
    OWNER = root
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

CREATE USER civ WITH PASSWORD 'civ' CREATEDB;
CREATE DATABASE civ6
    WITH
    OWNER = civ
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

\c civ6 civ
CREATE TABLE expansion(
    id serial PRIMARY KEY,
    expansion VARCHAR,
    release_date DATE
);

CREATE TABLE civilization(
    id serial PRIMARY KEY,
    leader VARCHAR (255),
    country VARCHAR(255),
    expansion INT,
    FOREIGN KEY (expansion) REFERENCES expansion(id)
);

CREATE TABLE wonder(
    id serial PRIMARY KEY,
    wonder VARCHAR,
    expansion int,
    FOREIGN KEY (expansion) REFERENCES expansion(id)
);

CREATE TABLE game_mode(
    id serial PRIMARY KEY,
    game_mode VARCHAR(255)
);

CREATE TABLE game_speed(
    id serial PRIMARY KEY,
    game_speed VARCHAR(255)
);

CREATE TABLE map_type(
    id serial PRIMARY KEY,
    map_type VARCHAR(255)
);

CREATE TABLE map_feature(
    id serial PRIMARY KEY,
    feature VARCHAR(255),
    expansion INT,
    FOREIGN KEY (expansion) REFERENCES expansion(id)
);

CREATE TABLE secret_society(
    id serial PRIMARY KEY,
    secret_society VARCHAR(255)
);

CREATE TABLE city_state(
    id serial PRIMARY KEY,
    city_state VARCHAR(255),
    expansion INT,
    FOREIGN KEY (expansion) REFERENCES expansion(id)
);

CREATE TABLE luxury_resource(
    id serial PRIMARY KEY,
    luxury_resource VARCHAR(255),
    expansion INT,
    FOREIGN KEY (expansion) REFERENCES expansion(id)
);

CREATE TABLE game(
    id serial PRIMARY KEY,
    game_name VARCHAR,
    game_seed INT,
    map_seed INT,
    map_type INT,
    civ_played INT,
    difficulty VARCHAR(255),
    game_speed int,
    game_version VARCHAR,
    secret_society int,
    FOREIGN KEY (map_type) REFERENCES map_type(id),
    FOREIGN KEY (civ_played) REFERENCES civilization(id),
    FOREIGN KEY (game_speed) REFERENCES game_speed(id),
    FOREIGN KEY (secret_society) REFERENCES secret_society(id)
);

CREATE TABLE game_mode_link(
  id serial PRIMARY KEY,
  game INT,
  game_mode INT,
  FOREIGN KEY (game) REFERENCES game(id),
  FOREIGN KEY (game_mode) REFERENCES game_mode(id)
);


CREATE TABLE wonder_link(
    id serial PRIMARY KEY,
    wonder INT,
    game INT,
    FOREIGN KEY (wonder) REFERENCES wonder(id),
    FOREIGN KEY (game) REFERENCES game(id)
);

CREATE TABLE opponent_link(
  id serial PRIMARY KEY,
  civilization INT,
  game INT,
  FOREIGN KEY (civilization) REFERENCES civilization(id),
  FOREIGN KEY (game) REFERENCES game(id)
);

CREATE TABLE city_state_link(
  id serial PRIMARY KEY,
  city_state int,
  game INT,
  FOREIGN KEY (city_state) REFERENCES city_state(id),
  FOREIGN KEY (game) REFERENCES game(id)
);

CREATE TABLE results(
  id serial PRIMARY KEY,
  game INT,
  number_of_turns INT,
  score INT,
  victory_condition VARCHAR(255),
  FOREIGN KEY (game) REFERENCES game(id)
);

CREATE TABLE map_feature_link(
    id serial PRIMARY KEY,
    game INT,
    map_feature INT,
    feature_count INT,
    FOREIGN KEY (game) REFERENCES game(id),
    FOREIGN KEY (map_feature) REFERENCES map_feature(id)
);

CREATE TABLE luxury_resource_link(
    id serial PRIMARY KEY,
    game INT,
    luxury_resource INT,
    FOREIGN KEY (game) REFERENCES game(id),
    FOREIGN KEY (luxury_resource) REFERENCES luxury_resource(id)
);

\c humankind humankind
CREATE TABLE version(
    id serial PRIMARY KEY,
    descriptor VARCHAR (50),
    description VARCHAR (255)
);

CREATE TABLE lake_odds(
    id serial PRIMARY KEY,
    descriptor VARCHAR (255),
    version INT,
    FOREIGN KEY (version) REFERENCES version (id)
);

CREATE TABLE rivers(
    id serial PRIMARY KEY,
    descriptor VARCHAR (255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE end_conditions(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE elevation(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE lake_size(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE ridges_and_cliffs(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE hemisphere(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE world_wrap(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255)
);

CREATE TABLE island_odds(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE new_world(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255)
);

CREATE TABLE continent_shape(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE number_of_continents(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE strategic_resource(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE luxury_resource(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE Natural_wonder(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE world_size(
    id serial PRIMARY KEY,
    descriptor VARCHAR (255),
    supported_players int,
    hexagons int,
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE world_shape(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE pace(
    id serial PRIMARY KEY,
    descriptor VARCHAR (255),
    turns int,
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE era(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    description VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE difficulty(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE continent_spread(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE continent_form(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE climate(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE civilization(
    id serial PRIMARY KEY,
    descriptor VARCHAR(255),
    era INT,
    affinity VARCHAR(255),
    version INT,
    FOREIGN KEY (era) REFERENCES era(id),
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE game(
    id serial PRIMARY KEY,
    descriptor VARCHAR (255),
    world_size INT,
    world_shape INT,
    continent_shape INT,
    climate INT,
    land_percentage INT,
    number_of_continents int,
    new_world int,
    island_odds int,
    world_wrap INT,
    hemisphere int,
    seed int,
    continent_spread int,
    continent_form int,
    lake_odds int,
    lake_size int,
    rivers int,
    ridges_and_cliffs int,
    elevation int,
    difficulty int,
    pace int,
    end_conditions int,
    start_date DATE,
    end_date DATE,
    version INT,
    FOREIGN KEY (world_size) REFERENCES world_size(id),
    FOREIGN KEY (world_shape) REFERENCES world_shape(id),
    FOREIGN KEY (continent_shape) REFERENCES continent_shape(id),
    FOREIGN KEY (climate) REFERENCES climate(id),
    FOREIGN KEY (number_of_continents) REFERENCES number_of_continents(id),
    FOREIGN KEY (new_world) REFERENCES new_world(id),
    FOREIGN KEY (island_odds) REFERENCES island_odds(id),
    FOREIGN KEY (world_wrap) REFERENCES world_wrap(id),
    FOREIGN KEY (hemisphere) REFERENCES hemisphere(id),
    FOREIGN KEY (continent_spread) REFERENCES continent_spread(id),
    FOREIGN KEY (continent_form) REFERENCES continent_form(id),
    FOREIGN KEY (lake_odds) REFERENCES lake_odds(id),
    FOREIGN KEY (lake_size) REFERENCES lake_size(id),
    FOREIGN KEY (rivers) REFERENCES rivers(id),
    FOREIGN KEY (ridges_and_cliffs) REFERENCES ridges_and_cliffs(id),
    FOREIGN KEY (elevation) REFERENCES elevation(id),
    FOREIGN KEY (difficulty) REFERENCES difficulty(id),
    FOREIGN KEY (pace) REFERENCES pace(id),
    FOREIGN KEY (end_conditions) REFERENCES end_conditions(id),
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE natural_wonder_link(
    id SERIAL PRIMARY KEY,
    game_id INT,
    natural_wonder INT,
    FOREIGN KEY (game_id) REFERENCES game(id),
    FOREIGN KEY (natural_wonder) REFERENCES natural_wonder(id)
);

CREATE TABLE strategic_resource_link(
  id SERIAL PRIMARY KEY,
  game_id INT,
  resource_id INT,
  quantity INT,
  FOREIGN KEY (game_id) REFERENCES game(id),
  FOREIGN KEY (resource_id) REFERENCES strategic_resource(id)
);

CREATE TABLE luxury_resource_link(
  id SERIAL PRIMARY KEY,
  game_id INT,
  resource_id INT,
  quantity INT,
  FOREIGN KEY (game_id) REFERENCES game(id),
  FOREIGN KEY (resource_id) REFERENCES luxury_resource(id)
);

\c galciv4 galciv
CREATE TABLE version(
  id serial PRIMARY KEY,
  version VARCHAR(255),
  description VARCHAR(255)
);

CREATE TABLE victory_condition(
  id serial PRIMARY KEY,
  victory_condition VARCHAR(255),
  version INT,
  FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE starting_sector_size(
  id serial PRIMARY KEY,
  starting_sector_size VARCHAR(255)
);

CREATE TABLE star_frequency(
    id serial PRIMARY KEY,
    star_frequency VARCHAR(255)
);

CREATE TABLE abilities(
    id serial PRIMARY KEY,
    ability VARCHAR(255),
    description VARCHAR(255),
    extra_ability VARCHAR(255),
    version INT,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE anomolies(
    id serial PRIMARY KEY,
    anomolies VARCHAR(255)
);

CREATE TABLE ascension_crystals(
    id serial PRIMARY KEY,
    ascension_crystals VARCHAR(255)
);

CREATE TABLE asteroid(
    id serial PRIMARY KEY,
    asteroid VARCHAR(255)
);

CREATE TABLE biology(
    id serial PRIMARY KEY,
    biology VARCHAR(255)
);

CREATE TABLE black_holes(
    id serial PRIMARY KEY,
    black_holes VARCHAR(255)
);

CREATE TABLE civilization_proximity(
    id serial PRIMARY KEY,
    civilization_proximity VARCHAR(255)
);

CREATE TABLE game_pacing(
    id serial PRIMARY KEY,
    game_pacing VARCHAR(255)
);

CREATE TABLE galaxy_difficulty(
    id serial PRIMARY KEY,
    galaxy_difficulty VARCHAR(255)
);

CREATE TABLE hostile_entities(
    id serial PRIMARY KEY,
    hostile_entities VARCHAR(255)
);

CREATE TABLE ideology(
    id serial PRIMARY KEY,
    ideology VARCHAR(255),
    description VARCHAR(255),
    version int,
    FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE race(
  id serial PRIMARY KEY,
  race VARCHAR(255),
  ideology int,
  biology int,
  version int,
  FOREIGN KEY (ideology) REFERENCES ideology(id),
  FOREIGN KEY (biology) REFERENCES biology(id),
  FOREIGN KEY (version) REFERENCES version(id)
);

CREATE TABLE minor_races(
    id serial PRIMARY KEY,
    minor_races VARCHAR(255)
);

CREATE TABLE nebulas(
    id serial PRIMARY KEY,
    nebulas VARCHAR(255)
);

CREATE TABLE number_of_sectors(
    id serial PRIMARY KEY,
    number_of_sectors VARCHAR(255)
);

CREATE TABLE planets_frequency(
    id serial PRIMARY KEY,
    planet_frequency VARCHAR(255)
);

CREATE TABLE relics(
    id serial PRIMARY KEY,
    relics VARCHAR(255)
);

CREATE TABLE research_rate(
    id serial PRIMARY KEY,
    research_rate VARCHAR(255)
);

CREATE TABLE resources(
    id serial PRIMARY KEY,
    resources VARCHAR(255)
);

CREATE TABLE game(
    id serial PRIMARY KEY,
    name VARCHAR(255),
    race INT,
    galaxy_difficulty INT,
    civilization_proximity INT,
    game_pacing INT,
    research_rate INT,
    number_of_sectors INT,
    starting_sector_size INT,
    star_frequency INT,
    planets_frequency INT,
    minor_races INT,
    hostile_entities INT,
    anomolies INT,
    relics INT,
    ascension_crystals INT,
    resources INT,
    asteroid INT,
    nebulas INT,
    black_holes INT,
    disable_tech_trading BOOLEAN,
    disable_tech_brokering BOOLEAN,
    disable_ai_surrendering BOOLEAN,
    surrendered_colonies BOOLEAN,
    no_fow_in_territory BOOLEAN,
    number_of_players INT,
    version INT,
    FOREIGN KEY (race) REFERENCES race(id),
    FOREIGN KEY (galaxy_difficulty) REFERENCES galaxy_difficulty(id),
    FOREIGN KEY (civilization_proximity) REFERENCES civilization_proximity(id),
    FOREIGN KEY (game_pacing) REFERENCES game_pacing(id),
    FOREIGN KEY (research_rate) REFERENCES research_rate(id),
    FOREIGN KEY (number_of_sectors) REFERENCES number_of_sectors(id),
    FOREIGN KEY (starting_sector_size) REFERENCES starting_sector_size(id),
    FOREIGN KEY (star_frequency) REFERENCES star_frequency(id),
    FOREIGN KEY (planets_frequency) REFERENCES planets_frequency(id),
    FOREIGN KEY (minor_races) REFERENCES minor_races(id),
    FOREIGN KEY (hostile_entities) REFERENCES hostile_entities(id),
    FOREIGN KEY (anomolies) REFERENCES anomolies(id),
    FOREIGN KEY (relics) REFERENCES relics(id),
    FOREIGN KEY (ascension_crystals) REFERENCES ascension_crystals(id),
    FOREIGN KEY (resources) REFERENCES resources(id),
    FOREIGN KEY (asteroid) REFERENCES asteroid(id),
    FOREIGN KEY (nebulas) REFERENCES nebulas(id),
    FOREIGN KEY (black_holes) REFERENCES black_holes(id)
);

CREATE TABLE opponent_link(
    id serial PRIMARY KEY,
    race int,
    game int,
    FOREIGN KEY (race) REFERENCES race(id),
    FOREIGN KEY (game) REFERENCES game(id)
);

CREATE TABLE result(
    id serial PRIMARY KEY,
    game int,
    turns int,
    result int,
    score int,
    time_played TIME,
    FOREIGN KEY (game) REFERENCES game(id),
    FOREIGN KEY (result) REFERENCES victory_condition(id)
);