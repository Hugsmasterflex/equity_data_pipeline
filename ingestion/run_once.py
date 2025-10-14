# ingestion/run_once.py
import logging
import sys
from datetime import datetime, timedelta
from config import settings
from client import get_aggs_5m
from normalise import aggs_to_df
from writer import write_partitioned
from state import load_state, save_state
import time

logging.basicConfig(level=logging.INFO)

TICKERS_FILE = "/home/hugsmaster/projects/equity_data_pipeline/ingestion/tickers.txt"

def daterange(start, end, days):
    cur = start
    while cur < end:
        nxt = min(cur + timedelta(days=days), end)
        yield cur, nxt
        cur = nxt

def main():
    with open(TICKERS_FILE,"r") as f:
        symbols = f.read().splitlines()
    print(symbols)

    state = load_state()

    for symbol in symbols:
        logging.info(f"Fetching {symbol}")
        for start, end in daterange(settings.START_DATE, settings.END_DATE, settings.CHUNK_DAYS):
            aggs = get_aggs_5m(symbol, start, end)
            df = aggs_to_df(symbol, aggs, tz=settings.LOCAL_TZ)
            write_partitioned(df, settings.MINIO_BUCKET, settings.DATA_PATH)
            state[symbol] = end.isoformat()
            save_state(state)
        time.sleep(2) #For free tier
    logging.info("Done.")

if __name__ == "__main__":
    main()
