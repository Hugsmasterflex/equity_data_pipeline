# ingestion/writer.py
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def write_partitioned(df, bucket, base_path):
    if df.empty:
        logger.info("No rows to write")
        return

    import s3fs
    fs = s3fs.S3FileSystem(
        key=df.attrs.get("aws_access_key_id", "minioadmin"),
        secret=df.attrs.get("aws_secret_access_key", "minioadmin"),
        client_kwargs={"endpoint_url": "http://localhost:9000"}
    )

    for dt, group in df.groupby("dt"):
        symbol = group["symbol"].iloc[0]
        path = f"{base_path}/symbol={symbol}/dt={dt}/part.parquet"
        logger.info(f"Writing {len(group)} rows to {path}")
        group.to_parquet(path, index=False, filesystem=fs)
