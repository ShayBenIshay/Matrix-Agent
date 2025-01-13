from flask import current_app
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Dict, Any

class PolygonService:
    def __init__(self):
        self.api_key = current_app.config['POLYGON_API_KEY']

    def analyze_trend(self, ticker: str) -> Dict[str, Any]:
        """Analyze trend using SMA data from Polygon.io."""
        url = (
            f"https://api.polygon.io/v1/indicators/sma/"
            f"{ticker}?timespan=day&adjusted=true&window=150&series_type=close&order=asc&limit=10&apiKey"
            f"={self.api_key}"
        )

        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()["results"]
        data_values = data["values"]
        values = np.array([point["value"] for point in data_values])
        indices = np.arange(len(values))

        # Fit linear regression
        X = indices.reshape(-1, 1)
        model = LinearRegression()
        model.fit(X, values)
        slope = model.coef_[0]

        # Classify trend
        epsilon = 0.01
        if slope < -epsilon:
            trend = "Declining"
        elif slope > epsilon:
            trend = "Incline"
        else:
            trend = "Parallel"

        return {
            "trend": trend,
            "slope": float(slope),
            "values": values.tolist()
        } 