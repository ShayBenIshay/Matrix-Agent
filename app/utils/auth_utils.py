import requests
import os
from dotenv import load_dotenv

load_dotenv()

AGENT_EMAIL = os.getenv("SERVICE_AGENT_EMAIL")
AGENT_PASSWORD = os.getenv("SERVICE_AGENT_PASSWORD")

def get_auth_token():
    """Authenticate and obtain a token for API access."""
    auth_url = "http://localhost:3030/authentication"
    credentials = {
        "strategy": "local",
        "email": AGENT_EMAIL,
        "password": AGENT_PASSWORD
    }
    
    try:
        response = requests.post(auth_url, json=credentials)
        response.raise_for_status()  # Raise an error for bad responses
        token = response.json().get('accessToken')
        if not token:
            raise Exception("Token not found in response")
        return token
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise Exception("Failed to authenticate and obtain token")
    except Exception as e:
        print(f"Error: {e}")
        raise 