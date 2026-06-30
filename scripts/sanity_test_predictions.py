import os
import sys
import glob
import pandas as pd
import cv2
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from predict import run_prediction

def sanity_test():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='manual_test', help='Input directory')
    args = parser.parse_args()
    
    base_dir = os.path.abspath(args.input)
    
    results = []
    
    for root, dirs, files in os.walk(base_dir):
        if 'failure_cases' in root and 'unknown' not in base_dir:
            continue
            
        for file in files:
            if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
                
            path = os.path.join(root, file)
            true_label = 'real' if 'real' in root.split(os.sep) else 'screen'
            category = os.path.basename(root)
            
            img = cv2.imread(path)
            if img is None:
                continue
                
            res = run_prediction(img)
            
            is_correct = (res['predicted_label'] == 0 and true_label == 'real') or (res['predicted_label'] == 1 and true_label == 'screen')
            
            top_boost = ''
            if res.get('individual_rule_boosts'):
                top_boost = max(res['individual_rule_boosts'].items(), key=lambda x: x[1])[0]
                
            results.append({
                'filepath': os.path.relpath(path, start=os.path.join(os.path.dirname(__file__), '..')),
                'category': category,
                'true_label': true_label,
                'raw_model_score': res['raw_model_score'],
                'rule_boost_total': res['rule_boost_total'],
                'final_score': res['final_score'],
                'threshold': res['threshold'],
                'predicted_label': res['predicted_label'],
                'correct': is_correct,
                'top_boost_reason': top_boost
            })
            
    if not results:
        print("No test images found.")
        return
        
    df = pd.DataFrame(results)
    
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'reports'), exist_ok=True)
    df.to_csv(os.path.join(os.path.dirname(__file__), '..', 'reports', 'sanity_predictions.csv'), index=False)
    
    count_total = len(df)
    count_pred_real = len(df[df['predicted_label'] == 0])
    count_pred_screen = len(df[df['predicted_label'] == 1])
    count_borderline = len(df[(df['final_score'] >= 0.35) & (df['final_score'] < 0.65)])
    
    avg_real = df[df['true_label'] == 'real']['final_score'].mean() if len(df[df['true_label'] == 'real']) > 0 else 0
    avg_screen = df[df['true_label'] == 'screen']['final_score'].mean() if len(df[df['true_label'] == 'screen']) > 0 else 0
    
    fp = len(df[(df['true_label'] == 'real') & (df['predicted_label'] == 1)])
    fn = len(df[(df['true_label'] == 'screen') & (df['predicted_label'] == 0)])
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'reports', 'sanity_summary.md'), 'w') as f:
        f.write("# Fresh Unseen Sanity Test Summary\n\n")
        f.write(f"- **Count of images tested:** {count_total}\n")
        f.write(f"- **Number predicted real:** {count_pred_real}\n")
        f.write(f"- **Number predicted screen:** {count_pred_screen}\n")
        f.write(f"- **Number in borderline zone (0.35-0.65):** {count_borderline}\n")
        f.write(f"- **Average real score:** {avg_real:.4f}\n")
        f.write(f"- **Average screen score:** {avg_screen:.4f}\n")
        f.write(f"- **False positives (real predicted as screen):** {fp}\n")
        f.write(f"- **False negatives (screen predicted as real):** {fn}\n\n")
        
        f.write("## Individual Results\n")
        f.write(df[['filepath', 'true_label', 'final_score', 'predicted_label', 'correct']].to_markdown(index=False))
        f.write("\n")

if __name__ == "__main__":
    sanity_test()
