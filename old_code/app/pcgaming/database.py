from sqlalchemy import URL, create_engine, MetaData, Table, select


class DataBaseConnection:

    def __init__(
        self, username: str, password: str, host: str, database: str, schema: str
    ):
        self._username = username
        TABLELIST = ["collection", "games", "player"]
        url_object = URL.create(
            "postgresql",
            username=username,
            password=password,
            host=host,
            database=database,
        )

        self._engine = create_engine(url_object)
        self._tables = self.fetch_tables(TABLELIST, schema=schema)

    def fetch_tables(self, table_list: list, schema: str):
        metadata = MetaData()
        table_dict = {}

        for table_name in table_list:
            table = Table(
                table_name, metadata, autoload_with=self._engine, schema=schema
            )
            table_dict.update({table_name: table})

        return table_dict

    def fetch_data(self, table_name: str, single_row: bool = False):
        sel = select(self._tables[table_name])
        connection = self._engine.connect()
        if single_row:
            data = connection.execute(sel).fetchone()
        else:
            data = connection.execute(sel).fetchall()
        connection.close()
        return data

    def insert_data(self, table_name: str, data: dict):
        connection = self._engine.connect()

        ins = self._tables[table_name].insert()

        connection.execute(ins, data)
        connection.commit()
        connection.close()


# class PCGameConnection(DataBaseConnection):
#
#     def __init__(self, username: str, password: str, host: str, database: str, schema: str):
#         super().__init__(
#             username=username, password=password, host=host, database=database, schema=schema
#         )
