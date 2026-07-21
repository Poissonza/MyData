import json
from pyspark.sql.functions import from_json, col

class storage:

    def __init__(self):
        pass

    def store(self, data: dict, volume_path: str):

        json_str = json.dumps(data)

        df_strings = spark.createDataFrame([(json_str,)], ["json_str"])

        schema = df_strings.selectExpr("schema_of_json_agg(json_str)").collect()[0][0]

        data_df = df_strings.select(from_json(col("json_str"), schema).alias("parsed")).select("parsed.*")

        data_df.write.format("delta").mode("overwrite").save(f"/Volumes/{volume_path}")

        print("data Written")