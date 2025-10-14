# ingestion/writer.py
import pandas as pd
import logging
from config import settings

logger = logging.getLogger(__name__)

def write_partitioned(df, bucket, base_path):
    if df.empty:
        logger.info("No rows to write")
        return

    import s3fs
    fs = s3fs.S3FileSystem(
        key=settings.AWS_ACCESS_KEY_ID,
        secret=settings.AWS_SECRET_ACCESS_KEY,
        client_kwargs={"endpoint_url": settings.MINIO_ENDPOINT}
    )

    for dt, group in df.groupby("dt"):
        symbol = group["symbol"].iloc[0]
        path = f"{base_path}/symbol={symbol}/dt={dt}/part.parquet"
        logger.info(f"Writing {len(group)} rows to {path}")
        group.to_parquet(path, index=False, filesystem=fs)
