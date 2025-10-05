# ingestion/client.py
from polygon import RESTClient
from ingestion.config import settings
import time
import logging

logger = logging.getLogger(__name__)

client = RESTClient(api_key=settings.POLYGON_API_KEY)

def get_aggs_5m(symbol, start, end, limit=50000):
    """Fetch 5-min aggregate bars for symbol between start and end (inclusive)."""
    all_aggs = []
    while True:
        try:
            resp = client.get_aggs(
                symbol=symbol,
                multiplier=5,
                timespan="minute",
                from_=start,
                to=end,
                limit=limit
            )
            all_aggs.extend(resp)
            break
        except Exception as e:
            logger.warning(f"Retrying {symbol}: {e}")
            time.sleep(2)
    return all_aggs
