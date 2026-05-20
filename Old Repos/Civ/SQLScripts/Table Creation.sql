

Create Table Expansion
(
    Expansion_id   integer primary key autoincrement,
    Expansion_Name char(255),
    Release_Date   Date
);

insert into Expansion (Expansion_Name, Release_Date)
values ('Original Game', '2016-10-16'),
       ('Vikings Scenario Pack', '2016-12-21'),
       ('Poland Civilization', '2016-12-21'),
       ('Australia Civilization', '2017-02-24'),
       ('Persia and Macedon Civilization', '2017-03-28'),
       ('Nubia Civilization', '2017-07-27'),
       ('Khmer and Indonesia Civilization', '2017-10-19'),
       ('Rise and Fall', '2018-02-08'),
       ('Gathering Storm', '2019-02-14'),
       ('Maya & Gran Columbia', '2020-05-21'),
       ('New Frontier Pass', '2020-05-21'),
       ('Ethiopia Pack', '2020-07-23');


Create table Civilization
(
    Civ_id         integer primary key autoincrement,
    Leader_name    char(255),
    Country        char(255),
    Expansion_link integer,
    foreign key (Expansion_link) references Expansion (Expansion_id)
);

-- noinspection SpellCheckingInspection

insert into Civilization (Leader_name, Country, Expansion_link)
values ('Alexander','Macedonian',5),
       ('Amanitore','Nubian',6),
       ('Catherine de Medici','France',1),
       ('Catherine de Medici (Magnificence)','France',11),
       ('Chandragupta','India',8),
       ('Cleopatra','Egypt',1),
       ('Cyrus','Persia',5),
       ('Dido','Phoenician',9),
       ('Eleanor of Aquitaine (French)','France',9),
       ('Eleanor of Aquitaine (England)','England',9),
       ('Frederick Barbarossa','Germany',1),
       ('Gandhi','India',1),
       ('Genghis Khan','Mongolian',8),
       ('Gilgamesh','Sumerian',1),
       ('Gitarja','Indonesian',7),
       ('Gorgo','Greece',1),
       ('Harald Hardrada','Norwegian',1),
       ('Hojo Tokimune','Japan',1),
       ('Jadwiga','Poland',3),
       ('Jayavarman','Khmer',7),
       ('John Curtin','Australia',4),
       ('Kristina','Sweden',9),
       ('Kupe','Maori',9),
       ('Lady Six Sky','Mayan',10),
       ('Lautaro','Mapuche',8),
       ('Mansa Musa','Malian',9),
       ('Matthias Corvinus','Hungary',9),
       ('Menelik II','Ethiopia',12),
       ('Montezuma','Aztec',1),
       ('Mvemba a Nzinga','Kongo',1),
       ('Pachacuti','Incan',9),
       ('Pedro II','Brazil',1),
       ('Pericles','Greece',1),
       ('Peter','Russia',1),
       ('Philip II','Spain',1),
       ('Poundmaker','Cree',8),
       ('Qin Shi Huang','China',1),
       ('Robert the Bruce','Scottland',8),
       ('Saladin','Arabia',1),
       ('Seondeok','Korea',8),
       ('Simón Bolívar','Gran Columbia',10),
       ('Shaka','Zulu',8),
       ('Suleiman','Ottoman',8),
       ('Tamar','Gergian',8),
       ('Teddy Roosevelt','America',1),
       ('Teddy Roosevelt (Bull)','America',11),
       ('Tomyris','Scythian',1),
       ('Trajan','Rome',1),
       ('Victoria','England',1),
       ('Wilfrid Laurier','Canada',9),
       ('Wilhelmina','Dutch',8) ;

-- noinspection SpellCheckingInspection

create table Game_played
(
    Game_Played_id integer primary key,
    GameSeed       integer,
    Mapseed        integer,
    Map_type       integer,
    Civ_played     integer,
    Difficulty     char(255),
    Game_Speed     integer,
    Game_Version   char(10),
    foreign key (Civ_played) references Civilization (Civ_id),
    foreign key (Game_Speed) references Game_Speed (Game_Speed_id),
    foreign key (Map_type) references Map_types (Map_Types_id)
);


create table Game_Modes
(
    GM_id   integer primary key autoincrement,
    GM_name char(255)
);

insert into Game_Modes (GM_name)
values ('Apocalypse'),
       ('Secret Societies');


create table Game_Mode_Link
(
    Game_Mode_link_id integer primary key autoincrement,
    Game_link         integer,
    Game_mode_link    integer,
    foreign key (Game_link) references Game_played (Game_Played_id),
    foreign key (Game_mode_link) references Game_Modes (GM_id)
);

Create Table Wonder
(
    Wonder_id      integer primary key autoincrement,
    Wonder_Name    char(255),
    Expansion_link integer,
    foreign key (Expansion_link) references Expansion (expansion_id)
);

-- noinspection SpellCheckingInspection

insert into Wonder (Wonder_Name, Expansion_link) values
('Bermuda Triangle',10),
('Chocolate Hills',9),
('Cliffs of Dover',1),
('Crater Lake',1),
('Dead Sea',1),
('Delicate Arch',8),
('Eye of the Sahara',8),
('Eyjafjallajokull',2),
('Fountain of Youth',10),
('Galapagos Islands',1),
('Giant''s Causway',2),
('Gobustan',9),
('Great Barrier Reef',1),
('Ha Long Bay',7),
('Ik-Kil',9),
('Lake Retba',8),
('Lysefjord',2),
('Mato Tipila',9),
('Matterhorn',8),
('Mount Everest',1),
('Mount Kilimanjaro',1),
('Mount Roraima',8),
('Mount Vesuvius',9),
('Paititi',10),
('Pamukkale',9),
('Pantanal',1),
('Piopiotahi',1),
('Sahara el Beyda',9),
('Torres del Paine',1),
('Tsingy de Bemaraha',1),
('Ubsunur Hollow',8),
('Uluru',4),
('Yosemite',1),
('Zhangye Danxia',8);

create table Wonder_link
(
    Wonder_link_id integer primary key autoincrement,
    Game_id_link   integer,
    Wonder_id_link integer,
    foreign key (Game_id_link) references Game_played (Game_Played_id),
    foreign key (Wonder_link_id) references Wonder (Wonder_id)
);

create table Opponent_link
(
    Opponent_link_id integer primary key autoincrement,
    Game_id_link     integer,
    Civ_link         integer,
    foreign key (Game_id_link) references Game_played (Game_Played_id),
    foreign key (Civ_link) references Civilization (Civ_id)
);

create table City_State
(
    City_State_id   integer primary key autoincrement,
    City_State_Name char(255),
    Expansion_link  integer,
    foreign key (Expansion_link) references Expansion (Expansion_id)
);

-- noinspection SpellCheckingInspection

insert into City_State(City_State_Name, Expansion_link)
values ('Babylon', 8),
       ('Bandar Brunel', 1),
       ('Fez', 9),
       ('Hattusa', 1),
       ('Mohenjo-Daro', 1),
       ('Rapa Nui', 9),
       ('Auckland',2),
       ('Zanzibar',1),
       ('Ngazargamu',9),
       ('Vatican City',10),
       ('Brussels',1),
       ('Buenos Aires',1),
       ('Yerevan',1),
       ('Armagh',2),
       ('Vilinius',1),
       ('Muscat',2),
       ('Kabul',1),
       ('Jerusalem',1),
       ('Mitla',10),
       ('Lisbon',99),
       ('Singapore',99),
       ('Cahokia',99),
       ('Cardiff',99),
       ('Valletta',99),
       ('Hong Kong',99),
       ('Geneva',99),
       ('La Venta',99),
       ('Caguana',99);


create table City_State_link
(
    City_state_link_id integer primary key autoincrement,
    Game_link          integer,
    City_State_link    integer,
    foreign key (Game_link) references Game_played (Game_Played_id),
    foreign key (City_State_link) references City_State (City_State_id)
);

create table Game_Results
(
    Game_Results_id    integer primary key autoincrement,
    Game_id            integer,
    Num_Turns          integer,
    Score              integer,
    Victory_conditions char(1),
    foreign key (Game_id) references Game_played (Game_Played_id)
);


create table Secret_Societies
(
    Secret_Society_id   integer primary key autoincrement,
    Secret_Society_Name char(255)
);

-- noinspection SpellCheckingInspection

insert into Secret_Societies(Secret_Society_Name)
values ('Owls of Minerva'),
       ('Hermetic Order'),
       ('Voidsingers'),
       ('Sanguine Pact');

create table Map_Features
(
    Feature_id    integer primary key autoincrement,
    Feature_title char(255),
    Expansion_id  integer,
    foreign key (Expansion_id) references Expansion (Expansion_id)
);

insert into Map_Features(Feature_title, Expansion_id)
values ('Volcano', 9),
       ('GeoThermal Fissure', 9),
       ('Ley Lines', 12);

create table Map_Features_link
(
    Map_Features_link_id integer primary key autoincrement,
    Game_link            integer,
    Map_Feature          integer,
    Feature_Count        integer,
    foreign key (Game_link) references Game_played (Game_Played_id),
    foreign key (Map_Feature) references Map_Features (Feature_id)
);

create table Game_Speed
(
    Game_Speed_id          integer primary key autoincrement,
    Game_Speed_Description char(255)
);

insert into Game_Speed(Game_Speed_Description)
Values ('Online'),
       ('Quick'),
       ('Standard'),
       ('Epic'),
       ('Marathon');

create table Map_types
(
    Map_Types_id  integer primary key autoincrement,
    Map_Type_Name char(255)
);

-- noinspection SpellCheckingInspection

insert into Map_types(Map_Type_Name)
values ('4-Leaf Clover'),
       ('6-Armed Snowflake'),
       ('Archipelago'),
       ('Continents'),
       ('Continents and Islands'),
       ('Earth'),
       ('East Asia'),
       ('Europe'),
       ('Fractal'),
       ('Inland Sea'),
       ('Island Plates'),
       ('Lakes'),
       ('Mirror'),
       ('Pangea'),
       ('Primordial'),
       ('Seven Seas'),
       ('Shuffle'),
       ('Small Continents'),
       ('Splintered Fractal'),
       ('Terra'),
       ('Tilted Axis'),
       ('True Start Location Earth'),
       ('True Start Location East Asia'),
       ('True Start Location Europe');

create table Luxury_Resources
(
    Luxury_Resources_id  integer primary key autoincrement,
    Luxury_Resource_Name char(255),
    Expansion            integer,
    foreign key (Expansion) references Expansion (Expansion_id)
);

insert into Luxury_Resources (Luxury_Resource_Name, Expansion)
values ('Jade', 1),
       ('Coffee', 1),
       ('Spices', 1),
       ('Truffles', 1),
       ('Pearls', 1),
       ('Citrus', 1),
       ('Furs', 1),
       ('Ivory', 1),
       ('Tea', 1),
       ('Whales', 1),
       ('Dyes',1),
       ('Cotton',1),
       ('Amber',8),
       ('Silver',1),
       ('Salt',1),
       ('Olives',8),
       ('Turtles',8),
       ('Sugar',1),
       ('Diamond',1),
       ('Honey',10),
       ('Tobacco',1),
       ('Cocoa',1),
       ('Incense',1),
       ('Silk',99),
       ('Mercury',99),
       ('Wine',99)
       ;

create table Luxury_Resources_Link
(
    Luxury_Resources_Link_ID integer primary key autoincrement,
    Game_link                integer,
    Resources_Link           integer,
    foreign key
        (Game_link) references Game_played (Game_Played_id),
    foreign key (Resources_Link) references Luxury_Resources (Luxury_Resources_id)
);

create table Secret_Society_link
(
    Secret_Society_Link_ID integer primary key autoincrement,
    Game_link              integer,
    Secret_Society_Link    integer,
    foreign key (Game_link) references Game_played (Game_Played_id),
    foreign key (Secret_Society_Link) references Secret_Societies (Secret_Society_id)
);