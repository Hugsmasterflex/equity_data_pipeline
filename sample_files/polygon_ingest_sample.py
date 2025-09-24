"""
polygon_ingest.py
Skeleton ingestion script for Polygon aggregated bars -> Postgres
"""
import os
import time
import json
from datetime import datetime, timedelta
import requests
import psycopg2
from psycopg2.extras import execute_values


# Config from env
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
DB_DSN = os.getenv('DB_DSN') # e.g. 'postgresql://user:pass@localhost:5432/marketdb'


# Basic constants
POLYGON_BASE = 'https://api.polygon.io'
AGGS_ENDPOINT = '/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_dt}/{to_dt}'


# Simple helper for rate limiting/backoff
def polite_request(url, params, max_retries=5, backoff_factor=1.5):
attempt = 0
while attempt < max_retries:
r = requests.get(url, params=params, timeout=30)
if r.status_code == 200:
return r.json()
elif r.status_code in (429, 503):
# Rate limited or service unavailable: backoff
wait = (backoff_factor ** attempt) + 1
print(f"Rate limited or unavailable. Sleeping {wait}s (attempt {attempt})")
time.sleep(wait)
attempt += 1
continue
else:
r.raise_for_status()
raise RuntimeError('Failed after retries')


# Normalize a single Polygon agg bar to our schema
def normalize_agg(bar, symbol, timespan='1min', multiplier=1, provider='polygon'):
# Polygon aggregated bar fields: v, o, c, h, l, t (unix ms)
    t_ms = int(bar.get('t'))
    t = datetime.utcfromtimestamp(t_ms / 1000.0)
    return {
    'symbol': symbol,
    'timespan': timespan,
    'period_multiplier': multiplier,
    backfill(symbols, days=30, multiplier=1, timespan='1day')