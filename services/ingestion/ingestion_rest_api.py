from dotenv import load_dotenv
import os
from polygon import RESTClient
import json
load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")


def main():
    client = RESTClient(POLYGON_API_KEY)
    tickers = []
    for t in client.list_tickers(
        ticker= "INTL",
        market="stocks",
        active="true",
        order="asc",
        limit="100",
        sort="ticker",
        ):
        tickers.append(t)

    print(tickers)
if __name__ == "__main__":
    main()