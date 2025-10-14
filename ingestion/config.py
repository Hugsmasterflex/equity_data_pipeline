import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class Settings:
    POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_BUCKET = os.getenv("BRONZE_BUCKET","bronze-layer")
    AWS_ACCESS_KEY_ID = os.getenv("MINIO_ROOT_USER","minioadmin")
    AWS_SECRET_ACCESS_KEY = os.getenv("MINIO_ROOT_PASSWORD","minioadmin")
    LOCAL_TZ = os.getenv("LOCAL_TZ","America/New_York")
    DATA_PATH = "s3://bronze-layer/equities/agg_5m"
    CHUNK_DAYS = 7
    START_DATE = datetime(2025,9,29)
    END_DATE = datetime(2025,10,10)

settings = Settings()