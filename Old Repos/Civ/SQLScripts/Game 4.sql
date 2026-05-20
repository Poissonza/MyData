insert into Game_played (Game_Played_id,GameSeed, Mapseed, Map_type, Civ_played, Difficulty, Game_Speed, Game_Version)
values (4,-979245686,-979245687,17,14,'Prince','3','1.0.3.31');

insert into Game_Mode_Link (Game_link, Game_mode_link)
values (4,2);

insert into Wonder_link(Game_id_link, Wonder_id_link)
values (4,3),
       (4,8),
       (4,10),
       (4,14);

insert into Opponent_link(Game_id_link, Civ_link)
values (4,7),
       (4,21),
       (4,43),
       (4,48),
       (4,27);


insert into City_State_link(Game_link, City_State_link)
values (4,5),
       (4,6),
       (4,16),
       (4,19),
       (4,12),
       (4,20),
       (4,21),
       (4,9),
       (4,22)
       ;

insert into Game_Results(Game_id, Num_Turns, Score, Victory_conditions)
values (4,405,1192,'C');

insert into Map_Features_link(Game_link, Map_Feature, Feature_Count)
values (4,1,6),
        (4,2,6),
        (4,3,30);

insert into Luxury_Resources_Link(Game_link, Resources_Link)
values (4,4),
       (4,13),
       (4,17),
       (4,12),
       (4,3),
       (4,5),
       (4,15),
       (4,24),
       (4,1),
       (4,7),
       (4,18),
       (4,6),
       (4,25)
       ;

insert into Secret_Society_link(Game_link, Secret_Society_Link)
values (4,2);
