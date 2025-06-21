from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder \
    .appName("ParquetToPostgres") \
    .master("local[*]") \
    .getOrCreate()

# Read Parquet files written by streaming job
df = spark.read.parquet("/opt/bitnami/spark-app/output")

# Define PostgreSQL connection properties
postgres_url = "jdbc:postgresql://postgres:5432/flights"  # Use 'postgres' if service name is 'postgres'

properties = {
    "user": "superset",
    "password": "superset",
    "driver": "org.postgresql.Driver"
}

# Write data into PostgreSQL (append mode)
df.write.jdbc(
    url=postgres_url,
    table="flights",
    mode="append",
    properties=properties
)

print("✅ Data inserted successfully into PostgreSQL.")
spark.stop()
