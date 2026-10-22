import json
import logging

from pyspark.sql.functions import col, current_date, current_timestamp, from_json
from pyspark.sql.utils import AnalysisException

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

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
        store_raw_json: bool = True,
    ):
        """Store API response data to Delta tables.

        Args:
            data: Dictionary containing API response
            volume_path: Path like 'catalog/schema/volume/table' (no leading /Volumes/)
            merge_schema: If True, allows schema evolution in parsed table
            add_date: If True, adds a 'ts' column with current_date
            store_raw_json: If True, stores raw JSON to {volume_path}_raw for replay
        """
        json_str = json.dumps(data)
        df_strings = self.spark.createDataFrame([(json_str,)], ["json_str"])

        # Store raw JSON first if enabled (source of truth for future replays)
        if store_raw_json:
            raw_df = df_strings.withColumn("ingested_at", current_timestamp())
            raw_path = f"/Volumes/{volume_path}_raw"
            try:
                raw_df.write.format("delta").mode("append").save(raw_path)
                logger.info("Raw JSON written to %s", raw_path)
            except Exception as e:
                logger.error("Failed to write raw JSON to %s: %s", raw_path, str(e))
                raise

        # For parsed table: use existing schema to maintain consistency
        # (even if schema is wrong - raw JSON is source of truth for future fixes)
        try:
            existing_df = self.spark.read.format("delta").load(
                f"/Volumes/{volume_path}"
            )
            schema = existing_df.schema
            logger.info("Using existing schema from %s", volume_path)
        except AnalysisException:
            # No existing table, infer from current batch
            schema = df_strings.selectExpr("schema_of_json_agg(json_str)").collect()[0][
                0
            ]
            logger.info("Inferring new schema for %s", volume_path)

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
