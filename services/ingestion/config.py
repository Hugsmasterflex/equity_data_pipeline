import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    AWS_ACCESS_KEY_ID = os.getenv("MINIO_ROOT_USER","minioadmin")
    AWS_SECRET_ACCESS_KEY = os.getenv("MINIO_ROOT_PASSWORD","minioadmin")
    DATA_PATH = "s3://bronze-layer/equities/agg_5m"

settings = Settings()