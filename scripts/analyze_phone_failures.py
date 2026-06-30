import os
import sys
import cv2
import pandas as pd
import numpy as np
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from features import extract_features

def main():
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    csv_path = os.path.join(reports_dir, 'phone_test_results.csv')
    
    if not os.path.exists(csv_path):
        print("Test results CSV not found.")
        sys.exit(1)
        
    df = pd.read_csv(csv_path)
    failures = df[df['correct'] == False].copy()
    
    if failures.empty:
        print("No failures found! Perfect score.")
        sys.exit(0)
        
    print(f"Analyzing {len(failures)} failures...")
    
    analysis_results = []
    
    for _, row in failures.iterrows():
        filepath = row['filepath']
        true_label = row['true_label']
        predicted_score = row['predicted_score']
        
        # Reconstruct path
        subfolder = 'real' if true_label == 0 else 'screen'
        full_path = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'my_photos', subfolder, filepath)
        
        if not os.path.exists(full_path):
            print(f"File not found: {full_path}")
            continue
            
        img = cv2.imread(full_path)
        if img is None:
            continue
            
        h, w = img.shape[:2]
        is_whatsapp = "WhatsApp" in filepath or "WA" in filepath
        
        _, group_dict = extract_features(img)
        
        # Flatten features dict
        flat_feats = {}
        for feat_name, feat_val in group_dict.items():
            flat_feats[feat_name] = feat_val
                
        analysis_results.append({
            "filepath": filepath,
            "true_label": true_label,
            "predicted_score": predicted_score,
            "failure_type": "False Positive" if true_label == 0 else "False Negative",
            "is_whatsapp": is_whatsapp,
            "resolution": f"{w}x{h}",
            **flat_feats
        })
        
    analysis_df = pd.DataFrame(analysis_results)
    
    out_csv = os.path.join(reports_dir, 'phone_failure_analysis.csv')
    analysis_df.to_csv(out_csv, index=False)
    
    # Write MD summary
    out_md = os.path.join(reports_dir, 'phone_failure_summary.md')
    with open(out_md, 'w') as f:
        f.write("# Phone Failure Analysis\n\n")
        f.write(f"**Total Failures:** {len(failures)}\n")
        f.write(f"- False Positives (Real flagged as Screen): {len(failures[failures['true_label'] == 0])}\n")
        f.write(f"- False Negatives (Screen flagged as Real): {len(failures[failures['true_label'] == 1])}\n\n")
        
        f.write("## Insights\n")
        wa_count = analysis_df['is_whatsapp'].sum()
        f.write(f"- **WhatsApp Compression:** {wa_count} out of {len(failures)} failed images were heavily compressed via WhatsApp.\n")
        
        avg_res = analysis_df['resolution'].value_counts().idxmax()
        f.write(f"- **Most Common Resolution of failures:** {avg_res}\n\n")
        
        f.write("### Average Feature Values for False Positives\n")
        fp_df = analysis_df[analysis_df['true_label'] == 0]
        if not fp_df.empty:
            f.write("False positives (real images) are likely triggering on these features (high values typically indicate a screen):\n")
            f.write(f"- `fft_hf_ratio`: {fp_df['fft_hf_ratio'].mean():.4f}\n")
            f.write(f"- `laplacian_var`: {fp_df['laplacian_var'].mean():.4f}\n")
            f.write(f"- `edge_density`: {fp_df['edge_density'].mean():.4f}\n")
            f.write(f"- `banding_score`: {fp_df['banding_score'].mean():.4f}\n")
            
        f.write("\n### Conclusion\n")
        f.write("The current features are heavily sensitive to high-frequency noise introduced by lossy JPEG compression. Before feature extraction, images must be resized/normalized and optionally smoothed to strip out compression blockiness while retaining true physical screen Moiré.\n")
        
    print(f"Saved analysis to {out_csv} and {out_md}")

if __name__ == "__main__":
    main()
