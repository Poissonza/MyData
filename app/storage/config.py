from app.config import Config


class StorageConfig:

    @classmethod
    def table_path(cls, table: str) -> str:
        return f"{Config.DELTA_BASE_PATH}/{table}"

    @classmethod
    def get_spark(cls):
        if Config.APP_ENV == "prod":
            from pyspark.sql import SparkSession

            return SparkSession.getActiveSession()

        from pyspark.sql import SparkSession
        from delta import configure_spark_with_delta_pip

        builder = (
            SparkSession.builder.master(Config.SPARK_MASTER_URL)
            .appName("MyData")
            .config(
                "spark.sql.extensions",
                "io.delta.sql.DeltaSparkSessionExtension",
            )
            .config(
                "spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog",
            )
        )
        return configure_spark_with_delta_pip(builder).getOrCreate()
