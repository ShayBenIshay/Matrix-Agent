import json
from typing import Dict, Any
import logging
import requests

from flask import current_app
from .openai_service import OpenAIService
from app.utils.auth_utils import get_auth_token

class PortfolioService:
    def __init__(self):
        self._openai_service = OpenAIService()
        self._logger = logging.getLogger(__name__)  # Initialize logger
        self._token = None
    
    def _get_token(self):
        if not self._token:
            self._token = get_auth_token()
        return self._token
    
    def generate(
        self,
        prompt: str = "",
    ) -> Dict[str, Any]:
        """Get portfolio recommendations using OpenAI.
        
        Args:
            additional_info: Optional context for the recommendation
            
        Returns:
            Dict[str, Any]: AI-generated portfolio recommendation as JSON
            
        Raises:
            ValueError: If input parameters are invalid
            json.JSONDecodeError: If AI response is not valid JSON
        """
            
        response = self._openai_service.generate_portfolio(prompt=prompt)
        return json.loads(response)  # Parse string response into JSON directly 
    
    def manipulate(
        self,
        cash: float,
        totals: Dict[str, Any],
        additional_info: str = ""
    ) -> Dict[str, Any]:
        """Manipulate existing portfolio based on current holdings and cash.
        
        Args:
            cash: Available liquid cash
            totals: Current portfolio holdings
            additional_info: Optional context for the recommendation
            
        Returns:
            Dict[str, Any]: AI-generated portfolio recommendation as JSON
            
        Raises:
            ValueError: If input parameters are invalid
            json.JSONDecodeError: If AI response is not valid JSON
        """
        user_preferences = (
            f"I want you to decide after analyzing of the market if and how to change my portfolio. "
            f"This is my current portfolio:\n"
            f"{totals}\n"
            f"i also have liquid cash: {cash}\n"
            f"{additional_info}\n"
            f"your mission is decide how my portfolio should look today after your analyze."
        )
        
        # Calculate total current portfolio value
        total_value = cash + sum(stock['currentValue'] for stock in totals.values())

        # Get AI-generated recommendation
        response = self._openai_service.manipulate_portfolio(
            prompt=user_preferences,
            system_prompt=current_app.config['PORTFOLIO_MANIPULATION_PROMPT']
        )
        recommendation = json.loads(response)
        
        # Log the recommendation
        self._logger.info("AI-generated recommendation: %s", recommendation)

        # Obtain authentication token
        token = self._get_token()
        self._logger.info(f"Using token: {token}")
        
        # Calculate buy/sell actions and add additional information
        for stock in recommendation['portfolio']:
            ticker = stock['ticker']
            desired_percentage = stock.pop('percentage') / 100  # Change key to desiredPercentage
            stock['desiredPercentage'] = desired_percentage * 100  # Store as percentage

            desired_value = total_value * desired_percentage

            if ticker in totals:
                current_value = totals[ticker]['currentValue']
                current_price = totals[ticker]['currentPrice']
                current_percentage = (current_value / total_value) * 100

                stock['currentPrice'] = current_price
                stock['currentPercentage'] = current_percentage

                difference = desired_value - current_value

                if desired_percentage == 0 or desired_value < current_value:
                    # Sell all shares if desired percentage is zero or less than current
                    stock['action'] = 'sell'
                    stock['papers'] = totals[ticker]['position']
                else:
                    stock['action'] = 'buy' if difference > 0 else 'sell'
                    stock['papers'] = abs(difference) // current_price
            else:
                # Fetch current price for new stocks
                headers = {'Authorization': f'Bearer {token}'}
                response = requests.get(f"http://localhost:3030/throttle?name=prev&ticker={ticker}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    self._logger.info(f"API response for {ticker}: {data}")
                    current_price = data.get('close')
                    if current_price is None:
                        self._logger.error(f"'close' key not found in response for {ticker}")
                        stock['currentPrice'] = None
                        stock['papers'] = 0
                        continue

                    stock['currentPrice'] = current_price
                    stock['currentPercentage'] = 0

                    # Calculate papers to buy
                    stock['action'] = 'buy'
                    stock['papers'] = desired_value // current_price
                else:
                    self._logger.error("Failed to fetch current price for %s", ticker)
                    stock['currentPrice'] = None
                    stock['papers'] = 0

        return recommendation 
    
    def assess_risk_and_diversify(
        self,
        cash: float,
        totals: Dict[str, Any],
        additional_info: str = ""
    ) -> Dict[str, Any]:
        """Assess risk and recommend diversification strategies.
        
        Args:
            cash: Available liquid cash
            totals: Current portfolio holdings
            additional_info: Optional context for the recommendation
            
        Returns:
            Dict[str, Any]: AI-generated assessment and diversification recommendation
        """
        # Prepare the prompt for OpenAI
        user_preferences = (
            f"Assess the risk profile of the following portfolio and suggest diversification strategies:\n"
            f"Current portfolio:\n{totals}\n"
            f"Available cash: {cash}\n"
            f"{additional_info}\n"
            f"Provide an assessment of the risk and recommendations for balancing the portfolio across sectors, asset classes, and geographies."
        )
        print('portfolio_service.assess_risk_and_diversify')
        # Get AI-generated diversification recommendation
        response = self._openai_service.assess_risk_and_diversify(prompt=user_preferences)
        recommendation = json.loads(response)
        # Log the recommendation
        self._logger.info("AI-generated assessment and diversification recommendation: %s", recommendation)

        return {
            "assessment": recommendation.get("assessment", ""),
            "diversify": recommendation.get("diversify", [])
        } 