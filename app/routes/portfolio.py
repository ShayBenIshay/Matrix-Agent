from flask import Blueprint, request, jsonify
from http import HTTPStatus
from app.services.portfolio_service import PortfolioService
from logging import getLogger
from typing import Dict, Any

logger = getLogger(__name__)
portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/build-portfolio', methods=['GET'])
def build_portfolio():
    """Get initial portfolio recommendations based on user preferences and cash."""
    try:
        prompt = request.args.get('prompt', '')
        
        portfolio_service = PortfolioService()
        result = portfolio_service.generate(
            prompt=prompt
        )
        
        return jsonify({"recommendation": result}), HTTPStatus.OK
        
    except ValueError as e:
        logger.warning(f"Invalid request: {str(e)}")
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        logger.error(f"Error in build_portfolio: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

def validate_portfolio_request(data: Dict[str, Any]) -> None:
    """Validate the portfolio manipulation request data."""
    if not isinstance(data, dict):
        raise ValueError("Invalid request body")
        
    if not isinstance(data.get('cash'), (int, float)):
        raise ValueError("Cash must be a number")
        
    if not isinstance(data.get('totals'), dict):
        raise ValueError("Totals must be a dictionary of holdings")

@portfolio_bp.route('/manipulate-portfolio', methods=['POST'])
def manipulate_portfolio():
    """Get recommendations for portfolio changes based on current holdings."""
    try:
        data = request.get_json()
        validate_portfolio_request(data)

        portfolio_service = PortfolioService()
        result = portfolio_service.manipulate(
            cash=data['cash'],
            totals=data['totals'],
            additional_info=data.get('additionalInfo', '')
        )

        return jsonify(result), HTTPStatus.OK
        
    except ValueError as e:
        logger.warning(f"Invalid request: {str(e)}")
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        logger.error(f"Error in manipulate_portfolio: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@portfolio_bp.route('/assess-risk-and-diversify', methods=['POST'])
def assess_risk_and_diversify():
    """Assess risk and recommend diversification strategies."""
    try:
        data = request.get_json()
        validate_portfolio_request(data)

        portfolio_service = PortfolioService()
        result = portfolio_service.assess_risk_and_diversify(
            cash=data['cash'],
            totals=data['totals'],
            additional_info=data.get('additionalInfo', '')
        )
        return jsonify(result), HTTPStatus.OK
        
    except ValueError as e:
        logger.warning(f"Invalid request: {str(e)}")
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        logger.error(f"Error in assess_risk_and_diversify: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR 