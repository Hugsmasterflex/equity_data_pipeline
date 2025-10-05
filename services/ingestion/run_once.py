# ingestion/run_once.py
import logging
from datetime import datetime, timedelta
from ingestion.config import settings
from ingestion.client import get_aggs_5m
from ingestion.normalise import aggs_to_df
from ingestion.writer import write_partitioned
from ingestion.state import load_state, save_state

logging.basicConfig(level=logging.INFO)

def daterange(start, end, days):
    cur = start
    while cur < end:
        nxt = min(cur + timedelta(days=days), end)
        yield cur, nxt
        cur = nxt

def main():
    symbols = ["INTL", "AAPL", "MSFT"]
    state = load_state()

    for symbol in symbols:
        logging.info(f"Fetching {symbol}")
        for start, end in daterange(settings.START_DATE, settings.END_DATE, settings.CHUNK_DAYS):
            aggs = get_aggs_5m(symbol, start, end)
            df = aggs_to_df(symbol, aggs, tz=settings.LOCAL_TZ)
            write_partitioned(df, settings.S3_BUCKET, settings.DATA_PATH)
            state[symbol] = end.isoformat()
            save_state(state)
    logging.info("Done.")

if __name__ == "__main__":
    main()
