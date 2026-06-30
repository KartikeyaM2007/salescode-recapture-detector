import os
import glob
import json
import argparse
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import StratifiedKFold, train_test_split
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

from features import extract_features, get_feature_names

def ensure_reports_dir():
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    return reports_dir

def gather_data(data_dir: str):
    cache_dir = os.path.join(data_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_x = os.path.join(cache_dir, "X.npy")
    cache_y = os.path.join(cache_dir, "y.npy")
    cache_g = os.path.join(cache_dir, "groups.npy")
    
    if os.path.exists(cache_x) and os.path.exists(cache_y) and os.path.exists(cache_g):
        print("Loading cached features from disk...")
        return np.load(cache_x), np.load(cache_y), np.load(cache_g)

    X = []
    y = []
    groups = []
    
    real_dir = os.path.join(data_dir, "real")
    screen_dir = os.path.join(data_dir, "screen")
    
    import cv2
    from tqdm import tqdm
    import re
    
    print(f"Scanning for images in {real_dir} and {screen_dir}...")
    
    def extract_group(filepath, is_screen):
        basename = os.path.basename(filepath)
        if not is_screen:
            match = re.search(r'(?:DS-05-)(\d+)', basename)
            return match.group(1) if match else basename
        else:
            match = re.search(r'-(\d{3,4})\.\w+$', basename)
            return match.group(1) if match else basename

    def process_image(filepath, label, is_screen):
        img = cv2.imread(filepath)
        if img is not None:
            vec, _ = extract_features(img)
            grp = extract_group(filepath, is_screen)
            return vec, label, grp
        return None

    from joblib import Parallel, delayed

    real_files = glob.glob(os.path.join(real_dir, "*.*"))
    screen_files = glob.glob(os.path.join(screen_dir, "*.*"))
    
    print(f"Extracting features from {len(real_files)} real and {len(screen_files)} screen images in parallel (n_jobs=4 to save RAM)...")
    
    real_results = Parallel(n_jobs=4)(delayed(process_image)(f, 0, False) for f in tqdm(real_files, desc="Real Images"))
    screen_results = Parallel(n_jobs=4)(delayed(process_image)(f, 1, True) for f in tqdm(screen_files, desc="Screen Images"))
    
    all_results = [r for r in real_results + screen_results if r is not None]
    
    for vec, label, grp in all_results:
        X.append(vec)
        y.append(label)
        groups.append(grp)
            
    X_arr = np.array(X)
    y_arr = np.array(y)
    g_arr = np.array(groups)
    
    print("Saving features to cache...")
    np.save(cache_x, X_arr)
    np.save(cache_y, y_arr)
    np.save(cache_g, g_arr)
    
    return X_arr, y_arr, g_arr

def train_model(data_dir: str, phone_data_dir: str = None, mode: str = "default"):
    print("Starting training phase...")
    X, y, groups = gather_data(data_dir)
    
    if len(X) == 0:
        print("Error: No valid images found in dataset directories.")
        return
        
    print(f"Successfully extracted features from {len(X)} images.")
    
    if len(np.unique(y)) < 2:
        print("Error: Dataset must contain both real and screen images.")
        return

    from sklearn.model_selection import GroupShuffleSplit
    
    # --- Grouped Split (Leakage Free) ---
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups))
    X_tr_g, X_te_g, y_tr_g, y_te_g = X[train_idx], X[test_idx], y[train_idx], y[test_idx]
    from sklearn.calibration import CalibratedClassifierCV
    
    # Base robust Random Forest to compare
    ratio_g = float(np.sum(y_tr_g == 0)) / np.sum(y_tr_g == 1) if np.sum(y_tr_g == 1) > 0 else 1.0
    rf_base = xgb.XGBClassifier(n_estimators=100, max_depth=4, reg_lambda=10, random_state=42, scale_pos_weight=ratio_g, tree_method='hist', device='cuda')
    
    # Wrap in Logistic Calibration (Platt Scaling)
    rf_grouped = CalibratedClassifierCV(rf_base, method='sigmoid', cv=3)
    
    print("Training Calibrated XGBoost model on GPU (Leakage-Free)...")
    rf_grouped.fit(X_tr_g, y_tr_g)
    
    print("Evaluating leak-free model on test set...")
    y_pred = rf_grouped.predict(X_te_g)
    y_proba = rf_grouped.predict_proba(X_te_g)[:, 1]
    
    acc = accuracy_score(y_te_g, y_pred)
    prec = precision_score(y_te_g, y_pred, zero_division=0)
    rec = recall_score(y_te_g, y_pred, zero_division=0)
    f1 = f1_score(y_te_g, y_pred, zero_division=0)
    
    try:
        roc_auc = roc_auc_score(y_te_g, y_proba)
    except ValueError:
        roc_auc = 0.0

    cm = confusion_matrix(y_te_g, y_pred)

    print("------------------------------")
    print("Metrics on Grouped Held-out Test Set:")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC AUC:   {roc_auc:.4f}")
    print("Confusion Matrix:")
    print(cm)
    print("------------------------------")

    model_path = os.path.join(os.path.dirname(__file__), "model.joblib")
    joblib.dump(rf_grouped, model_path)
    print(f"Model saved to {model_path}.")

    # --- Phone Domain Calibration & Model Comparison ---
    threshold = 0.50
    calibration_status = "Uncalibrated"
    final_model = rf_grouped
    final_model_name = "XGBoost Classifier"
    
    if mode in ["hybrid-domain", "phone-adapted"] and phone_data_dir:
        print(f"Running phone-domain model comparison using {phone_data_dir}...")
        X_phone, y_phone, _ = gather_data(phone_data_dir)
        if len(X_phone) > 0:
            from sklearn.model_selection import StratifiedKFold
            skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            
            # Tracking metrics for the 4 models
            f1_icl_base = []
            f1_thresh_cal = []
            f1_phone_adapt = []
            f1_rule_boost = []
            
            f_names = get_feature_names()
            idx_bezel = f_names.index("bezel_score")
            idx_persp = f_names.index("perspective_score")
            idx_glare = f_names.index("glare_patch_size")

            best_threshold_overall = 0.50
            best_f1_overall = 0.0

            for train_idx_p, test_idx_p in skf.split(X_phone, y_phone):
                X_tr_p, y_tr_p = X_phone[train_idx_p], y_phone[train_idx_p]
                X_te_p, y_te_p = X_phone[test_idx_p], y_phone[test_idx_p]
                
                # 1. ICL Base Model
                probs_base = rf_grouped.predict_proba(X_te_p)[:, 1]
                preds_base = (probs_base >= 0.5).astype(int)
                f1_icl_base.append(f1_score(y_te_p, preds_base, zero_division=0))
                
                # 2. Threshold-Calibrated
                best_th = 0.5
                best_th_f1 = 0
                probs_tr_p = rf_grouped.predict_proba(X_tr_p)[:, 1]
                for th in np.arange(0.1, 0.9, 0.05):
                    f1 = f1_score(y_tr_p, (probs_tr_p >= th).astype(int), zero_division=0)
                    if f1 > best_th_f1:
                        best_th_f1 = f1
                        best_th = th
                
                preds_th = (probs_base >= best_th).astype(int)
                f1_thresh_cal.append(f1_score(y_te_p, preds_th, zero_division=0))
                
                # Update best overall threshold (averaging over folds)
                best_threshold_overall += best_th / 5.0
                
                # 3. Rule-Boosted Hybrid (Applied to Base probs)
                boosted_probs = probs_base.copy()
                for i in range(len(X_te_p)):
                    boost = 0.0
                    if X_te_p[i, idx_bezel] > 0.02: boost += 0.15
                    if X_te_p[i, idx_persp] > 0.2: boost += 0.15
                    if X_te_p[i, idx_glare] > 0.02: boost += 0.1
                    boosted_probs[i] = min(1.0, boosted_probs[i] + boost)
                
                preds_boost = (boosted_probs >= best_th).astype(int)
                f1_rule_boost.append(f1_score(y_te_p, preds_boost, zero_division=0))
                
                # 4. Phone-adapted Model (Train on ICL + Phone Train fold)
                X_comb = np.vstack([X_tr_g, X_tr_p])
                y_comb = np.concatenate([y_tr_g, y_tr_p])
                ratio_c = float(np.sum(y_comb == 0)) / np.sum(y_comb == 1) if np.sum(y_comb == 1) > 0 else 1.0
                rf_adapted_base = xgb.XGBClassifier(n_estimators=100, max_depth=4, reg_lambda=10, random_state=42, scale_pos_weight=ratio_c, tree_method='hist', device='cuda')
                rf_adapted = CalibratedClassifierCV(rf_adapted_base, method='sigmoid', cv=3)
                rf_adapted.fit(X_comb, y_comb)
                
                probs_adapt = rf_adapted.predict_proba(X_te_p)[:, 1]
                # Also find best threshold for adapted model on its own train set
                probs_adapt_tr = rf_adapted.predict_proba(X_tr_p)[:, 1]
                best_th_adapt = 0.5
                best_th_adapt_f1 = 0
                for th in np.arange(0.1, 0.9, 0.05):
                    f1 = f1_score(y_tr_p, (probs_adapt_tr >= th).astype(int), zero_division=0)
                    if f1 > best_th_adapt_f1:
                        best_th_adapt_f1 = f1
                        best_th_adapt = th
                
                preds_adapt = (probs_adapt >= best_th_adapt).astype(int)
                f1_phone_adapt.append(f1_score(y_te_p, preds_adapt, zero_division=0))

            mean_f1_base = np.mean(f1_icl_base)
            mean_f1_thresh = np.mean(f1_thresh_cal)
            mean_f1_boost = np.mean(f1_rule_boost)
            mean_f1_adapt = np.mean(f1_phone_adapt)

            print("\n=== Phone-Domain 5-Fold CV Model Comparison ===")
            print(f"1. ICL Base Model:                F1 = {mean_f1_base:.4f}")
            print(f"2. Threshold-Calibrated Model:    F1 = {mean_f1_thresh:.4f}")
            print(f"3. Phone-Adapted Model:           F1 = {mean_f1_adapt:.4f}")
            print(f"4. Rule-Boosted Hybrid Model:     F1 = {mean_f1_boost:.4f}")
            print("===============================================\n")

            reports_dir = ensure_reports_dir()
            comp_df = pd.DataFrame({
                "Model": ["ICL Base", "Threshold-Calibrated", "Phone-Adapted", "Rule-Boosted Hybrid"],
                "Phone_CV_F1_Score": [mean_f1_base, mean_f1_thresh, mean_f1_adapt, mean_f1_boost]
            })
            comp_df.to_csv(os.path.join(reports_dir, "model_comparison.csv"), index=False)
            
            with open(os.path.join(reports_dir, "model_selection.md"), "w") as f:
                f.write("# Model Selection Report\n\n")
                f.write("Based on 5-Fold Stratified CV on the phone dataset:\n")
                f.write(comp_df.to_markdown(index=False))

            # Select final model logic
            best_model_idx = np.argmax([mean_f1_base, mean_f1_thresh, mean_f1_adapt, mean_f1_boost])
            if best_model_idx == 2:
                # Retrain phone-adapted on FULL phone set + ICL
                print("Selected: Phone-Adapted Model. Training final model on all ICL + Phone data...")
                X_comb_final = np.vstack([X_tr_g, X_phone])
                y_comb_final = np.concatenate([y_tr_g, y_phone])
                ratio_c = float(np.sum(y_comb_final == 0)) / np.sum(y_comb_final == 1) if np.sum(y_comb_final == 1) > 0 else 1.0
                rf_final_base = xgb.XGBClassifier(n_estimators=100, max_depth=4, reg_lambda=10, random_state=42, scale_pos_weight=ratio_c, tree_method='hist', device='cuda')
                rf_final = CalibratedClassifierCV(rf_final_base, method='sigmoid', cv=3)
                rf_final.fit(X_comb_final, y_comb_final)
                
                # Get best threshold for full phone set
                probs_final = rf_final.predict_proba(X_phone)[:, 1]
                best_th_final = 0.5
                best_th_f1_final = 0
                for th in np.arange(0.1, 0.9, 0.05):
                    f1 = f1_score(y_phone, (probs_final >= th).astype(int), zero_division=0)
                    if f1 > best_th_f1_final:
                        best_th_f1_final = f1
                        best_th_final = th
                        
                final_model = rf_final
                threshold = best_th_final
                calibration_status = "Phone-Adapted (Full Dataset)"
                final_model_name = "Phone-Adapted XGBoost"
                
            elif best_model_idx in [1, 3]:
                print("Selected: Threshold-Calibrated or Rule-Boosted. Using ICL Base with shifted threshold.")
                threshold = best_threshold_overall
                calibration_status = "Phone Domain Calibrated + Boosts (5-Fold CV)"
            else:
                print("Selected: ICL Base. (Unlikely, but fallback).")
                threshold = 0.50
                calibration_status = "Uncalibrated Base"

            joblib.dump(final_model, model_path)
            print(f"Final model saved. Threshold set to: {threshold:.2f}")

    # Update metadata
    meta_path = os.path.join(os.path.dirname(__file__), "model_metadata.json")
    meta = {
        "model_type": final_model_name,
        "threshold": threshold,
        "calibration_status": calibration_status,
        "icl_metrics": {
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "f1_score": float(f1),
            "roc_auc": float(roc_auc)
        },
        "feature_count": len(get_feature_names()),
        "feature_names": get_feature_names()
    }
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=4)
    print("Updated model_metadata.json.")

    # Save Feature Importance Report if available
    reports_dir = ensure_reports_dir()
    importances = None
    if hasattr(final_model, 'feature_importances_'):
        importances = final_model.feature_importances_
    elif hasattr(final_model, 'estimator') and hasattr(final_model.estimator, 'feature_importances_'):
        importances = final_model.estimator.feature_importances_
    
    if importances is not None:
        fi_df = pd.DataFrame({
            "Feature": get_feature_names(),
            "Importance": importances
        }).sort_values(by="Importance", ascending=False)
        fi_df.to_csv(os.path.join(reports_dir, "feature_importance.csv"), index=False)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Fraud Detection Model")
    parser.add_argument("--data", type=str, default="dataset", help="Directory containing real/ and screen/ subfolders")
    parser.add_argument("--phone-data", type=str, default=None, help="Directory containing phone images")
    parser.add_argument("--mode", type=str, default="default", help="Training mode (e.g. hybrid-domain)")
    args = parser.parse_args()
    
    train_model(args.data, args.phone_data, args.mode)
