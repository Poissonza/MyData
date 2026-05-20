insert into Game_played (Game_Played_id,GameSeed, Mapseed, Map_type, Civ_played, Difficulty, Game_Speed, Game_Version)
values (2,2, 2, 1, 18, 'Prince', 3, '1.0.3.31');

insert into Game_Mode_Link (Game_link, Game_mode_link)
values (2, 1),
       (2, 2);

insert into Wonder_link(Game_id_link, Wonder_id_link)
values (2, 20),
       (2, 10),
       (2, 13);

insert into Opponent_link(Game_id_link, Civ_link)
values (2, 40),
       (2, 51),
       (2, 47);

insert into City_State_link(Game_link, City_State_link)
values (2, 4),
       (2, 7),
       (2, 8),
       (2, 9),
       (2, 10),
       (2, 11);

insert into Game_Results(Game_id, Num_Turns, Score, Victory_conditions)
values (2, 373, 1260, 'D');

insert into Map_Features_link(Game_link, Map_Feature, Feature_Count)
values (2, 1, 0),
       (2, 2, 0),
       (2, 3, 0);

insert into Luxury_Resources_Link(Game_link, Resources_Link)
values (2, 4),
       (2, 2),
       (2, 3),
       (2, 1),
       (2, 7),
       (2, 9),
       (2, 8),
       (2, 6),
       (2, 5),
       (2, 10);

insert into Secret_Society_link(Game_link, Secret_Society_Link)
values (2, 2);