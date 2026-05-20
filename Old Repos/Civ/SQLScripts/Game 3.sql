insert into Game_played (Game_Played_id,GameSeed, Mapseed, Map_type, Civ_played, Difficulty, Game_Speed, Game_Version)
values (3,-1059404165, -1059404166, 4, 13, 'Prince', 3, '1.0.3.31');

insert into Game_Mode_Link (Game_link, Game_mode_link)
values (3, 1),
       (3, 2);

insert into Wonder_link(Game_id_link, Wonder_id_link)
values (3, 25),
       (3, 34),
       (3, 24);

insert into Opponent_link(Game_id_link, Civ_link)
values (3, 28),
       (3, 23),
       (3, 47),
       (3, 33),
       (3, 4);

insert into City_State_link(Game_link, City_State_link)
values (3,12),
       (3,13),
       (3,14),
       (3,8),
       (3,15),
       (3,16),
       (3,17),
       (3,10),
       (3,18);

insert into Game_Results(Game_id, Num_Turns, Score, Victory_conditions)
values (3, 353, 1289, 'D');

insert into Map_Features_link(Game_link, Map_Feature, Feature_Count)
values (3, 1, 12),
       (3, 2, 5);

insert into Luxury_Resources_Link(Game_link, Resources_Link)
values (3, 10),
       (3, 14),
       (3, 15),
       (3, 11),
       (3, 7),
       (3, 16),
       (3, 17),
       (3, 18),
       (3, 19),
       (3, 24),
       (3, 6),
       (3, 23),
       (3, 22),
       (3, 21);

insert into Secret_Society_link(Game_link, Secret_Society_Link)
values (3, 4);