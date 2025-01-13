from flask import Flask
from flask_cors import CORS
from config.settings import config

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(config[config_name])
    
    # Initialize CORS
    CORS(app, resources={r"/*": {"origins": app.config['FRONTEND_URL']}})
    
    # Register blueprints
    from app.routes.portfolio import portfolio_bp
    from app.routes.trade import trade_bp
    
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(trade_bp)
    
    return app 