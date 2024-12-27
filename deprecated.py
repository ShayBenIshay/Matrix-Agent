# def get_trade(portfolio):
#     base_url = "http://127.0.0.1:5000/trade"
#     str = ""
#     for item in portfolio:
#         ticker = item["Ticker"]
#
#         # Create query parameters
#         params = {
#             'ticker': ticker,
#             'count': 10,
#             'timespan': 'day'
#         }
#
#         # Make the GET request
#         response = requests.get(base_url, params=params)
#
#         # Check the response status and handle accordingly
#         if response.status_code == 200:
#             str = str + f"Response for {ticker}: {response.json()}"
#             # print(f"Response for {ticker}: {response.json()}")
#         else:
#             str += f"Failed to get data for {ticker}. Status code: {response.status_code}"
#             # print(f"Failed to get data for {ticker}. Status code: {response.status_code}")
#     return str
