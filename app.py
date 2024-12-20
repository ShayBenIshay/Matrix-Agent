from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "hello world"

@app.route("/tweet", methods=["GET"])
def tweet():
    ticker = request.args.get("ticker")
    price = request.args.get("price")
    operation = request.args.get("operation")
    papers = request.args.get("papers")

    content = f"{operation} {papers} stocks of {ticker} at {price}"
    print(content)
    try:
        client = OpenAI(api_key=api_key)
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
