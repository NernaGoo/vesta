#!/usr/bin/env python
# Name: stock_vesta.py
# Send stock market data to the Vestaboard

from config import (
    colors,
    send_text_to_vestaboard,
    compose_vbml,
    send_array_to_vestaboard,
)
from dotenv import load_dotenv
import os
import requests
import time
import finnhub

# Load API keys and environment
load_dotenv()
api_key = os.getenv("FINNHUB_API_KEY")

# initialize finnhub client
finnhub_client = finnhub.Client(api_key=api_key)

# ------------ STOCK SYMBOLS ----------- #
# Single stock  - current price, % and $ changes will be displayed
symbols = {  # stock ticker name, description
    "NVDA": "Nvidia",
    "GOOGL": "Google",
    "MSFT": "Microsoft",
    "AAPL": "Apple",
    "AMZN": "Amazon",
    "META": "Meta",
    "TSLA": "Tesla",
}

# Market perforance
# Market Indices '^GSPC', '^DJI', '^IXIC' not supported by Finnhub IO free tier; requires a subscription
# Use proxy workaround:
markets = {  # stocks listed here only display a color based on how it's currently performing in the market
    "QQQ": "NASDAQ",
    "SPY": "S&P 500",
    "DIA": "Dow Jones",
}


def display_stock(stocks):
    for i, (stock, company) in enumerate(stocks.items()):
        try:
            print(f"Requesting stock data for {stock}...")
            data = finnhub_client.quote(stock)

            print(f"stock data: {data}")
            c = data["c"]
            dp = data["dp"]
            d = data["d"]

            # format output based on stock performance
            price, percent_delta, dollar_delta, color = format_output(c, dp, d)

            WIDTH = 14  # the width of a vestaboard note reserved for stock banner (14 chars)
            # one char reserved for color bit
            banner = f"{stock}{price:>{WIDTH - len(stock)}}"

            print(banner)
            print(f"\t{dollar_delta}")
            print(f"\t{percent_delta}")

            props = {
                "banner": banner,
                "percent": percent_delta,
                "dollar": dollar_delta,
                "color": color,
            }
            components = [  # format style and justification for each line on vestabaord
                {
                    "style": {"justify": "right", "align": "top", "height": 1},
                    "template": "{{banner}}{{color}}",
                },
                {
                    "style": {"justify": "right", "align": "top", "height": 1},
                    "template": "{{dollar}}",
                },
                {
                    "style": {"justify": "right", "align": "top", "height": 1},
                    "template": "{{percent}}",
                },
            ]

            characters = compose_vbml(props=props, components=components)
            send_array_to_vestaboard(characters)

            if i == len(stocks) - 1:
                print("Done")
                continue  # skip pause for the last item
            print("Pause before displaying next stock")
            time.sleep(120)

        except Exception as e:
            print(f"Something went wrong with {stock}:\n  {e}")


def get_performance_indicators(dp):
    # How is the stock performing today?
    # + is green (up), - is red (down), neutral is white (no movement)
    if dp >= 0:  # stock up
        color = colors["green"]
        direction = "+"
    elif dp < 0:  # stock down
        color = colors["red"]
        direction = "-"
    else:
        color = colors["white"]
        direction = ""

    return color, direction


def format_output(c, dp, d):
    color, direction = get_performance_indicators(dp)
    price = f"${c:.2f}"  # currency
    percent_delta = f"{direction}{abs(dp):.2f}%"  # % symbol
    dollar_delta = f"{direction}${abs(d):.2f}"  # currency
    return price, percent_delta, dollar_delta, color


def collate_market_data(stocks):
    # return a dictionary of stock values
    # https://finnhub.io/pricing
    # free tier: 60 API calls/minute
    stock_dict = {}
    print("Getting stock data (API calls are throttled, so might take a bit)...")
    for symbol, name in stocks.items():
        try:
            data = finnhub_client.quote(symbol)
            if data["c"] == 0:
                continue  # Doesn't seem to be a valid stock, skip
            stock_dict[symbol] = {
                "c": data["c"],
                "dp": data["dp"],
                "d": data["d"],
                "n": name,
            }
            # print(stock_dict)
        except Exception as e:
            print(f"Something went wrong: {e}")
        time.sleep(
            5
        )  # add a delay to throttle api calls and stay well within free limit
    return stock_dict


def display_stock_performance(stocks):
    # display stocks in chunks of 3 to fit vestaboard note 3x15 size
    market_dict = collate_market_data(stocks)

    items = list(market_dict.items())
    chunk_size = 3  # 3 rows on vestaboard; 1 stock per line

    for i in range(0, len(items), chunk_size):
        text = ""  # start with an empty page
        chunk = items[i : i + chunk_size]  # take a chunk and process it

        print(f"Page {i // chunk_size + 1}")

        for symbol, data in chunk:
            name = data["n"]  # company or market index name

            color, direction = get_performance_indicators(
                data["dp"]
            )  # performance indicators

            # vestaboard note: a line has a width of 15 chars or columns
            # Justify the line:
            WIDTH = 15  # the width of a vestaboard note: 15 chars across
            WIDTH += 3  # add buffer to width to account for color code string,
            # color code {nn} starts on column 15, counts as 1 char on vestaboard
            line = f"{name}{color:>{WIDTH - len(name)}}\n"
            print(len(line))
            text = text + line  # build page content

        print(f"Sending to vestaboard...")
        print(text)
        send_text_to_vestaboard(text)

        # If last chunk, skip pause
        if i + chunk_size >= len(items):
            print("Done.")
            continue

        print("Pause before displaying next page...\n")
        time.sleep(120)


def main():
    display_stock(symbols)
    time.sleep(120)  # pause between displays
    display_stock_performance(markets)


if __name__ == "__main__":
    main()
