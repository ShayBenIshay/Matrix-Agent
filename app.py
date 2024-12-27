from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
from utils import get_date_x_days_ago
import requests
import re
import json
from utils import parse_portfolio
from utils import convert_to_object

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
polygon_api_key = os.getenv("POLYGON_API_KEY")
frontend_url = os.getenv("FRONTEND_URL")

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": frontend_url}})

@app.route("/")
def hello_world():
    return "hello world"

@app.route("/portfolio")
def portfolio():
    cash = request.args.get("cash")

    system_content = (f"format: 1. a table with these headers: ticker, percentage, value. 2. empty line 3.short "
                      f"explanation. the tickers column should be valid wall street tickers. ")

    user_preferences = (f"I want to build a portfolio that is: "
                        f"60% low risk ETFs "
                        f"40% trades. ")

    user_content = (f"I have {cash}$ ."
                    f"I want my portfolio to have maximum 4 assets and to be 5% exposed to Bitcoin. choose how to spread "
                    f"the portfolio")


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
        portfolioObject = convert_to_object(portfolio_json)
        return portfolioObject
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/trade", methods=["GET"])
def trade():
    ticker = request.args.get("ticker")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    timespan = request.args.get("timespan")

    url= (f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/{timespan}/{from_date}"
          f"/{to_date}?adjusted=true&sort=asc&apiKey={polygon_api_key}")

    try:
        response = requests.get(url)
        response.raise_for_status()

        history_json = response.json()
        resultsCount = history_json["resultsCount"]
        history = history_json["results"]
        print(f"Data fetched successfully.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the data: {e}")

    resultsCount = json.dumps(resultsCount)
    history = json.dumps(history)

    system_content = (f"Your answer will be in this format: answer,empty line,explanation"
                      f"answer will be 1 line: buy: x,stop: y, profit: z")
                      # f"You are a low risk trader, swinging in a days to weeks time period. "
                      # f"When the user share stock information you will make a technical analysis base of it")
    user_content = (f"I want you analyze this trade based on the information i will share. what is the buy "
                    f"limit, stop loss order and profit take"
                    f"The next array is candles of ticker {ticker} from the oldest to today "
                    f"The candles: c = close, h = high, l = low, o = open, v = volume."
                    f"{resultsCount} days history: {history}")
    try:
        client = OpenAI(api_key=openai_api_key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content },
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