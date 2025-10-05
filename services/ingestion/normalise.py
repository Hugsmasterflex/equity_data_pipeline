# ingestion/normalize.py
import pandas as pd

def aggs_to_df(symbol, aggs, tz="America/New_York"):
    if not aggs:
        return pd.DataFrame()

    rows = []
    for a in aggs:
        # Extract attributes (no .dict() or .model_dump())
        rows.append({
            "symbol": symbol,
            "open": a.open,
            "high": a.high,
            "low": a.low,
            "close": a.close,
            "volume": a.volume,
            "vwap": a.vwap,
            "timestamp": a.timestamp,
            "transactions": a.transactions,
            "otc": a.otc
        })

    df = pd.DataFrame(rows)
    df["event_time_utc"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df["event_time_local"] = df["event_time_utc"].dt.tz_convert(tz)
    df["dt"] = df["event_time_utc"].dt.strftime("%Y-%m-%d")

    return df
