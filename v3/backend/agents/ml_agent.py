"""
ZoneWise V3 - ML Agent
Uses XGBoost models for price prediction and probability estimation.
Local model execution - no LLM calls needed.
"""

from typing import Optional
import structlog
import numpy as np

logger = structlog.get_logger()


class MLAgent:
    """
    Agent for ML-based predictions.
    
    Models:
    - Price prediction: Estimates property value
    - Win probability: Probability of winning auction at given price
    """
    
    def __init__(self):
        self.price_model = None
        self.prob_model = None
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained XGBoost models."""
        try:
            import xgboost as xgb
            import os
            
            model_dir = os.environ.get("MODEL_DIR", "models")
            
            # Try to load models if they exist
            price_path = f"{model_dir}/price_model.json"
            prob_path = f"{model_dir}/probability_model.json"
            
            if os.path.exists(price_path):
                self.price_model = xgb.XGBRegressor()
                self.price_model.load_model(price_path)
                logger.info("Price model loaded")
            
            if os.path.exists(prob_path):
                self.prob_model = xgb.XGBClassifier()
                self.prob_model.load_model(prob_path)
                logger.info("Probability model loaded")
                
        except Exception as e:
            logger.warning("ML models not loaded", error=str(e))
    
    async def execute(
        self,
        parcel_id: Optional[str] = None,
        features: Optional[dict] = None,
    ) -> dict:
        """Execute ML predictions."""
        logger.info("ML agent executing", parcel_id=parcel_id)
        
        result = {
            "predicted_value": None,
            "value_confidence": 0.0,
            "win_probability": None,
            "prob_confidence": 0.0,
            "model_version": "v1.0",
        }
        
        try:
            # Get features for the parcel
            feature_vector = await self._prepare_features(parcel_id, features)
            
            if feature_vector is not None:
                # Price prediction
                if self.price_model:
                    prediction = self.price_model.predict([feature_vector])[0]
                    result["predicted_value"] = float(prediction)
                    result["value_confidence"] = 0.644  # From BidDeed.AI accuracy
                else:
                    # Fallback: simple estimation
                    result["predicted_value"] = self._fallback_price_estimate(features)
                    result["value_confidence"] = 0.5
                
                # Win probability
                if self.prob_model:
                    prob = self.prob_model.predict_proba([feature_vector])[0][1]
                    result["win_probability"] = float(prob)
                    result["prob_confidence"] = 0.644
                else:
                    # Fallback
                    result["win_probability"] = 0.5
                    result["prob_confidence"] = 0.3
            
            logger.info(
                "ML agent completed",
                value=result["predicted_value"],
                probability=result["win_probability"],
            )
            
        except Exception as e:
            logger.error("ML agent error", error=str(e))
            result["error"] = str(e)
        
        return result
    
    async def _prepare_features(
        self,
        parcel_id: Optional[str],
        features: Optional[dict],
    ) -> Optional[np.ndarray]:
        """Prepare feature vector for ML models."""
        if not features:
            features = {}
        
        # Feature list (must match training data)
        feature_names = [
            "lot_sqft",
            "building_sqft",
            "bedrooms",
            "bathrooms",
            "year_built",
            "assessed_value",
            "zone_numeric",
            "foreclosure_amount",
            "days_on_market",
        ]
        
        # Extract features with defaults
        vector = [
            features.get("lot_sqft", 7500),
            features.get("building_sqft", 1500),
            features.get("bedrooms", 3),
            features.get("bathrooms", 2),
            features.get("year_built", 1990),
            features.get("assessed_value", 200000),
            self._encode_zone(features.get("zone_code", "R-1")),
            features.get("foreclosure_amount", 0),
            features.get("days_on_market", 30),
        ]
        
        return np.array(vector)
    
    def _encode_zone(self, zone_code: str) -> int:
        """Encode zone code to numeric."""
        zone_map = {
            "R-1": 1, "R-1A": 2, "R-2": 3, "R-3": 4, "R-4": 5,
            "C-1": 10, "C-2": 11, "C-3": 12,
            "I-1": 20, "I-2": 21,
            "PUD": 30, "MU": 31,
        }
        return zone_map.get(zone_code.upper(), 0)
    
    def _fallback_price_estimate(self, features: Optional[dict]) -> float:
        """Simple price estimation when models unavailable."""
        if not features:
            return 250000
        
        base_price = 150000
        
        # Lot size: $10/sqft
        lot_sqft = features.get("lot_sqft", 7500)
        base_price += lot_sqft * 10
        
        # Building: $150/sqft
        building_sqft = features.get("building_sqft", 1500)
        base_price += building_sqft * 150
        
        # Bedrooms: $15,000 each
        bedrooms = features.get("bedrooms", 3)
        base_price += bedrooms * 15000
        
        return base_price
