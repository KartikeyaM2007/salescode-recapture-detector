"""
Usage:
    python predict.py path/to/image.jpg

Outputs a single float from 0 to 1 representing the fraud score.
  0 = real photo
  1 = screen/recapture (fraud)

Optional flags:
    --verbose : Print detailed analysis logs
    --json    : Output result as JSON
"""

import sys
import os
import cv2
import json
import joblib
import argparse
import numpy as np
import xgboost as xgb
import warnings

# Suppress XGBoost DMatrix/device warnings during prediction to ensure clean output
warnings.filterwarnings("ignore")

# We'll import extract_features but use a dummy print to intercept logs if not verbose
from features import extract_features

def get_args():
    parser = argparse.ArgumentParser(description="SalesCode Spot the Fake Photo Predictor")
    parser.add_argument("image_path", type=str, help="Path to the image to classify")
    parser.add_argument("--verbose", action="store_true", help="Print detailed logs")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--no-rules", action="store_true", help="Disable rule-based boosts to see raw model output")
    return parser.parse_args()

def run_prediction(img, log_cb=lambda x: None, no_rules=False):
    log_cb("Extracting features...")
    feature_vector, features_dict = extract_features(img, log_callback=log_cb)

    model_path = os.path.join(os.path.dirname(__file__), "model.joblib")
    meta_path = os.path.join(os.path.dirname(__file__), "model_metadata.json")
    
    threshold = 0.50
    model_name = "XGBoost Classifier"
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            meta = json.load(f)
            threshold = meta.get("threshold", 0.50)
            model_name = meta.get("model_type", model_name)
    
    score = 0.0
    model_status = "heuristic fallback"
    raw_score_pre_boost = 0.0
    boost = 0.0
    
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            
            # The CalibratedClassifierCV might not have set_params in the same way, handle safely
            if hasattr(model, 'set_params'):
                try:
                    model.set_params(device='cpu')
                except:
                    pass
                
            probs = model.predict_proba([feature_vector])[0]
            raw_score = float(probs[1]) 
            raw_score_pre_boost = raw_score
            
            # Rule-Based Safety Boost
            boost = 0.0
            individual_rule_boosts = {}
            num_cues = 0
            natural_scene = False
            
            if no_rules:
                log_cb("Rule boosts bypassed (--no-rules).")
            else:
                bezel = features_dict.get('bezel_score', 0) > 0.5  
                perspective = features_dict.get('perspective_score', 0) > 0.2
                glare = features_dict.get('glare_patch_size', 0) > 0.01
                moire = features_dict.get('moire_score', 0) > 3.0
                banding = features_dict.get('banding_score', 0) > 0.0005
                paper = features_dict.get('paper_texture', 0) > 80
                rect = features_dict.get('rect_contour_score', 0) > 0.75
                strong_glare = features_dict.get('glare_patch_size', 0) > 0.018
                display_texture = features_dict.get('local_fft_hf', 0) > 130
                
                num_cues = sum([bezel, perspective, glare, moire, banding, paper])
                
                if rect and strong_glare and display_texture and raw_score > 0.25:
                    boost += 0.38
                    individual_rule_boosts['rect_glare_texture'] = 0.38
                    log_cb("Screen-like rectangle + glare + display texture detected. Strong boost.")
                elif bezel and moire:
                    boost += 0.10
                    individual_rule_boosts['bezel_moire'] = 0.10
                    log_cb("Visible bezel + Moiré detected. Moderate boost.")
                elif perspective and glare:
                    boost += 0.10
                    individual_rule_boosts['perspective_glare'] = 0.10
                    log_cb("Display rectangle + Glare detected. Moderate boost.")
                elif paper and banding:
                    boost += 0.10
                    individual_rule_boosts['paper_banding'] = 0.10
                    log_cb("Paper texture + Banding detected. Moderate boost.")
                    
                boost = max(-0.15, min(0.45, boost))
                
            final_score = min(1.0, max(0.0, raw_score + boost))
                
            model_status = "sample-trained model"
        except Exception as e:
            log_cb(f"Model load failed: {e}. Falling back to heuristic.")
            model_status = "heuristic fallback (load failed)"
            threshold = 0.50
            final_score = fallback_heuristic(features_dict)
            raw_score_pre_boost = final_score
            boost = 0.0
    else:
        log_cb("No trained model found. Using heuristic fallback...")
        model_status = "heuristic fallback"
        threshold = 0.50
        final_score = fallback_heuristic(features_dict)
        raw_score_pre_boost = final_score
        boost = 0.0

    final_score = max(0.0, min(1.0, final_score))
    log_cb("Final fraud score computed.")
    
    return {
        "final_score": final_score,
        "raw_model_score": raw_score_pre_boost,
        "rule_boost_total": boost,
        "rule_boost_score": boost, # keep for backward compatibility if needed
        "threshold": threshold,
        "predicted_label": 1 if final_score >= threshold else 0,
        "model_type": model_name,
        "metadata_path": meta_path,
        "preprocessing": "1024x1024 Gaussian Blur",
        "top_features": dict(sorted(features_dict.items(), key=lambda item: abs(item[1]), reverse=True)[:5]),
        "model_status": model_status,
        "bezel_score": features_dict.get('bezel_score', 0),
        "screen_border_score": features_dict.get('perspective_score', 0),
        "moire_score": features_dict.get('moire_score', 0),
        "local_fft_score": features_dict.get('local_fft_hf', 0),
        "glare_score": features_dict.get('glare_patch_size', 0),
        "printout_texture_score": features_dict.get('paper_texture', 0),
        "compression_score": features_dict.get('compression_diff', 0),
        "individual_rule_boosts": individual_rule_boosts if 'individual_rule_boosts' in locals() else {},
        "features": features_dict,
        "raw_score_with_boost": raw_score_pre_boost + boost
    }

def predict_image(image_path: str, verbose=False, json_output=False, no_rules=False):
    logs = []
    
    def log_cb(msg):
        logs.append(msg)
        if verbose and not json_output:
            print(f"[LOG] {msg}", file=sys.stderr)
            
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    img = cv2.imread(image_path)
    if img is None:
        with open(image_path, "rb") as f:
            header = f.read(32)
        if b"Exif" in header or b"JFIF" in header:
            print("Error: Could not decode image via OpenCV despite JPEG headers.", file=sys.stderr)
        else:
            print("Error: Could not decode image", file=sys.stderr)
        sys.exit(1)

    result = run_prediction(img, log_cb, no_rules=no_rules)
    result["logs"] = logs

    if json_output:
        print(json.dumps(result))
    else:
        if verbose:
            print(f"[RESULT] Score: {result['final_score']:.4f} ({result['model_status']})")
        else:
            print(f"{result['final_score']:.4f}")

def fallback_heuristic(f_dict):
    hf = min(1.0, f_dict.get('fft_hf_ratio', 0) / 0.5)
    ed = min(1.0, f_dict.get('edge_density', 0) / 0.2)
    lap = min(1.0, f_dict.get('laplacian_var', 0) / 2000.0)
    banding = min(1.0, f_dict.get('banding_score', 0) * 100)
    fraud_score = (hf * 0.4) + (ed * 0.3) + (banding * 0.3)
    return max(0.0, min(1.0, fraud_score))

if __name__ == "__main__":
    args = get_args()
    predict_image(args.image_path, args.verbose, args.json, args.no_rules)
