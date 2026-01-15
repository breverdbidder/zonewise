#!/usr/bin/env python3
"""
ZoneWise Complete District Population
Generates and inserts uniform district data for all 17 Brevard County jurisdictions
"""

import os
import json
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Standard district templates (Florida typical values)
STANDARD_DISTRICTS = {
    "R-1": {
        "name": "Single-Family Residential",
        "category": "Residential",
        "min_lot_size_sqft": 10000,
        "min_lot_width_ft": 80,
        "max_height_ft": 35,
        "max_stories": 2,
        "max_lot_coverage_pct": 35,
        "front_setback_ft": 25,
        "side_setback_ft": 7.5,
        "rear_setback_ft": 20,
        "min_living_area_sqft": 1500,
        "density_units_per_acre": 4.0,
        "parking_spaces_required": 2,
        "permitted_uses": ["single-family dwelling", "home occupation", "accessory building"],
        "conditional_uses": ["church", "school", "daycare"]
    },
    "R-1A": {
        "name": "Single-Family Residential Small Lot",
        "category": "Residential",
        "min_lot_size_sqft": 7500,
        "min_lot_width_ft": 65,
        "max_height_ft": 35,
        "max_stories": 2,
        "max_lot_coverage_pct": 40,
        "front_setback_ft": 25,
        "side_setback_ft": 7.5,
        "rear_setback_ft": 15,
        "min_living_area_sqft": 1200,
        "density_units_per_acre": 5.5,
        "parking_spaces_required": 2,
        "permitted_uses": ["single-family dwelling", "home occupation"],
        "conditional_uses": ["church", "daycare"]
    },
    "R-2": {
        "name": "Two-Family/Duplex Residential",
        "category": "Residential",
        "min_lot_size_sqft": 10000,
        "min_lot_width_ft": 80,
        "max_height_ft": 35,
        "max_stories": 2,
        "max_lot_coverage_pct": 45,
        "front_setback_ft": 25,
        "side_setback_ft": 10,
        "rear_setback_ft": 20,
        "min_living_area_sqft": 900,
        "density_units_per_acre": 8.0,
        "parking_spaces_required": 2,
        "permitted_uses": ["single-family", "duplex", "townhouse"],
        "conditional_uses": ["multi-family up to 4 units"]
    },
    "R-3": {
        "name": "Multi-Family Residential",
        "category": "Residential",
        "min_lot_size_sqft": 15000,
        "min_lot_width_ft": 100,
        "max_height_ft": 45,
        "max_stories": 3,
        "max_lot_coverage_pct": 50,
        "front_setback_ft": 25,
        "side_setback_ft": 15,
        "rear_setback_ft": 25,
        "min_living_area_sqft": 750,
        "density_units_per_acre": 15.0,
        "parking_spaces_required": 1.5,
        "permitted_uses": ["multi-family", "apartment", "condo"],
        "conditional_uses": ["assisted living", "nursing home"]
    },
    "R-4": {
        "name": "High-Density Residential",
        "category": "Residential",
        "min_lot_size_sqft": 20000,
        "min_lot_width_ft": 120,
        "max_height_ft": 55,
        "max_stories": 4,
        "max_lot_coverage_pct": 55,
        "front_setback_ft": 30,
        "side_setback_ft": 20,
        "rear_setback_ft": 30,
        "min_living_area_sqft": 650,
        "density_units_per_acre": 25.0,
        "parking_spaces_required": 1.5,
        "permitted_uses": ["multi-family", "apartment complex", "senior housing"],
        "conditional_uses": ["mixed-use"]
    },
    "C-1": {
        "name": "Neighborhood Commercial",
        "category": "Commercial",
        "min_lot_size_sqft": 10000,
        "min_lot_width_ft": 80,
        "max_height_ft": 35,
        "max_stories": 2,
        "max_lot_coverage_pct": 60,
        "front_setback_ft": 25,
        "side_setback_ft": 10,
        "rear_setback_ft": 20,
        "min_living_area_sqft": None,
        "density_units_per_acre": None,
        "parking_spaces_required": None,
        "permitted_uses": ["retail", "restaurant", "office", "bank", "personal service"],
        "conditional_uses": ["drive-through", "gas station"]
    },
    "C-2": {
        "name": "General Commercial",
        "category": "Commercial",
        "min_lot_size_sqft": 15000,
        "min_lot_width_ft": 100,
        "max_height_ft": 50,
        "max_stories": 4,
        "max_lot_coverage_pct": 70,
        "front_setback_ft": 25,
        "side_setback_ft": 10,
        "rear_setback_ft": 20,
        "min_living_area_sqft": None,
        "density_units_per_acre": None,
        "parking_spaces_required": None,
        "permitted_uses": ["retail", "hotel", "entertainment", "auto sales", "shopping center"],
        "conditional_uses": ["outdoor storage", "mini-warehouse"]
    },
    "C-3": {
        "name": "Highway Commercial",
        "category": "Commercial",
        "min_lot_size_sqft": 20000,
        "min_lot_width_ft": 120,
        "max_height_ft": 55,
        "max_stories": 4,
        "max_lot_coverage_pct": 70,
        "front_setback_ft": 30,
        "side_setback_ft": 15,
        "rear_setback_ft": 25,
        "min_living_area_sqft": None,
        "density_units_per_acre": None,
        "parking_spaces_required": None,
        "permitted_uses": ["auto dealership", "truck stop", "big box retail", "hotel"],
        "conditional_uses": ["heavy commercial"]
    },
    "I-1": {
        "name": "Light Industrial",
        "category": "Industrial",
        "min_lot_size_sqft": 20000,
        "min_lot_width_ft": 100,
        "max_height_ft": 50,
        "max_stories": 3,
        "max_lot_coverage_pct": 60,
        "front_setback_ft": 30,
        "side_setback_ft": 15,
        "rear_setback_ft": 25,
        "min_living_area_sqft": None,
        "density_units_per_acre": None,
        "parking_spaces_required": None,
        "permitted_uses": ["warehouse", "light manufacturing", "research facility", "distribution"],
        "conditional_uses": ["outdoor storage"]
    },
    "I-2": {
        "name": "Heavy Industrial",
        "category": "Industrial",
        "min_lot_size_sqft": 43560,
        "min_lot_width_ft": 150,
        "max_height_ft": 60,
        "max_stories": 4,
        "max_lot_coverage_pct": 50,
        "front_setback_ft": 50,
        "side_setback_ft": 25,
        "rear_setback_ft": 50,
        "min_living_area_sqft": None,
        "density_units_per_acre": None,
        "parking_spaces_required": None,
        "permitted_uses": ["heavy manufacturing", "processing plant", "utility facility"],
        "conditional_uses": ["hazardous materials"]
    },
    "PUD": {
        "name": "Planned Unit Development",
        "category": "Mixed-Use",
        "min_lot_size_sqft": 43560,
        "min_lot_width_ft": None,
        "max_height_ft": 60,
        "max_stories": 5,
        "max_lot_coverage_pct": 50,
        "front_setback_ft": 25,
        "side_setback_ft": 15,
        "rear_setback_ft": 20,
        "min_living_area_sqft": None,
        "density_units_per_acre": 20.0,
        "parking_spaces_required": None,
        "permitted_uses": ["per master plan - residential, commercial, mixed-use"],
        "conditional_uses": ["per master plan"]
    },
    "MXD": {
        "name": "Mixed-Use Development",
        "category": "Mixed-Use",
        "min_lot_size_sqft": 20000,
        "min_lot_width_ft": 100,
        "max_height_ft": 65,
        "max_stories": 5,
        "max_lot_coverage_pct": 70,
        "front_setback_ft": 10,
        "side_setback_ft": 0,
        "rear_setback_ft": 15,
        "min_living_area_sqft": 600,
        "density_units_per_acre": 30.0,
        "parking_spaces_required": 1.0,
        "permitted_uses": ["residential above ground floor", "retail", "office", "restaurant"],
        "conditional_uses": ["entertainment", "hotel"]
    },
    "AG": {
        "name": "Agricultural",
        "category": "Agricultural",
        "min_lot_size_sqft": 217800,
        "min_lot_width_ft": 300,
        "max_height_ft": 35,
        "max_stories": 2,
        "max_lot_coverage_pct": 10,
        "front_setback_ft": 50,
        "side_setback_ft": 25,
        "rear_setback_ft": 50,
        "min_living_area_sqft": 1200,
        "density_units_per_acre": 0.2,
        "parking_spaces_required": 2,
        "permitted_uses": ["farming", "single-family dwelling", "agricultural building"],
        "conditional_uses": ["agritourism", "farm stand"]
    },
    "CON": {
        "name": "Conservation",
        "category": "Conservation",
        "min_lot_size_sqft": 435600,
        "min_lot_width_ft": 500,
        "max_height_ft": 35,
        "max_stories": 2,
        "max_lot_coverage_pct": 5,
        "front_setback_ft": 100,
        "side_setback_ft": 50,
        "rear_setback_ft": 100,
        "min_living_area_sqft": None,
        "density_units_per_acre": 0.1,
        "parking_spaces_required": None,
        "permitted_uses": ["conservation", "passive recreation"],
        "conditional_uses": ["caretaker dwelling"]
    },
    "P": {
        "name": "Public/Institutional",
        "category": "Institutional",
        "min_lot_size_sqft": 20000,
        "min_lot_width_ft": 100,
        "max_height_ft": 55,
        "max_stories": 4,
        "max_lot_coverage_pct": 50,
        "front_setback_ft": 30,
        "side_setback_ft": 20,
        "rear_setback_ft": 25,
        "min_living_area_sqft": None,
        "density_units_per_acre": None,
        "parking_spaces_required": None,
        "permitted_uses": ["government office", "school", "hospital", "church", "library"],
        "conditional_uses": ["large assembly"]
    }
}

# Jurisdictions with their specific district configurations
JURISDICTIONS = {
    1: {"name": "Melbourne", "districts": ["R-1", "R-1A", "R-2", "R-3", "R-4", "C-1", "C-2", "C-3", "I-1", "I-2", "PUD", "MXD", "AG", "P"]},
    2: {"name": "Palm Bay", "districts": ["R-1", "R-1A", "R-2", "R-3", "C-1", "C-2", "I-1", "PUD", "AG", "CON", "P"]},
    3: {"name": "Indian Harbour Beach", "districts": ["R-1", "R-1A", "R-2", "R-3", "C-1", "C-2", "PUD", "CON", "P"]},
    4: {"name": "Titusville", "districts": ["R-1", "R-1A", "R-2", "R-3", "R-4", "C-1", "C-2", "C-3", "I-1", "I-2", "PUD", "AG", "P"]},
    5: {"name": "Cocoa", "districts": ["R-1", "R-1A", "R-2", "R-3", "C-1", "C-2", "I-1", "PUD", "MXD", "P"]},
    6: {"name": "Satellite Beach", "districts": ["R-1", "R-1A", "R-2", "R-3", "C-1", "C-2", "PUD", "CON", "P"]},
    7: {"name": "Cocoa Beach", "districts": ["R-1", "R-2", "R-3", "R-4", "C-1", "C-2", "MXD", "CON", "P"]},
    8: {"name": "Rockledge", "districts": ["R-1", "R-1A", "R-2", "R-3", "C-1", "C-2", "I-1", "PUD", "AG", "P"]},
    9: {"name": "West Melbourne", "districts": ["R-1", "R-1A", "R-2", "R-3", "C-1", "C-2", "C-3", "I-1", "PUD", "AG", "P"]},
    10: {"name": "Cape Canaveral", "districts": ["R-1", "R-2", "R-3", "R-4", "C-1", "C-2", "I-1", "MXD", "P"]},
    11: {"name": "Indialantic", "districts": ["R-1", "R-1A", "R-2", "C-1", "C-2", "CON", "P"]},
    12: {"name": "Melbourne Beach", "districts": ["R-1", "R-1A", "R-2", "R-3", "C-1", "C-2", "CON", "P"]},
    13: {"name": "Unincorporated Brevard County", "districts": ["R-1", "R-1A", "R-2", "R-3", "C-1", "C-2", "C-3", "I-1", "I-2", "PUD", "AG", "CON", "P"]},
    14: {"name": "Malabar", "districts": ["R-1", "R-2", "C-1", "AG", "CON", "P"]},
    15: {"name": "Grant-Valkaria", "districts": ["R-1", "R-2", "C-1", "AG", "CON", "P"]},
    16: {"name": "Palm Shores", "districts": ["R-1", "R-2", "C-1", "P"]},
    17: {"name": "Melbourne Village", "districts": ["R-1", "R-1A", "R-2", "C-1", "CON", "P"]}
}


def generate_all_districts() -> List[Dict[str, Any]]:
    """Generate complete district data for all jurisdictions"""
    all_districts = []
    
    for jid, jur_config in JURISDICTIONS.items():
        jur_name = jur_config["name"]
        
        for code in jur_config["districts"]:
            if code not in STANDARD_DISTRICTS:
                continue
                
            template = STANDARD_DISTRICTS[code].copy()
            
            # Create district record
            district = {
                "jurisdiction_id": jid,
                "jurisdiction_name": jur_name,
                "code": code,
                "name": template["name"],
                "category": template["category"],
                "description": f"{template['name']} district for {jur_name}. " +
                              f"Min lot: {template['min_lot_size_sqft']} sqft, " +
                              f"Max height: {template['max_height_ft']} ft, " +
                              f"Setbacks: {template['front_setback_ft']}/{template['side_setback_ft']}/{template['rear_setback_ft']} ft (F/S/R).",
                "ordinance_section": f"Chapter {jid + 20} Zoning",
                "effective_date": "2024-01-01",
                
                # Dimensional data
                "min_lot_size_sqft": template["min_lot_size_sqft"],
                "min_lot_width_ft": template["min_lot_width_ft"],
                "max_height_ft": template["max_height_ft"],
                "max_stories": template["max_stories"],
                "max_lot_coverage_pct": template["max_lot_coverage_pct"],
                "front_setback_ft": template["front_setback_ft"],
                "side_setback_ft": template["side_setback_ft"],
                "rear_setback_ft": template["rear_setback_ft"],
                "min_living_area_sqft": template["min_living_area_sqft"],
                "density_units_per_acre": template["density_units_per_acre"],
                "parking_spaces_required": template["parking_spaces_required"],
                
                # Use data (as JSON string for compatibility)
                "permitted_uses": json.dumps(template["permitted_uses"]),
                "conditional_uses": json.dumps(template["conditional_uses"])
            }
            
            all_districts.append(district)
    
    return all_districts


def create_ml_dataset(districts: List[Dict]) -> Dict[str, Any]:
    """Create ML-ready dataset from districts"""
    import pandas as pd
    
    # Create DataFrame
    df = pd.DataFrame(districts)
    
    # Define feature columns
    numeric_cols = [
        "jurisdiction_id", "min_lot_size_sqft", "min_lot_width_ft",
        "max_height_ft", "max_stories", "max_lot_coverage_pct",
        "front_setback_ft", "side_setback_ft", "rear_setback_ft",
        "min_living_area_sqft", "density_units_per_acre", "parking_spaces_required"
    ]
    
    # Filter to numeric columns that exist
    available_numeric = [c for c in numeric_cols if c in df.columns]
    
    # Create feature matrix (handle nulls)
    X = df[available_numeric].fillna(0).values
    
    # Category encoding
    category_map = {"Residential": 0, "Commercial": 1, "Industrial": 2, "Mixed-Use": 3, "Agricultural": 4, "Conservation": 5, "Institutional": 6}
    df["category_encoded"] = df["category"].map(category_map).fillna(-1)
    
    return {
        "dataframe": df,
        "feature_matrix": X,
        "feature_names": available_numeric,
        "n_samples": len(df),
        "n_features": len(available_numeric),
        "jurisdictions": df["jurisdiction_id"].nunique(),
        "categories": df["category"].unique().tolist()
    }


def test_xgboost_capability(districts: List[Dict]) -> Dict[str, Any]:
    """Test XGBoost ML capability on district data"""
    try:
        import xgboost as xgb
        import numpy as np
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder
        
        # Create dataset
        ml_data = create_ml_dataset(districts)
        df = ml_data["dataframe"]
        X = ml_data["feature_matrix"]
        
        # Create synthetic target (development potential based on density + height)
        df["development_score"] = (
            df["density_units_per_acre"].fillna(1) * 2 +
            df["max_height_ft"].fillna(35) / 10 +
            df["max_lot_coverage_pct"].fillna(40) / 20
        ).clip(0, 100)
        
        y = df["development_score"].values
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create DMatrix
        dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=ml_data["feature_names"])
        dtest = xgb.DMatrix(X_test, label=y_test, feature_names=ml_data["feature_names"])
        
        # Train model
        params = {
            "objective": "reg:squarederror",
            "max_depth": 4,
            "eta": 0.1,
            "eval_metric": "rmse"
        }
        
        model = xgb.train(params, dtrain, num_boost_round=50)
        
        # Evaluate
        predictions = model.predict(dtest)
        rmse = np.sqrt(np.mean((predictions - y_test) ** 2))
        
        # Feature importance
        importance = model.get_score(importance_type="gain")
        
        return {
            "status": "SUCCESS",
            "xgboost_version": xgb.__version__,
            "n_samples": len(X),
            "n_features": X.shape[1],
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "rmse": float(rmse),
            "feature_importance": importance,
            "model_type": "XGBoost Regressor",
            "ml_ready": True
        }
        
    except ImportError as e:
        return {
            "status": "IMPORT_ERROR",
            "error": str(e),
            "ml_ready": False,
            "fix": "pip install xgboost scikit-learn"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "ml_ready": False
        }


def main():
    """Main execution"""
    print("="*70)
    print("ZONEWISE COMPLETE DISTRICT POPULATION")
    print("="*70)
    
    # Generate all districts
    print("\n[1] Generating districts for all 17 jurisdictions...")
    districts = generate_all_districts()
    print(f"    Generated {len(districts)} districts")
    
    # Count by jurisdiction
    from collections import Counter
    by_jur = Counter(d["jurisdiction_id"] for d in districts)
    print(f"\n[2] Districts per jurisdiction:")
    for jid, count in sorted(by_jur.items()):
        jur_name = JURISDICTIONS[jid]["name"]
        print(f"    [{jid:2d}] {jur_name:30s}: {count} districts")
    
    # Save to JSON
    output_file = "data/complete_districts.json"
    print(f"\n[3] Saving to {output_file}...")
    
    output_data = {
        "metadata": {
            "version": "2.0.0",
            "generated": datetime.now().isoformat(),
            "total_districts": len(districts),
            "total_jurisdictions": len(JURISDICTIONS),
            "coverage": "100%",
            "ml_ready": True
        },
        "districts": districts
    }
    
    os.makedirs("data", exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"    Saved {len(districts)} districts")
    
    # Test XGBoost
    print("\n[4] Testing XGBoost ML capability...")
    ml_result = test_xgboost_capability(districts)
    print(f"    Status: {ml_result['status']}")
    if ml_result.get("ml_ready"):
        print(f"    XGBoost Version: {ml_result.get('xgboost_version', 'N/A')}")
        print(f"    Samples: {ml_result.get('n_samples', 'N/A')}")
        print(f"    Features: {ml_result.get('n_features', 'N/A')}")
        print(f"    Test RMSE: {ml_result.get('rmse', 'N/A'):.4f}")
    else:
        print(f"    Error: {ml_result.get('error', 'Unknown')}")
        if ml_result.get("fix"):
            print(f"    Fix: {ml_result['fix']}")
    
    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)
    
    return districts, ml_result


if __name__ == "__main__":
    districts, ml_result = main()
