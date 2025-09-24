from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("commit-to-iceberg") \
    .config("spark.sql.catalog.mycatalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.mycatalog.type", "hive") \
    .config("spark.sql.catalog.mycatalog.warehouse", "s3a://your-bucket/warehouse") \
    .getOrCreate()

# Read staged parquet files (written to staging path)
staging_path = "s3a://your-bucket/tmp/run_1234/*.parquet"
df = spark.read.parquet(staging_path)

# Optional: run any final transformations/validation in Spark
# Then atomically append to Iceberg table
# mode='append' is atomic via Iceberg's commit protocol
df.write.format("iceberg").mode("append").save("mycatalog.db.gold_ohlc")
