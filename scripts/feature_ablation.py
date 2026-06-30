import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from train import gather_data
from features import get_feature_names

def run_ablation():
    feature_groups = {
        'brightness_color': ['brightness', 'contrast', 'saturation'],
        'blur_sharpness': ['laplacian_var', 'sobel_mean', 'edge_density'],
        'fft_global_freq': ['fft_hf_ratio', 'h_freq_peak', 'v_freq_peak', 'diag_freq_peak'],
        'local_patch_fft': ['local_fft_hf'],
        'moire_banding': ['moire_score', 'banding_score'],
        'jpeg_compression': ['compression_diff', 'blockiness'],
        'bezel_border': ['bezel_score', 'rect_contour_score'],
        'perspective_rect': ['perspective_score'],
        'glare_overexposure': ['glare_ratio', 'glare_patch_size'],
        'printout_paper': ['paper_texture']
    }
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'dataset')
    phone_dir = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'my_photos')
    
    print("Loading datasets...")
    X_tr_g, y_tr_g, _ = gather_data(data_dir)
    X_phone, y_phone, _ = gather_data(phone_dir)
    
    f_names = get_feature_names()
    
    results = []
    
    def eval_model(X_train, y_train, X_test, y_test, disabled_indices=[]):
        X_train_sub = np.delete(X_train, disabled_indices, axis=1)
        X_test_sub = np.delete(X_test, disabled_indices, axis=1)
        
        ratio = float(np.sum(y_train == 0)) / np.sum(y_train == 1) if np.sum(y_train == 1) > 0 else 1.0
        base = xgb.XGBClassifier(n_estimators=100, max_depth=4, reg_lambda=10, random_state=42, scale_pos_weight=ratio, tree_method='hist', device='cpu')
        model = CalibratedClassifierCV(base, method='sigmoid', cv=3)
        model.fit(X_train_sub, y_train)
        
        probs = model.predict_proba(X_test_sub)[:, 1]
        
        best_th, best_f1 = 0.5, 0
        for th in np.arange(0.1, 0.9, 0.05):
            f1 = f1_score(y_test, (probs >= th).astype(int), zero_division=0)
            if f1 > best_f1:
                best_f1, best_th = f1, th
                
        preds = (probs >= best_th).astype(int)
        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        
        fp = np.sum((preds == 1) & (y_test == 0))
        fn = np.sum((preds == 0) & (y_test == 1))
        
        return acc, prec, rec, best_f1, fp, fn
        
    def cv_eval(disabled_indices):
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        metrics = []
        for tr_idx, te_idx in skf.split(X_phone, y_phone):
            X_comb = np.vstack([X_tr_g, X_phone[tr_idx]])
            y_comb = np.concatenate([y_tr_g, y_phone[tr_idx]])
            
            acc, prec, rec, f1, fp, fn = eval_model(X_comb, y_comb, X_phone[te_idx], y_phone[te_idx], disabled_indices)
            metrics.append([acc, prec, rec, f1, fp, fn])
        
        return np.mean(metrics, axis=0)
        
    print("Evaluating Baseline...")
    base_metrics = cv_eval([])
    results.append({
        'Ablated Group': 'None (Baseline)',
        'Accuracy': base_metrics[0],
        'Precision': base_metrics[1],
        'Recall': base_metrics[2],
        'F1': base_metrics[3],
        'False Positives': base_metrics[4] * 5, 
        'False Negatives': base_metrics[5] * 5
    })
    
    for group, features in feature_groups.items():
        print(f"Evaluating without {group}...")
        indices = [f_names.index(f) for f in features if f in f_names]
        metrics = cv_eval(indices)
        results.append({
            'Ablated Group': group,
            'Accuracy': metrics[0],
            'Precision': metrics[1],
            'Recall': metrics[2],
            'F1': metrics[3],
            'False Positives': metrics[4] * 5,
            'False Negatives': metrics[5] * 5
        })
        
    df = pd.DataFrame(results)
    
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'reports'), exist_ok=True)
    df.to_csv(os.path.join(os.path.dirname(__file__), '..', 'reports', 'feature_ablation.csv'), index=False)
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'reports', 'feature_ablation_summary.md'), 'w') as f:
        f.write("# Feature Ablation Summary\n\n")
        f.write(df.to_markdown(index=False))
        f.write("\n")

if __name__ == "__main__":
    run_ablation()
