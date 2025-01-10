from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
polygon_api_key = os.getenv("POLYGON_API_KEY")
frontend_url = os.getenv("FRONTEND_URL")

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": frontend_url}})

@app.route("/")
def hello_world():
    return "hello world"

@app.route('/manipulate-portfolio', methods=['POST'])
def manipulate_portfolio():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    # Log each parameter
    cash = data.get("cash")
    additional_info = data.get("additionalInfo")
    print(additional_info)
    additional_info = ""
    totals = data.get("totals")

    system_content = ("""
                    You are a financial broker investing for the long term. you need to decide if and how to 
                    manipulate the portfolio of the user.
                    you will receive the cash amount, the position on each stock with additional calculations.
                    Respond with the following JSON without any markdowns and surroundings::
                    {
                        "analysis": string (A short analysis of the data),
                        "portfolio": 
                        [{
                            "percentage": float (the percentage from my portfolio),
                            "ticker": string (valid wall street ticker Symbol)
                        }]
                    }
                    """)

    user_preferences = (f"""I want you to decide after analyzing of the market if and how to change my portfolio. 
                        This is my current portfolio:
                        {totals}
                        i also have liquid cash: {cash}
                        {additional_info}
                        your mission is decide how my portfolio should look today after your analyze.
                        """)

    try:
        client = OpenAI(api_key=openai_api_key)
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_preferences},
            ],
            temperature=0.8,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/portfolio")
def portfolio():
    userPreference = request.args.get("userPreference")
    print("userPreference " +userPreference)

    system_content = ("""
    You are a financial broker investing for the long term, helping clients to create portfolio.
    Respond with the following JSON without any markdowns and surroundings::
    {
        "analysis": string (A short analysis of the data),
        "portfolio": 
        [{
            "percentage": float (the percentage from my portfolio),
            "ticker": string (valid wall street ticker Symbol)
        }]
    }
    """)

    user_preferences = (f"I want to invest in techonology and semiconductor industtries.")

    try:
        client = OpenAI(api_key=openai_api_key)
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_preferences},
            ],
            temperature=0.8,
        )
        return completion.choices[0].message.content
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

    system_content = ("""Respond with the following JSON without any markdowns and surroundings:
                      {
                        "analysis": string (A short analysis of the data),
                        "buy": float,
                        "stop loss": float,
                        "take profit": float,
                      """)

    user_content = (f"I want you to analyze this trade based on the information i will share. what is the buy "
                    f"limit, stop loss order and profit take"
                    f"The next array is {resultsCount} days candles of a ticker {ticker} from the oldest to today."
                    f"The candles: c = close, h = high, l = low, o = open, v = volume."
                    f"{history}")
    try:
        client = OpenAI(api_key=openai_api_key)
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content },
            ],
            temperature=0.8,
        )

        return completion.choices[0].message.content

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/tweet", methods=["GET"])
def tweet():
    ticker = request.args.get("ticker")
    price = request.args.get("price")
    operation = request.args.get("operation")
    papers = request.args.get("papers")

    system_content = """
    You are a financial analyst that write tweets about your trades.
    """
    user_content = f"""
    I just made this operation:
    {operation} {papers} stocks of {ticker} at {price}
    this was my analysis: 
    The recent trend in MSFT shows a recovery after a period of decline, marked by higher 
    highs and higher lows
    in the latter candles. The volume shows a consistent level of activity, indicating strong interest in the stock. The
    recent pullback offers a potential buy opportunity if the trend continues.
    --
    Your mission is to make a tweet about the trade. (optional) consider adding a short explanation about the trade.
    """
    try:
        client = OpenAI(api_key=openai_api_key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
            ],
            temperature=0.8,
        )
        return jsonify({"response": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)