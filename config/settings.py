import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    
    # OpenAI prompts
    PORTFOLIO_SYSTEM_PROMPT = """
    You are a financial broker investing for the long term, helping clients to create portfolio.
    Respond with the following JSON without any markdowns and surroundings:
    {
        "analysis": string (A short analysis of the data),
        "portfolio": 
        [{
            "percentage": float (the percentage from my portfolio),
            "ticker": string (it is important to be a VALID wall street ticker Symbol)
        }]
    }
    
    *note - Bitcoin has ETFS in the wall street market with symbol 'IBIT' 
    """

    PORTFOLIO_MANIPULATION_PROMPT = """
    You are a financial broker investing for the long term. you need to decide if and how to 
    manipulate the portfolio of the user.
    you will receive the cash amount, the position on each stock with additional calculations.
    Respond with the following JSON without any markdowns and surroundings:
    {
        "analysis": string (A short analysis of the data),
        "portfolio": 
        [{
            "percentage": float (the percentage from my portfolio),
            "ticker": string (valid wall street ticker Symbol)
        }]
    }
    """

    TRADE_SYSTEM_PROMPT = """
    Respond with the following JSON without any markdowns and surroundings:
    {
        "analysis": string (A short analysis of the data),
        "buy": float,
        "stop loss": float,
        "take profit": float,
    }
    """

    TWEET_SYSTEM_PROMPT = """
    You are a financial analyst that write tweets about your trades.
    """

    ASSESSMENT_AND_DIVERSIFICATION_PROMPT = """
    You are a financial advisor specializing in risk assessment and diversification.
    Provide an assessment of the risk profile of the portfolio and recommendations for balancing the portfolio across sectors, asset classes, and geographies.
    Respond with the following JSON without any markdowns and surroundings:
    {
        "assessment": string (A short assessment of the risk profile),
        "diversify": 
        [ {
            "strategy": string (Description of the diversification strategy),
            "details": string (Additional details about the strategy)
        }]
    }
    """

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

# Export the active configuration
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 