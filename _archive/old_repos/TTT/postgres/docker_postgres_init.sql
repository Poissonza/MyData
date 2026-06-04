CREATE USER ttt WITH PASSWORD 'ttt' CREATEDB;
CREATE DATABASE ttt
    WITH
    OWNER = ttt
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

\c ttt ttt
CREATE TABLE video(
    id serial PRIMARY KEY,
    date DATE,
    name VARCHAR,
    major_change VARCHAR,
    video_play_time TIME,
    server_type INT
);

CREATE TABLE winnerchartdetails(
    id serial PRIMARY KEY,
    winner_id VARCHAR(255) UNIQUE,
    colour VARCHAR(255),
    label VARCHAR(255)
);

CREATE TABLE round(
    id serial PRIMARY KEY,
    round_number INT,
    video_link INT,
    winner VARCHAR(255),
    time_stamp TIME,
    FOREIGN KEY (video_link) REFERENCES video(id),
    FOREIGN KEY (winner) REFERENCES winnerchartdetails(winner_id)
);

CREATE TABLE player(
    id serial PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE role(
    id serial PRIMARY KEY,
    name VARCHAR(255),
    team VARCHAR(255),
    description VARCHAR(255)
);

CREATE TABLE play(
    id serial PRIMARY KEY,
    player_link INT,
    round_link INT,
    role_link INT,
    FOREIGN KEY (player_link) REFERENCES player(id),
    FOREIGN KEY (round_link) REFERENCES round(id),
    FOREIGN KEY (role_link) REFERENCES role(id)
);

CREATE VIEW rounds_complete as (
with rounds as(
SELECT video.date,video.name, count(play.role_link) as round_count from video
left join round on round.video_link = video.id
full join play on play.round_link = round.id
group by video.date, video.name
)

select * from rounds where date > '2020-02-01' order by date
);

CREATE VIEW player_play_counts as(
with player_role_dates as (
SELECT video.date as date, player.name as player, role.name as role FROM play
LEFT JOIN player ON player.id = play.player_link
LEFT JOIN round on round.id = play.round_link
LEFT JOIN role on role.id = play.role_link
LEFT JOIN video on video.id = round.video_link
WHERE video.server_type = 1
)

SELECT date, player, count(player) AS count FROM player_role_dates
GROUP BY date, player ORDER BY date);

CREATE view role_play_counts as(
with player_role_dates as (
SELECT video.date as date, player.name as player, role.name as role FROM play
LEFT JOIN player ON player.id = play.player_link
LEFT JOIN round on round.id = play.round_link
LEFT JOIN role on role.id = play.role_link
LEFT JOIN video on video.id = round.video_link
WHERE video.server_type = 1
)

SELECT date, role, count(role) AS count FROM player_role_dates
GROUP BY date, role ORDER BY date);