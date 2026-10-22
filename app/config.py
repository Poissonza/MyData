import os


class Config:
    # Environment: "dev" (local Docker) or "prod" (Databricks)
    APP_ENV: str = os.getenv("APP_ENV", "dev")

    # Storage: local volume for dev, DBFS/Unity Catalog path for prod
    DELTA_BASE_PATH: str = os.getenv("DELTA_BASE_PATH", "file:///data/delta")

    # Spark master URL (dev only — omit for prod/Databricks)
    SPARK_MASTER_URL: str = os.getenv("SPARK_MASTER_URL", "spark://spark:7077")

    # Databricks (prod only)
    DATABRICKS_HOST: str = os.getenv("DATABRICKS_HOST", "")
    DATABRICKS_TOKEN: str = os.getenv("DATABRICKS_TOKEN", "")

    # Torn API
    TORN_API_KEY: str = os.getenv("TORN_API_KEY", "")
    TORN_COMMENT: str = os.getenv("TORN_COMMENT", "python")

    # Relational DB (TTT, legacy game analysis)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "")

    @classmethod
    def db_url(cls, db_name: str = None) -> str:
        name = db_name or cls.DB_NAME
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{name}"
