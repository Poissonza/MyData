CREATE USER bg_data WITH PASSWORD 'bg_data' CREATEDB;

CREATE DATABASE boardgames
    WITH
    OWNER = bg_data
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

\connect boardgames bg_data;
CREATE SCHEMA IF NOT EXISTS bgg;


CREATE TABLE IF NOT EXISTS bgg.player
(
    id              INT PRIMARY KEY,
    username        VARCHAR,
    firstname       VARCHAR,
    lastname        VARCHAR,
    yearregistered  INT,
    lastlogin       DATE,
    stateorprovince VARCHAR,
    country         VARCHAR
);

CREATE TABLE IF NOT EXISTS bgg.collection
(
    id         SERIAL PRIMARY KEY,
    collid     INT,
    gameid     INT,
    playerid   INT,
    own        BOOLEAN,
    preordered BOOLEAN,
    prevowned  BOOLEAN,
    want       BOOLEAN,
    wanttobuy  BOOLEAN,
    wanttoplay BOOLEAN,
    wishlist   BOOLEAN,
    rating     float8,
    FOREIGN KEY (playerid) REFERENCES bgg.player (id)
);

CREATE TABLE IF NOT EXISTS bgg.games
(
    id            INT PRIMARY KEY,
    name          VARCHAR,
    yearpublished INT,
    minplayers    INT,
    maxplayers    INT,
    playingtime   INT,
    minage        INT
);