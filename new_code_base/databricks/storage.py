import json
import logging

from pyspark.sql.functions import col, current_date, from_json
from pyspark.sql.utils import AnalysisException

logger = logging.getLogger(__name__)


class Storage:

    def __init__(self, spark):
        self.spark = spark

    def store(
        self,
        data: dict,
        volume_path: str,
        merge_schema: bool = False,
        add_date: bool = False,
    ):

        json_str = json.dumps(data)

        df_strings = self.spark.createDataFrame([(json_str,)], ["json_str"])

        try:
            existing_df = self.spark.read.format("delta").load(
                f"/Volumes/{volume_path}"
            )
            schema = existing_df.schema
        except AnalysisException:
            schema = df_strings.selectExpr("schema_of_json_agg(json_str)").collect()[0][
                0
            ]

        data_df = df_strings.select(
            from_json(col("json_str"), schema).alias("parsed")
        ).select("parsed.*")

        if add_date:
            data_df = data_df.withColumn("ts", current_date())

        writer = data_df.write.format("delta").mode("append")
        if merge_schema:
            writer = writer.option("mergeSchema", "true")
        writer.save(f"/Volumes/{volume_path}")

        logger.info("Data written to %s", volume_path)
