insert into Game_played (Game_Played_id,GameSeed, Mapseed, Map_type, Civ_played, Difficulty, Game_Speed, Game_Version)
values (1,1, 1, 1, 5, 'Prince', 3, '1.0.2.39');

insert into Game_Mode_Link (Game_link, Game_mode_link)
values (1, 1);

insert into Wonder_link(Game_id_link, Wonder_id_link)
values (1, 20),
       (1, 10),
       (1, 13);

insert into Opponent_link(Game_id_link, Civ_link)
values (1, 22),
       (1, 37),
       (1, 44);

insert into City_State_link(Game_link, City_State_link)
values (1, 1),
       (1, 2),
       (1, 3),
       (1, 4),
       (1, 5),
       (1, 6);

insert into Game_Results(Game_id, Num_Turns, Score, Victory_conditions)
values (1, 158, 340, 'R');

insert into Map_Features_link(Game_link, Map_Feature, Feature_Count)
values (1, 1, 0),
       (1, 2, 0);

insert into Luxury_Resources_Link(Game_link, Resources_Link)
values (1, 1),
       (1, 2),
       (1, 3),
       (1, 4),
       (1, 5),
       (1, 6),
       (1, 7),
       (1, 8),
       (1, 9),
       (1, 10);

