from sqlalchemy import MetaData, Table, select


class GalCivInsertion:

    def __init__(self, engine):
        self.engine = engine
        self.get_tables()

    def get_tables(self):
        meta = MetaData()
        table_names = [
            "abilities",
            "anomolies",
            "ascension_crystals",
            "asteroid",
            "biology",
            "black_holes",
            "civilization_proximity",
            "galaxy_difficulty",
            "game",
            "game_pacing",
            "hostile_entities",
            "ideology",
            "minor_races",
            "nebulas",
            "number_of_sectors",
            "opponent_link",
            "planets_frequency",
            "race",
            "relics",
            "research_rate",
            "resources",
            "result",
            "star_frequency",
            "starting_sector_size",
            "version",
            "victory_condition",
        ]
        self.table_dict = {}
        [
            self.table_dict.update(
                {table_name: Table(table_name, meta, autoload_with=self.engine)}
            )
            for table_name in table_names
        ]

    def insert_data(self, table_name, data):
        ins = self.table_dict[table_name].insert()
        self.engine.execute(ins, data)

    def fill_abilities(self, ability_data):
        for ability in ability_data:
            if self.get_ability_id(ability["ability"]) is None:
                ability.update({"version": self.get_version_id(ability["version"])[0]})
                self.insert_data("abilities", ability)

    def fill_anomolies(self, anomoly_data):
        for anomoly in anomoly_data:
            if self.get_anomoly_id(anomoly["anomolies"]) is None:
                self.insert_data("anomolies", anomoly)

    def fill_ascension_crystal(self, ascension_crystal_data):
        for ascension_crystal in ascension_crystal_data:
            if (
                self.get_ascension_crystal_id(ascension_crystal["ascension_crystals"])
                is None
            ):
                self.insert_data("ascension_crystals", ascension_crystal)

    def fill_asteroid(self, asteroid_data):
        for asteroid in asteroid_data:
            if self.get_asteroid_id(asteroid["asteroid"]) is None:
                self.insert_data("asteroid", asteroid)

    def fill_biology(self, biology_data):
        for biology in biology_data:
            if self.get_biology_id(biology["biology"]) is None:
                self.insert_data("biology", biology)

    def fill_black_hole(self, black_hole_data):
        for black_hole in black_hole_data:
            if self.get_black_hole_id(black_hole["black_holes"]) is None:
                self.insert_data("black_holes", black_hole)

    def fill_civilization_proximity(self, civilization_proximity_data):
        for civilization_proximity in civilization_proximity_data:
            if (
                self.get_civilization_proximity_id(
                    civilization_proximity["civilization_proximity"]
                )
                is None
            ):
                self.insert_data("civilization_proximity", civilization_proximity)

    def fill_galaxy_difficulty(self, galaxy_difficulty_data):
        for galaxy_difficulty in galaxy_difficulty_data:
            if (
                self.get_galaxy_difficulty_id(galaxy_difficulty["galaxy_difficulty"])
                is None
            ):
                self.insert_data("galaxy_difficulty", galaxy_difficulty)

    def fill_game(self, game_data):
        for game_name in game_data:
            game = game_data[game_name]
            if game["complete"]:
                if self.get_game_id(game_name) is None:
                    new_vc = []
                    for victory_condition in game["victory_conditions"]:
                        new_vc.append(
                            self.get_victory_condition_id(victory_condition)[0]
                        )

                    new_opp = []
                    for opponent in game["opponent"]:
                        try:
                            new_opp.append(self.get_race_id(opponent)[0])
                        except:
                            raise ValueError(
                                f"Issue with the {opponent} in game: {game_name}"
                            )

                    game.update({"victory_condition": new_vc, "opponent": new_opp})
                    game["results"].update(
                        {
                            "result": self.get_victory_condition_id(
                                game["results"]["result"]
                            )[0]
                        }
                    )

                    game["setup"].update(
                        {
                            "name": game_name,
                            "race": self.get_race_id(game["setup"]["race"])[0],
                            "galaxy_difficulty": self.get_galaxy_difficulty_id(
                                game["setup"]["galaxy_difficulty"]
                            )[0],
                            "civilization_proximity": self.get_civilization_proximity_id(
                                game["setup"]["civilization_proximity"]
                            )[
                                0
                            ],
                            "game_pacing": self.get_game_pacing(
                                game["setup"]["game_pacing"]
                            )[0],
                            "research_rate": self.get_research_rate_id(
                                game["setup"]["research_rate"]
                            )[0],
                            "number_of_sectors": self.get_number_of_sectors_id(
                                game["setup"]["number_of_sectors"]
                            )[0],
                            "starting_sector_size": self.get_starting_sector_size_id(
                                game["setup"]["starting_sector_size"]
                            )[0],
                            "star_frequency": self.get_star_frequency_id(
                                game["setup"]["star_frequency"]
                            )[0],
                            "planets_frequency": self.get_planets_frequency_id(
                                game["setup"]["planets_frequency"]
                            )[0],
                            "minor_races": self.get_minor_race_id(
                                game["setup"]["minor_races"]
                            )[0],
                            "hostile_entities": self.get_hostile_entities(
                                game["setup"]["hostile_entities"]
                            )[0],
                            "anomolies": self.get_anomoly_id(
                                game["setup"]["anomolies"]
                            )[0],
                            "relics": self.get_relics_id(game["setup"]["relics"])[0],
                            "ascension_crystals": self.get_ascension_crystal_id(
                                game["setup"]["ascension_crystals"]
                            )[0],
                            "resources": self.get_resources_id(
                                game["setup"]["resources"]
                            )[0],
                            "asteroid": self.get_asteroid_id(game["setup"]["asteroid"])[
                                0
                            ],
                            "nebulas": self.get_nebula_id(game["setup"]["nebulas"])[0],
                            "black_holes": self.get_black_hole_id(
                                game["setup"]["black_holes"]
                            )[0],
                            "version": self.get_version_id(game["setup"]["version"])[0],
                        }
                    )
                    self.insert_data("game", game["setup"])

                    game_id = self.get_game_id(game_name)[0]
                    game["results"].update({"game": game_id})

                    self.insert_data("result", game["results"])
                    for opponent in game["opponent"]:
                        self.insert_data(
                            "opponent_link", {"game": game_id, "race": opponent}
                        )

    def fill_game_pacing(self, game_pacing_data):
        for game_pace in game_pacing_data:
            if self.get_game_pacing(game_pace["game_pacing"]) is None:
                self.insert_data("game_pacing", game_pace)

    def fill_hostile_entities(self, hostile_entity_data):
        for hostile_entity in hostile_entity_data:
            if self.get_hostile_entities(hostile_entity["hostile_entities"]) is None:
                self.insert_data("hostile_entities", hostile_entity)

    def fill_ideology(self, ideology_data):
        for ideology in ideology_data:
            if self.get_ideology_id(ideology["ideology"]) is None:
                ideology.update(
                    {"version": self.get_version_id(ideology["version"])[0]}
                )
                self.insert_data("ideology", ideology)

    def fill_minor_races(self, minor_races_data):
        for minor_race in minor_races_data:
            if self.get_minor_race_id(minor_race["minor_races"]) is None:
                self.insert_data("minor_races", minor_race)

    def fill_nebulas(self, nebulas_data):
        for nebula in nebulas_data:
            if self.get_nebula_id(nebula["nebulas"]) is None:
                self.insert_data("nebulas", nebula)

    def fill_number_of_sectors(self, number_of_sectors_data):
        for number_of_sector in number_of_sectors_data:
            if (
                self.get_number_of_sectors_id(number_of_sector["number_of_sectors"])
                is None
            ):
                self.insert_data("number_of_sectors", number_of_sector)

    def fill_planets_frequency(self, planets_frequency_data):
        for planets_frequency in planets_frequency_data:
            if (
                self.get_planets_frequency_id(planets_frequency["planet_frequency"])
                is None
            ):
                self.insert_data("planets_frequency", planets_frequency)

    def fill_planets_frequency(self, planets_frequency_data):
        for planets_frequency in planets_frequency_data:
            if (
                self.get_planets_frequency_id(planets_frequency["planet_frequency"])
                is None
            ):
                self.insert_data("planets_frequency", planets_frequency)

    def fill_race(self, race_data):
        for race in race_data:
            if self.get_race_id(race["race"]) is None:
                race.update(
                    {
                        "version": self.get_version_id(race["version"])[0],
                        "ideology": self.get_ideology_id(race["ideology"])[0],
                        "biology": self.get_biology_id(race["biology"])[0],
                    }
                )
                self.insert_data("race", race)

    def fill_relics(self, relics_data):
        for relic in relics_data:
            if self.get_relics_id(relic["relics"]) is None:
                self.insert_data("relics", relic)

    def fill_research_rate(self, research_rate_data):
        for research_rate in research_rate_data:
            if self.get_research_rate_id(research_rate["research_rate"]) is None:
                self.insert_data("research_rate", research_rate)

    def fill_resources(self, resources_data):
        for resource in resources_data:
            if self.get_resources_id(resource["resources"]) is None:
                self.insert_data("resources", resource)

    def fill_star_frequency(self, star_frequency_data):
        for star_frequency in star_frequency_data:
            if self.get_star_frequency_id(star_frequency["star_frequency"]) is None:
                self.insert_data("star_frequency", star_frequency)

    def fill_starting_sector_size(self, starting_sector_size_data):
        for starting_sector_size in starting_sector_size_data:
            if (
                self.get_starting_sector_size_id(
                    starting_sector_size["starting_sector_size"]
                )
                is None
            ):
                self.insert_data("starting_sector_size", starting_sector_size)

    def fill_version(self, version_data):
        for version in version_data:
            if self.get_version_id(version["version"]) is None:
                self.insert_data("version", version)

    def fill_victory_condition(self, victory_condition_data):
        for victory_condition in victory_condition_data:
            if (
                self.get_victory_condition_id(victory_condition["victory_condition"])
                is None
            ):
                victory_condition.update(
                    {"version": self.get_version_id(victory_condition["version"])[0]}
                )
                self.insert_data("victory_condition", victory_condition)

    def get_ability_id(self, ability_name):
        s = select(self.table_dict["abilities"].c.id).where(
            self.table_dict["abilities"].c.ability == ability_name
        )
        return self.engine.execute(s).fetchone()

    def get_anomoly_id(self, anomoly_name: str):
        s = select(self.table_dict["anomolies"].c.id).where(
            self.table_dict["anomolies"].c.anomolies == anomoly_name
        )
        return self.engine.execute(s).fetchone()

    def get_ascension_crystal_id(self, ascention_crystal_name):
        s = select(self.table_dict["ascension_crystals"].c.id).where(
            self.table_dict["ascension_crystals"].c.ascension_crystals
            == ascention_crystal_name
        )
        return self.engine.execute(s).fetchone()

    def get_asteroid_id(self, asteroid_name):
        s = select(self.table_dict["asteroid"].c.id).where(
            self.table_dict["asteroid"].c.asteroid == asteroid_name
        )
        return self.engine.execute(s).fetchone()

    def get_biology_id(self, biology_name):
        s = select(self.table_dict["biology"].c.id).where(
            self.table_dict["biology"].c.biology == biology_name
        )
        return self.engine.execute(s).fetchone()

    def get_black_hole_id(self, black_hole_name):
        s = select(self.table_dict["black_holes"].c.id).where(
            self.table_dict["black_holes"].c.black_holes == black_hole_name
        )
        return self.engine.execute(s).fetchone()

    def get_civilization_proximity_id(self, civilization_proximity_name):
        s = select(self.table_dict["civilization_proximity"].c.id).where(
            self.table_dict["civilization_proximity"].c.civilization_proximity
            == civilization_proximity_name
        )
        return self.engine.execute(s).fetchone()

    def get_galaxy_difficulty_id(self, galaxy_difficulty_name):
        s = select(self.table_dict["galaxy_difficulty"].c.id).where(
            self.table_dict["galaxy_difficulty"].c.galaxy_difficulty
            == galaxy_difficulty_name
        )
        return self.engine.execute(s).fetchone()

    def get_game_id(self, game_name):
        s = select(self.table_dict["game"].c.id).where(
            self.table_dict["game"].c.name == game_name
        )
        return self.engine.execute(s).fetchone()

    def get_game_pacing(self, game_pacing_name):
        s = select(self.table_dict["game_pacing"].c.id).where(
            self.table_dict["game_pacing"].c.game_pacing == game_pacing_name
        )
        return self.engine.execute(s).fetchone()

    def get_hostile_entities(self, hostile_entities_name):
        s = select(self.table_dict["hostile_entities"].c.id).where(
            self.table_dict["hostile_entities"].c.hostile_entities
            == hostile_entities_name
        )
        return self.engine.execute(s).fetchone()

    def get_ideology_id(self, ideology_name):
        s = select(self.table_dict["ideology"].c.id).where(
            self.table_dict["ideology"].c.ideology == ideology_name
        )
        return self.engine.execute(s).fetchone()

    def get_minor_race_id(self, minor_race_name):
        s = select(self.table_dict["minor_races"].c.id).where(
            self.table_dict["minor_races"].c.minor_races == minor_race_name
        )
        return self.engine.execute(s).fetchone()

    def get_nebula_id(self, nebula_name):
        s = select(self.table_dict["nebulas"].c.id).where(
            self.table_dict["nebulas"].c.nebulas == nebula_name
        )
        return self.engine.execute(s).fetchone()

    def get_number_of_sectors_id(self, number_of_sector_name):
        s = select(self.table_dict["number_of_sectors"].c.id).where(
            self.table_dict["number_of_sectors"].c.number_of_sectors
            == number_of_sector_name
        )
        return self.engine.execute(s).fetchone()

    def get_planets_frequency_id(self, planets_frequency_name):
        s = select(self.table_dict["planets_frequency"].c.id).where(
            self.table_dict["planets_frequency"].c.planet_frequency
            == planets_frequency_name
        )
        return self.engine.execute(s).fetchone()

    def get_race_id(self, race_name):
        s = select(self.table_dict["race"].c.id).where(
            self.table_dict["race"].c.race == race_name
        )
        return self.engine.execute(s).fetchone()

    def get_relics_id(self, relics_name):
        s = select(self.table_dict["relics"].c.id).where(
            self.table_dict["relics"].c.relics == relics_name
        )
        return self.engine.execute(s).fetchone()

    def get_research_rate_id(self, research_rate_name):
        s = select(self.table_dict["research_rate"].c.id).where(
            self.table_dict["research_rate"].c.research_rate == research_rate_name
        )
        return self.engine.execute(s).fetchone()

    def get_resources_id(self, resources_name):
        s = select(self.table_dict["resources"].c.id).where(
            self.table_dict["resources"].c.resources == resources_name
        )
        return self.engine.execute(s).fetchone()

    def get_star_frequency_id(self, star_frequency_name):
        s = select(self.table_dict["star_frequency"].c.id).where(
            self.table_dict["star_frequency"].c.star_frequency == star_frequency_name
        )
        return self.engine.execute(s).fetchone()

    def get_starting_sector_size_id(self, starting_sector_size):
        s = select(self.table_dict["starting_sector_size"].c.id).where(
            self.table_dict["starting_sector_size"].c.starting_sector_size
            == starting_sector_size
        )
        return self.engine.execute(s).fetchone()

    def get_version_id(self, version_name: str):
        s = select(self.table_dict["version"].c.id).where(
            self.table_dict["version"].c.version == version_name
        )
        return self.engine.execute(s).fetchone()

    def get_victory_condition_id(self, victory_condition_name):
        s = select(self.table_dict["victory_condition"].c.id).where(
            self.table_dict["victory_condition"].c.victory_condition
            == victory_condition_name
        )
        return self.engine.execute(s).fetchone()
