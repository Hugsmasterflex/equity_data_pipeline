import os
import pandas as pd
import awswrangler as wr
from sqlalchemy import create_engine

DB_DSN = os.environ['DB_DSN']                 # postgresql://user:pass@host:5432/db
S3_PATH = "s3://your-bucket/marketdata/raw_ohlc/"
engine = create_engine(DB_DSN)

# Choose range to export (example: one month)
sql = """
SELECT symbol, timespan, period_multiplier, t AT TIME ZONE 'UTC' as t_utc,
       open::double precision as open,
       high::double precision as high,
       low::double precision as low,
       close::double precision as close,
       volume, provider
FROM raw_ohlc
WHERE t >= '2025-01-01' AND t < '2025-02-01';
"""

# Read from Postgres (streaming-friendly if you set chunksize)
df = wr.db.read_sql_query(sql=sql, con=engine)  # returns pandas.DataFrame

# Add partition columns
df['year'] = df['t_utc'].dt.year.astype(str)
df['month'] = df['t_utc'].dt.month.astype(str).str.zfill(2)
# optionally add day or symbol partition
df['day'] = df['t_utc'].dt.day.astype(str).str.zfill(2)

# Write to S3 as a partitioned parquet dataset and register to Glue catalog
wr.s3.to_parquet(
    df=df,
    path=S3_PATH,
    dataset=True,
    mode='append',                # or 'overwrite_partitions' if you want idempotent replacement
    database='market_catalog',    # optional Glue database
    table='raw_ohlc',
    partition_cols=['year','month','symbol'],
    compression='snappy'
)
