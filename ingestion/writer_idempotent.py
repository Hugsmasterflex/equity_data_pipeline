# ingestion/writer.py
import logging
import uuid
import s3fs
import pandas as pd
from datetime import datetime,timezone

logger = logging.getLogger(__name__)

def write_partitioned(df, bucket, base_path):
    """
    Write a DataFrame partitioned by symbol and date to MinIO/S3.
    Ensures idempotent writes via 'write-then-rename' (atomic visibility).
    """

    if df.empty:
        logger.info("No rows to write.")
        return

    # 1️⃣ Connect to MinIO / S3
    fs = s3fs.S3FileSystem(
        key="minioadmin",
        secret="minioadmin",
        client_kwargs={"endpoint_url": "http://localhost:9000"}
    )

    # 2️⃣ Add ingest metadata (useful for debugging & audit)
    ingest_batch_id = str(uuid.uuid4())
    ingest_time_utc = datetime.now(timezone.utc).isoformat()
    df["ingest_batch_id"] = ingest_batch_id
    df["ingest_time_utc"] = ingest_time_utc

    # 3️⃣ Group by partition keys
    for dt, group in df.groupby("dt"):
        symbol = group["symbol"].iloc[0]

        # Define base partition path
        partition_path = f"{base_path}/symbol={symbol}/dt={dt}"

        # Final file (the “official” data file)
        final_path = f"{partition_path}/part.parquet"

        # Temporary file name (unique per run)
        temp_path = f"{partition_path}/.temp-{ingest_batch_id}.parquet"

        logger.info(f"Writing {len(group)} rows to temp: {temp_path}")

        # 4️⃣ Write to the temporary file first
        group.to_parquet(temp_path, index=False, filesystem=fs)

        # 5️⃣ Rename temp → final (atomic in MinIO)
        # This ensures no partial files appear if a crash happens mid-write
        if fs.exists(final_path):
            logger.info(f"Overwriting existing file: {final_path}")
            fs.rm(final_path)
        fs.mv(temp_path, final_path)

        logger.info(f"✅ Wrote partition: {final_path} (batch={ingest_batch_id})")
