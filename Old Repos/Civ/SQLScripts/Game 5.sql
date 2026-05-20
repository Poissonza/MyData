insert into Game_played (Game_Played_id,GameSeed, Mapseed, Map_type, Civ_played, Difficulty, Game_Speed, Game_Version)
values (5,1101408943,1101408944,9,15,'Prince',3,'1.0.3.31');

insert into Game_Mode_Link (Game_link, Game_mode_link)
values (5,2);

insert into Wonder_link(Game_id_link, Wonder_id_link)
values (5,28),
       (5,4),
       (5,19),
       (5,8);

insert into Opponent_link(Game_id_link, Civ_link)
values (5,18),
       (5,10),
       (5,39),
       (5,17),
       (5,35);

insert into City_State_link(Game_link, City_State_link)
values (5,2),
       (5,6),
       (5,23),
       (5,24),
       (5,25),
       (5,26),
       (5,5),
       (5,27),
       (5,28);


insert into Game_Results(Game_id, Num_Turns, Score, Victory_conditions)
values (5,421,1227,'D');

insert into Map_Features_link(Game_link, Map_Feature, Feature_Count)
values (5,1,6),
       (5,2,6);

insert into Luxury_Resources_Link(Game_link, Resources_Link)
values (5,12),
       (5,22),
       (5,3),
       (5,19),
       (5,18),
       (5,9),
       (5,8),
       (5,4),
       (5,14),
       (5,25),
       (5,26),
       (5,13);

insert into Secret_Society_link(Game_link, Secret_Society_Link)
values (5,3);
