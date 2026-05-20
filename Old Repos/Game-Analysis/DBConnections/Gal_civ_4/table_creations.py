from sqlalchemy import String, Integer, ForeignKey, Column, Table, Boolean, Time


class GalCivTables:

    def __init__(self, meta):
        self.meta = meta

    def run_creation(self, engine):
        self.meta.create_all(engine)
