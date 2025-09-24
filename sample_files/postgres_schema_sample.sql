-- Create extension for UUIDs if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- 1. symbols: metadata about tracked tickers
CREATE TABLE IF NOT EXISTS symbols (
id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
symbol TEXT NOT NULL UNIQUE,
name TEXT,
exchange TEXT,
currency TEXT,
created_at TIMESTAMPTZ DEFAULT now()
);


-- 2. raw_ohlc: normalized OHLC bars from providers (one row per symbol+timestamp+timespan)
-- Partitioning by RANGE on day (for large datasets). Adjust partition strategy for your scale.
CREATE TABLE IF NOT EXISTS raw_ohlc (
id BIGSERIAL PRIMARY KEY,
symbol TEXT NOT NULL,
timespan TEXT NOT NULL, -- e.g. '1min', '5min', '1hour', '1day'
period_multiplier INT NOT NULL DEFAULT 1, -- e.g. 1 for 1min, 5 for 5min
t TIMESTAMPTZ NOT NULL, -- timestamp for this bar (start time)
open NUMERIC(18,6) NOT NULL,
high NUMERIC(18,6) NOT NULL,
low NUMERIC(18,6) NOT NULL,
close NUMERIC(18,6) NOT NULL,
volume BIGINT NOT NULL DEFAULT 0,
provider TEXT NOT NULL DEFAULT 'polygon',
retrieved_at TIMESTAMPTZ DEFAULT now(),
raw JSONB, -- raw provider payload for audit
UNIQUE(symbol, timespan, period_multiplier, t, provider)
) PARTITION BY RANGE (t);


-- Example: create monthly partitions (automation recommended)
-- CREATE TABLE raw_ohlc_2025_09 PARTITION OF raw_ohlc FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');


-- 3. indicators: derived indicator values per bar (can be computed offline or during ingest)
CREATE TABLE IF NOT EXISTS indicators (
id BIGSERIAL PRIMARY KEY,
symbol TEXT NOT NULL,
timespan TEXT NOT NULL,
period_multiplier INT NOT NULL DEFAULT 1,
t TIMESTAMPTZ NOT NULL,
indicator_name TEXT NOT NULL, -- e.g. 'ema_20', 'rsi_14'
value DOUBLE PRECISION,
created_at TIMESTAMPTZ DEFAULT now(),
UNIQUE(symbol, timespan, period_multiplier, t, indicator_name)
);


-- 4. ingestion_log: track ingestion status and metadata for runs
CREATE TABLE IF NOT EXISTS ingestion_log (
id BIGSERIAL PRIMARY KEY,
run_id UUID DEFAULT uuid_generate_v4(),
symbol TEXT,
timespan TEXT,
period_multiplier INT,
start_time TIMESTAMPTZ,
end_time TIMESTAMPTZ,
rows_inserted INT,
provider TEXT,
status TEXT, -- 'started','completed','failed'
message TEXT,
created_at TIMESTAMPTZ DEFAULT now()
);


-- Indexes to speed common queries
CREATE INDEX IF NOT EXISTS idx_raw_ohlc_symbol_t ON raw_ohlc (symbol, t DESC);
CREATE INDEX IF NOT EXISTS idx_indicators_symbol_t ON indicators (symbol, t DESC);


-- Useful view: latest bar per symbol+timespan
CREATE MATERIALIZED VIEW IF NOT EXISTS latest_bar AS
SELECT DISTINCT ON (symbol, timespan, period_multiplier)
symbol, timespan, period_multiplier, t, open, high, low, close, volume
FROM raw_ohlc
ORDER BY symbol, timespan, period_multiplier, t DESC;


-- Note: For production, consider TimescaleDB or partition maintenance scripts to create partitions by month/day.