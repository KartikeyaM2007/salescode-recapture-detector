import os
import cv2
import glob
import pandas as pd
import numpy as np
import sys

# Ensure parent directory is in path to import features
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from features import extract_features

def audit_features():
    groups = {
        'dataset_real': 'dataset/my_photos/real/*',
        'dataset_screen': 'dataset/my_photos/screen/*',
        'failure_real': 'manual_test/failure_cases/real/*',
        'failure_screen': 'manual_test/failure_cases/screen/*',
    }

    results = []

    for group_name, path_pattern in groups.items():
        base_path = os.path.join(os.path.dirname(__file__), '..', path_pattern)
        for filepath in glob.glob(base_path):
            if not os.path.isfile(filepath):
                continue
            
            img = cv2.imread(filepath)
            if img is None:
                continue
            
            _, features_dict = extract_features(img)
            features_dict['image'] = os.path.basename(filepath)
            features_dict['group'] = group_name
            
            # Simple ground truth 0 or 1
            if 'real' in group_name:
                features_dict['label'] = 0
            else:
                features_dict['label'] = 1
                
            results.append(features_dict)

    if not results:
        print("No images found to audit.")
        return

    df = pd.DataFrame(results)
    
    # Save raw audit
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'reports'), exist_ok=True)
    df.to_csv(os.path.join(os.path.dirname(__file__), '..', 'reports', 'feature_audit.csv'), index=False)

    # Group stats
    feature_cols = [c for c in df.columns if c not in ['image', 'group', 'label']]
    
    stats = []
    for f in feature_cols:
        real_vals = df[df['label'] == 0][f]
        screen_vals = df[df['label'] == 1][f]
        
        real_mean = real_vals.mean()
        screen_mean = screen_vals.mean()
        
        stats.append({
            'feature': f,
            'real_mean': real_mean,
            'real_std': real_vals.std(),
            'screen_mean': screen_mean,
            'screen_std': screen_vals.std(),
            'diff': screen_mean - real_mean,
            'abs_diff': abs(screen_mean - real_mean)
        })

    stats_df = pd.DataFrame(stats)
    stats_df = stats_df.sort_values('abs_diff', ascending=False)
    stats_df.to_csv(os.path.join(os.path.dirname(__file__), '..', 'reports', 'feature_group_stats.csv'), index=False)
    
    # Generate summary markdown
    with open(os.path.join(os.path.dirname(__file__), '..', 'reports', 'feature_audit_summary.md'), 'w') as f:
        f.write("# Feature Audit Summary\n\n")
        f.write("## Top Separating Features (High Abs Diff)\n")
        f.write(stats_df.head(10).to_markdown(index=False))
        f.write("\n\n")
        
        f.write("## Suspicious Features (Real > Screen)\n")
        suspicious = stats_df[stats_df['diff'] < 0]
        f.write(suspicious.to_markdown(index=False))
        f.write("\n")

if __name__ == "__main__":
    audit_features()
