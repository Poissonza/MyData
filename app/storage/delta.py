from __future__ import annotations

from app.storage.config import StorageConfig


class DeltaWriter:
    TABLE_NAME: str = ""
    PARTITION_BY: list[str] = []

    def __init__(self, spark=None):
        self._spark = spark or StorageConfig.get_spark()
        self._path = StorageConfig.table_path(self.TABLE_NAME)

    def write(self, data: list[dict], mode: str = "append") -> None:
        df = self._spark.createDataFrame(data)
        writer = df.write.format("delta").mode(mode)
        if self.PARTITION_BY:
            writer = writer.partitionBy(*self.PARTITION_BY)
        writer.save(self._path)

    def read(self):
        return self._spark.read.format("delta").load(self._path)
