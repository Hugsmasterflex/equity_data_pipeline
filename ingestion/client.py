# ingestion/client.py
from polygon import RESTClient
from config import settings
import time
import logging
from urllib3.exceptions import MaxRetryError
from requests.exceptions import HTTPError
import random

logger = logging.getLogger(__name__)

client = RESTClient(api_key=settings.POLYGON_API_KEY)

def get_aggs_5m(symbol, start, end, limit=50000, max_retries=5):
    """Fetch 5-min aggregate bars for symbol between start and end (inclusive)."""
    attempt = 0
    while attempt < max_retries:
        try:
            aggs = client.get_aggs(
                ticker=symbol,
                multiplier=5,
                timespan="minute",
                from_=start,
                to=end,
                limit=limit
            )
            logger.debug(f"Retrieved agg info for synbol={symbol}, start_date={start}, end_date={end}.")
            return aggs
        except HTTPError as e:
            #Handle HTTP 429 (rate limiting)
            if e.response is not None and e.response.status_code == 429:
                retry_after = e.response.headers.get("Retry-After")
                if retry_after:
                    sleep_time = float(retry_after)
                    logger.warning(f"Rate limit hit for {symbol}. Retrying in {sleep_time}s...")
                else:
                    sleep_time = min(60 * (2 ** attempt), 300) #Exponential backpff up to 5 mins
                    logger.warning(f"Rate limit (429) for {symbol}. Backing off {sleep_time:.1f}s...")
                time.sleep(sleep_time + random.uniform(0,1)) #jitter
                attempt += 1
            #Handle other HTTP exceptions
            elif e.response is not None and 500 <= e.response.status_code < 600:
                sleep_time = 5 * (2 ** attempt)
                logger.warning(f"Server error {e.response.status_code} for {symbol}, retrying in {sleep_time}s...")
                time.sleep(sleep_time)
                attempt += 1
                continue
            else:
                logger.error(f"HTTP error for {symbol}:{e}")
                raise
        except Exception as e:
            sleep_time = 5 * (2 ** attempt)
            logger.warning(f"Network error for {symbol}:{e}. Retrying in {sleep_time}s...")
            time.sleep(sleep_time)
            attempt += 1
            continue
    logger.error(f"Failed to fetch data for {symbol} after {max_retries} attempts.")
    raise RuntimeError(f"Failed to fetch data for {symbol} after {max_retries} attempts.")
