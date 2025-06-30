import pandas as pd
import numpy as np
from typing import Tuple

def calculate_esg_score(sales_data: pd.DataFrame, environmental_data: dict = None) -> Tuple[float, dict, dict]:
    """
    Calculates an ESG score with enhanced logic.
    Returns: (esg_score, social_impact, environmental_impact)
    """
    if sales_data.empty:
        return 0.0, {"fair_trade_index": 0.0, "community_engagement": "None"}, {"carbon_footprint_reduction_tons": 0.0, "water_usage_efficiency": "None"}
    
    # Sales-based metrics
    total_sales = sales_data['quantity'].sum()
    unique_products = sales_data['product_id'].nunique()
    
    # Social impact: weighted by sales volume and product diversity
    fair_trade_index = min(total_sales * 0.005, 0.95)
    community_engagement = "High" if unique_products > 3 else "Moderate" if unique_products > 1 else "Low"
    social_impact = {
        "fair_trade_index": fair_trade_index,
        "community_engagement": community_engagement
    }
    
    # Environmental impact: mock calculations (in a real app, use IoT or external data)
    carbon_reduction = total_sales * 0.002 if environmental_data is None else environmental_data.get('carbon_reduction', 1.2)
    water_efficiency = "High" if total_sales > 1000 else "Moderate"
    environmental_impact = {
        "carbon_footprint_reduction_tons": carbon_reduction,
        "water_usage_efficiency": water_efficiency
    }
    
    # ESG score: weighted combination of social and environmental factors
    esg_score = np.clip((fair_trade_index * 50) + (unique_products * 10) + (carbon_reduction * 20), 0, 100)
    
    return float(esg_score), social_impact, environmental_impact
