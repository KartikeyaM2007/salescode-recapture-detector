import os
import joblib
import json

def inspect():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "model.joblib")
    meta_path = os.path.join(base_dir, "model_metadata.json")
    
    print("--- Model Inspection ---")
    print(f"model.joblib path: {model_path}")
    
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        print(f"Model object class/type: {type(model)}")
        is_xgb = "xgboost" in str(type(model)).lower()
        is_rf = "randomforest" in str(type(model)).lower()
        print(f"Is XGBoost: {is_xgb}")
        print(f"Is Random Forest: {is_rf}")
    else:
        print("Model file not found.")

    print(f"\nmodel_metadata.json path: {meta_path}")
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            meta = json.load(f)
            print(f"Threshold value: {meta.get('threshold')}")
            print(f"Feature count: {meta.get('feature_count')}")
            feature_names = meta.get("feature_names", [])
            print(f"Feature names count: {len(feature_names)}")
    else:
        print("Metadata file not found.")

    print("\nPreprocessing settings:")
    print("All images are resized to 1024x1024 with light Gaussian Blur (as per features.py)")
    
    print("\nRule boosts enabled:")
    print("Yes (as per predict.py and backend/app.py logic)")

if __name__ == "__main__":
    inspect()
