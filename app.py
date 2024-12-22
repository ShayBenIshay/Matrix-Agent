from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
from agent import get_date_x_days_ago
from datetime import datetime
import requests
import re
import json
from agent import parse_portfolio
from agent import get_trade

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
polygon_api_key = os.getenv("POLYGON_API_KEY")
frontend_url = os.getenv("FRONTEND_URL")

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": frontend_url}})

@app.route("/")
def hello_world():
    return "hello world"

@app.route("/agent")
def agent():
    url = "http://127.0.0.1:5000/portfolio"

    response = requests.get(url)
    response_json = response.json()
    response_str = response_json['response']
    my_portfolio = parse_portfolio(response_str)

    portfolio_json = json.dumps(my_portfolio, indent=4)
    return get_trade(my_portfolio)


@app.route("/portfolio")
def portfolio():
    cash = request.args.get("cash")

    system_content = (f"Your answer will be in this format: table,empty line,explanation"
                       f"the 3 lines table should have: Ticker, Percentage, value. and the explanation will be 2 "
                      f"lines")

    user_preferences = (f"How to build my portfolio: "
                        f"Steady part - 60% of ETFs that tracks the S&P 500 and NASDAQ-100 "
                        f"Active part - 40% where you are swinging days to weeks trades. ")

    user_content = (f"I have {cash}$ and i want to build a portfolio."
                    f"I would like to invest in small portion on BITCOIN for he long term."
                    f"I like specific stocks like TSLA,NVDA")


    try:
        client = OpenAI(api_key=openai_api_key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_preferences+user_content},
            ],
            temperature=0.8,
            max_tokens=256,
            top_p=1,
        )
        my_portfolio = parse_portfolio(completion.choices[0].message.content)
        portfolio_json = json.dumps(my_portfolio, indent=4)
        return jsonify(portfolio_json)
        # return jsonify({"response": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/trade", methods=["GET"])
def trade():
    ticker = request.args.get("ticker")
    count = request.args.get("count")
    timespan = request.args.get("timespan")

    from_date = get_date_x_days_ago(43)
    to_date = datetime.now().strftime("%Y-%m-%d")

    url= (f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/{timespan}/{from_date}"
          f"/{to_date}?adjusted=true&sort=asc&apiKey={polygon_api_key}")
    history_json={}
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        # Parse the JSON response to a string and save it in the history dictionary
        history_json = response.json()
        print(f"Data fetched and saved successfully.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the data: {e}")

    history_str = json.dumps(history_json)

    system_content = (f"Your answer will be in this format: answer,empty line,explanation"
                      f"answer will be 1 line: buy: x,stop: y, profit: z")
                      # f"You are a low risk trader, swinging in a days to weeks time period. "
                      # f"When the user share stock information you will make a technical analysis base of it")
    user_content = f"Tell me based on this information of the last {count} {timespan}s: "

    try:
        client = OpenAI(api_key=openai_api_key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content + history_str},
            ],
            temperature=0.8,
            max_tokens=256,
            top_p=1,
        )

        first_line = completion.choices[0].message.content.split('\n')[0]
        pattern = r"buy: ([\d.]+), stop: ([\d.]+), profit: ([\d.]+)"
        match = re.match(pattern, first_line)

        if match:
            parsed_data = {
                "buy": float(match.group(1)),
                "stop": float(match.group(2)),
                "profit": float(match.group(3)),
                "ticker": ticker
            }

            json_data = json.dumps(parsed_data, indent=2)
            return json_data
        else:
            print("Failed to parse input string.")

        # return jsonify({"response": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/tweet", methods=["GET"])
def tweet():
    ticker = request.args.get("ticker")
    price = request.args.get("price")
    operation = request.args.get("operation")
    papers = request.args.get("papers")

    content = f"{operation} {papers} stocks of {ticker} at {price}"
    try:
        client = OpenAI(api_key=openai_api_key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial analyst that write tweets about your trades. the user will provide a trade and you will write a tweet about it"},
                {"role": "user", "content": content},
            ],
            temperature=0.8,
            max_tokens=256,
            top_p=1,
        )
        return jsonify({"response": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)