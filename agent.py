import json
import re
from datetime import datetime, timedelta
import requests

input_data =  """| Ticker | Percentage | Value   |\n|--------|------------|---------|\n| SPY    | 30%        | $3,000  |\n| QQQ    | 30%        | $3,000  |\n| TSLA   | 10%        | $1,000  |\n| NVDA   | 10%        | $1,000  |\n| BTC    | 5%         | $500    |\n| Cash   | 15%        | $1,500  |\n\nThe table shows a balanced approach to investing, with 60% allocated to stable ETFs and 40% to specific stocks and cash for trading opportunities. This strategy allows for both long-term growth and short-term gains while maintaining some liquidity."""

def get_trade(portfolio):
    base_url = "http://127.0.0.1:5000/trade"
    str = ""
    for item in portfolio:
        ticker = item["Ticker"]

        # Create query parameters
        params = {
            'ticker': ticker,
            'count': 10,
            'timespan': 'day'
        }

        # Make the GET request
        response = requests.get(base_url, params=params)

        # Check the response status and handle accordingly
        if response.status_code == 200:
            str = str + f"Response for {ticker}: {response.json()}"
            # print(f"Response for {ticker}: {response.json()}")
        else:
            str += f"Failed to get data for {ticker}. Status code: {response.status_code}"
            # print(f"Failed to get data for {ticker}. Status code: {response.status_code}")
    return str

def get_date_x_days_ago(x):
    target_date = datetime.now() - timedelta(days=x)
    return target_date.strftime("%Y-%m-%d")

def parse_portfolio(table_string):
    table_part = table_string.split('\n\n')[0]

    # Split the string into lines and strip each line to clean it up
    lines = table_part.strip().split('\n')

    # Extract headers from the first line (removing the | and whitespace)
    headers = [header.strip().lower() for header in lines[0].split('|') if header.strip()]

    # Process data rows
    data_rows = []
    for line in lines[2:]:  # Skip header and separator lines
        row_values = [value.strip() for value in line.split('|') if value.strip()]
        row_dict = dict(zip(headers, row_values))
        data_rows.append(row_dict)

    return data_rows

# my_portfolio = parse_portfolio(input_data)
# print(my_portfolio)
#
#
# portfolio_json = json.dumps(my_portfolio, indent=4)
# print(portfolio_json)
#
# get_trade(my_portfolio)