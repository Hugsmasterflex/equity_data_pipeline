import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(DB_DSN)
cur = conn.cursor()

try:
    conn.autocommit = False

    # 1) Create staging temp table (transaction-scoped)
    cur.execute("""
    CREATE TEMP TABLE tmp_staging (
        symbol TEXT,
        timespan TEXT,
        period_multiplier INT,
        t TIMESTAMPTZ,
        open DOUBLE PRECISION,
        high DOUBLE PRECISION,
        low DOUBLE PRECISION,
        close DOUBLE PRECISION,
        volume BIGINT,
        provider TEXT,
        raw JSONB
    ) ON COMMIT DROP;
    """)

    # 2) Bulk insert rows into tmp_staging (using execute_values)
    rows = [...]  # list of tuples loaded from staged parquet
    insert_sql = """
      INSERT INTO tmp_staging (symbol, timespan, period_multiplier, t, open, high, low, close, volume, provider, raw)
      VALUES %s
    """
    execute_values(cur, insert_sql, rows, page_size=1000)

    # 3) Upsert into production table (idempotent)
    upsert_sql = """
    INSERT INTO raw_ohlc (symbol, timespan, period_multiplier, t, open, high, low, close, volume, provider, raw)
    SELECT symbol, timespan, period_multiplier, t, open, high, low, close, volume, provider, raw
    FROM tmp_staging
    ON CONFLICT (symbol, timespan, period_multiplier, t, provider)
    DO UPDATE SET
      open = EXCLUDED.open,
      high = EXCLUDED.high,
      low = EXCLUDED.low,
      close = EXCLUDED.close,
      volume = EXCLUDED.volume,
      raw = EXCLUDED.raw,
      retrieved_at = now();
    """
    cur.execute(upsert_sql)

    # 4) Optionally, record rows inserted/updated and log in ingestion_log
    cur.execute("INSERT INTO ingestion_log (run_id, job_name, source_system, target_system, data_start, data_end, rows_processed, files_written, output_location, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (run_id, 'gold_to_postgres', 'gold_iceberg', 'postgres', data_start, data_end, len(rows), num_files, s3_final_path, 'SUCCESS'))

    conn.commit()
finally:
    cur.close()
    conn.close()
