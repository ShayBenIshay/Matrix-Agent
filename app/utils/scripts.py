import requests

def check_health():
    try:
        response = requests.get('https://services-smart-investor.onrender.com/health')
        print(f"Health check response: {response.text}")
        print(f"Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}") 