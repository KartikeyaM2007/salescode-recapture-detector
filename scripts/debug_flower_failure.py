import os
import sys
import json
import pandas as pd
import cv2

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from predict import run_prediction

def debug_flowers():
    test_cases = [
        "manual_test/failure_cases/real/real 1.jpeg",
        "manual_test/failure_cases/real/real 2.jpeg",
        "manual_test/failure_cases/screen/fake 1.jpeg",
        "manual_test/failure_cases/screen/fake 2.jpeg"
    ]
    
    results = []
    
    for case in test_cases:
        path = os.path.join(os.path.dirname(__file__), '..', case)
        if not os.path.exists(path):
            print(f"Skipping {path} - not found.")
            continue
            
        img = cv2.imread(path)
        if img is None:
            continue
            
        res = run_prediction(img, no_rules=False)
        
        row = {
            'image': os.path.basename(case),
            'true_label': 'real' if 'real' in case else 'screen',
            'raw_score': res['raw_model_score'],
            'rule_boost': res['rule_boost_total'],
            'final_score': res['final_score'],
            'predicted_label': res['predicted_label'],
            'boosts': json.dumps(res.get('individual_rule_boosts', {})),
        }
        
        for k, v in res.get('features', {}).items():
            row[k] = v
            
        results.append(row)
        
    if not results:
        print("No test cases found.")
        return
        
    df = pd.DataFrame(results)
    
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'reports'), exist_ok=True)
    df.to_csv(os.path.join(os.path.dirname(__file__), '..', 'reports', 'flower_failure_debug.csv'), index=False)
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'reports', 'flower_failure_summary.md'), 'w') as f:
        f.write("# Flower Failure Debug Summary\n\n")
        
        summary_cols = ['image', 'true_label', 'raw_score', 'rule_boost', 'final_score', 'boosts']
        f.write("## Prediction Summary\n")
        f.write(df[summary_cols].to_markdown(index=False))
        f.write("\n\n")
        
        f.write("## Feature Values\n")
        feature_cols = [c for c in df.columns if c not in summary_cols and c != 'predicted_label']
        # Transpose for easier reading
        feature_df = df[['image'] + feature_cols].set_index('image').T
        f.write(feature_df.to_markdown())
        f.write("\n")

if __name__ == "__main__":
    debug_flowers()
