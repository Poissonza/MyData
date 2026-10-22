from __future__ import annotations
from pyspark.sql.functions import row_number
from pyspark.sql.window import Window

from app.storage.config import StorageConfig


class DeltaWriter:
    TABLE_NAME: str = ""
    PARTITION_BY: list[str] = []

    def __init__(self, spark=None):
        self._spark = spark or StorageConfig.get_spark()
        self._path = StorageConfig.table_path(self.TABLE_NAME)

    def write(
        self, data: list[dict], mode: str = "append", make_id: bool = False, id_col : str = ""
    ) -> None:
        df = self._spark.createDataFrame(data)
        if make_id:
            window = Window.orderBy(id_col)
            df = df.withColumn("id", row_number().over(window))
        writer = df.write.format("delta").mode(mode)
        if self.PARTITION_BY:
            writer = writer.partitionBy(*self.PARTITION_BY)
        writer.save(self._path)

    def read(self):
        return self._spark.read.format("delta").load(self._path)
