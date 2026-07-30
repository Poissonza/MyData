import datetime as dt
import logging

logger = logging.getLogger(__name__)


class WatermarkManager:

    CONFIG = {
        "faction": {
            "attacks": {"spark_table": "torn.faction.faction_attacks", "column": "started",   "wm_type": "epoch"},
            "chains":  {"spark_table": "torn.faction.faction_chains",  "column": "start",     "wm_type": "epoch"},
            "balance": {"spark_table": "torn.faction.faction_balance", "column": "ts",        "wm_type": "date"},
            "basic":   {"spark_table": "torn.faction.faction_basic",   "column": "ts",        "wm_type": "date"},
            "members": {"spark_table": "torn.faction.faction_members", "column": "ts",        "wm_type": "date"},
            "news":    {"spark_table": "torn.faction.faction_armory",  "column": "timestamp", "wm_type": "epoch"},
        },
        "user": {
            "attacks": {"spark_table": "torn.user.user_attacks", "column": "started", "wm_type": "epoch"},
        },
    }

    def __init__(self, spark, default_from_ts: int, category: str):
        self.spark = spark
        self.default_from_ts = default_from_ts
        self.category = category

    def get_run_params(self, table: str, params: dict) -> tuple[bool, dict]:
        category_config = self.CONFIG.get(self.category, {})
        if table not in category_config:
            return True, params

        cfg = category_config[table]
        spark_table, column, wm_type = cfg["spark_table"], cfg["column"], cfg["wm_type"]

        if not self.spark.catalog.tableExists(spark_table):
            logger.info("%s: table does not exist, running from default", table)
            if wm_type == "date":
                return True, params
            return True, {**params, "from_ts": self.default_from_ts}

        row = self.spark.read.table(spark_table).select(column).agg({column: "max"}).collect()[0]
        current_max = row[f"max({column})"]
        logger.info("%s: current watermark = %s", table, current_max)

        if wm_type == "date":
            run = current_max < dt.datetime.today().date()
            logger.info("%s: %s", table, "running" if run else "skipping, already up to date")
            return run, params
        else:
            if current_max > dt.datetime.today().timestamp():
                logger.info("%s: skipping, watermark is in the future", table)
                return False, params
            return True, {**params, "from_ts": current_max}
