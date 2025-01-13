from flask import current_app
from openai import OpenAI
from typing import Dict, Any, Optional
from openai.types.chat import ChatCompletion
import logging

class OpenAIService:
    def __init__(self):
        self._client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
        self._model = "gpt-4o"  # Move to config if it changes frequently
        self._logger = logging.getLogger(__name__)
    
    def generate_portfolio(
        self, 
        prompt: str,
    ) -> str:
        """Get recommendations using OpenAI.
        
        Args:
            prompt: The formatted prompt to send to OpenAI
            
        Returns:
            str: AI-generated recommendation
            
        Raises:
            OpenAIError: If API call fails
        """
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": current_app.config['PORTFOLIO_SYSTEM_PROMPT']},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )
        
        return completion.choices[0].message.content 
    
    def generate_trade_tweet(
        self, 
        ticker: str, 
        price: float, 
        operation: str, 
        papers: int
    ) -> str:
        """Generate a tweet about a trade using OpenAI."""
        system_content = """
        You are a financial analyst that write tweets about your trades.
        """
        
        user_content = f"""
        I just made this operation:
        {operation} {papers} stocks of {ticker} at {price}
        this was my analysis: 
        The recent trend in {ticker} shows a recovery after a period of decline, marked by higher 
        highs and higher lows in the latter candles. The volume shows a consistent level of activity, 
        indicating strong interest in the stock. The recent pullback offers a potential buy opportunity 
        if the trend continues.
        --
        Your mission is to make a tweet about the trade. (optional) consider adding a short explanation about the trade.
        """
        
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
            ],
            temperature=0.8,
        )
        
        return completion.choices[0].message.content 
    
    def manipulate_portfolio(
        self, 
        prompt: str,
        system_prompt: str = None
    ) -> str:
        """Get recommendations for portfolio manipulation using OpenAI.
        
        Args:
            prompt: The formatted prompt to send to OpenAI
            system_prompt: Optional override for system prompt
            
        Returns:
            str: AI-generated recommendation
            
        Raises:
            OpenAIError: If API call fails
        """
        if system_prompt is None:
            system_prompt = current_app.config['PORTFOLIO_MANIPULATION_PROMPT']
        
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )
        
        return completion.choices[0].message.content 
    
    def assess_risk_and_diversify(
        self, 
        prompt: str
    ) -> str:
        """Get diversification recommendations using OpenAI."""
        try:
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": current_app.config['ASSESSMENT_AND_DIVERSIFICATION_PROMPT']},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            response_content = completion.choices[0].message.content
            self._logger.info(f"OpenAI response: {response_content}")
            return response_content
        except Exception as e:
            self._logger.error(f"Error calling OpenAI API: {str(e)}", exc_info=True)
            raise Exception("Failed to get diversification recommendation from OpenAI")