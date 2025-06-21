from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# Define schema of the flight data
flight_schema = StructType([
    StructField("icao24", StringType(), True),
    StructField("callsign", StringType(), True),
    StructField("origin_country", StringType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("baro_altitude", DoubleType(), True),
    StructField("velocity", DoubleType(), True),
    StructField("true_track", DoubleType(), True),
    StructField("vertical_rate", DoubleType(), True),
    StructField("geo_altitude", DoubleType(), True),
    StructField("squawk", StringType(), True)
])

# Create Spark session
spark = SparkSession.builder \
    .appName("FlightDataStreaming") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# PostgreSQL connection parameters
postgres_url = "jdbc:postgresql://postgres:5432/flights"
postgres_properties = {
    "user": "superset",
    "password": "superset",
    "driver": "org.postgresql.Driver"
}

def write_to_postgres(batch_df, batch_id):
    batch_df.write.jdbc(
        url=postgres_url,
        table="flight_data",
        mode="append",
        properties=postgres_properties
    )

try:
    # Read from Kafka
    df_raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "flights") \
        .option("startingOffsets", "latest") \
        .option("failOnDataLoss", "false") \
        .load()

    # Parse JSON payload
    df_parsed = df_raw.select(
        from_json(col("value").cast("string"), flight_schema).alias("data")
    ).select("data.*")

    # Write each micro-batch to PostgreSQL
    query = df_parsed.writeStream \
        .foreachBatch(write_to_postgres) \
        .option("checkpointLocation", "/opt/bitnami/spark-app/checkpoint_pg") \
        .start()

    query.awaitTermination()

except Exception as e:
    print(f"Error in streaming application: {e}")
finally:
    spark.stop()
