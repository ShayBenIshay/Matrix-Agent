from flask import Blueprint, request, jsonify
from http import HTTPStatus
from app.services.polygon_service import PolygonService
from app.services.openai_service import OpenAIService
from logging import getLogger

logger = getLogger(__name__)

trade_bp = Blueprint('trade', __name__)

@trade_bp.route("/trade", methods=["GET"])
def analyze_trade():
    """Analyze trade using polygon.io data and trend analysis."""
    try:
        ticker = request.args.get("ticker")
        if not ticker:
            return jsonify({"error": "Ticker is required"}), HTTPStatus.BAD_REQUEST

        polygon_service = PolygonService()
        trend_analysis = polygon_service.analyze_trend(ticker)
        
        return jsonify(trend_analysis), HTTPStatus.OK

    except Exception as e:
        logger.error(f"Error in analyze_trade: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@trade_bp.route("/tweet", methods=["GET"])
def generate_tweet():
    """Generate a tweet about a trade."""
    try:
        params = ["ticker", "price", "operation", "papers"]
        if not all(request.args.get(param) for param in params):
            return jsonify({"error": "Missing required parameters"}), HTTPStatus.BAD_REQUEST

        openai_service = OpenAIService()
        tweet = openai_service.generate_trade_tweet(
            ticker=request.args.get("ticker"),
            price=request.args.get("price"),
            operation=request.args.get("operation"),
            papers=request.args.get("papers")
        )
        
        return jsonify({"response": tweet}), HTTPStatus.OK

    except Exception as e:
        logger.error(f"Error in generate_tweet: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR 