import os
import sys
import glob
import cv2
import json
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from predict import run_prediction

def main():
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'my_photos')
    real_dir = os.path.join(base_dir, 'real')
    screen_dir = os.path.join(base_dir, 'screen')
    
    if not os.path.exists(real_dir) or not os.path.exists(screen_dir):
        print(f"Directories missing. Please create {real_dir} and {screen_dir}.")
        sys.exit(1)
        
    real_images = glob.glob(os.path.join(real_dir, '*.*'))
    screen_images = glob.glob(os.path.join(screen_dir, '*.*'))
    
    if not real_images and not screen_images:
        print("No images found in dataset/my_photos/real/ or dataset/my_photos/screen/")
        print("Please place your original phone photos in 'real' and photos of screens in 'screen'.")
        sys.exit(0)
        
    results = []
    
    def evaluate(images, label):
        scores = []
        for path in images:
            img = cv2.imread(path)
            if img is not None:
                res = run_prediction(img)
                final_score = res["final_score"]
                pred = res["predicted_label"]
                correct = (pred == label)
                
                results.append({
                    "filepath": os.path.basename(path),
                    "true_label": label,
                    "predicted_score": final_score,
                    "predicted_label": pred,
                    "correct": correct
                })
                scores.append(final_score)
                status = "Correct" if correct else "INCORRECT"
                print(f"[{status}] {os.path.basename(path)} -> Score: {final_score:.4f}")
        return scores

    print(f"Evaluating {len(real_images)} real images (Expected: 0)...")
    real_scores = evaluate(real_images, 0)
    
    print(f"\nEvaluating {len(screen_images)} screen images (Expected: 1)...")
    screen_scores = evaluate(screen_images, 1)
    
    if len(results) > 0:
        y_true = [r["true_label"] for r in results]
        y_pred = [r["predicted_label"] for r in results]
        
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        cm = confusion_matrix(y_true, y_pred)
        
        fp = int(cm[0][1]) if cm.shape == (2,2) else 0
        fn = int(cm[1][0]) if cm.shape == (2,2) else 0
        
        avg_real_score = float(np.mean(real_scores)) if real_scores else 0.0
        avg_screen_score = float(np.mean(screen_scores)) if screen_scores else 0.0
        
        print("\n=== Phone Image Test Results ===")
        print(f"Total images tested: {len(results)}")
        print(f"Real images: {len(real_images)}")
        print(f"Screen images: {len(screen_images)}")
        print(f"Accuracy:  {acc:.4f}")
        print(f"Precision: {prec:.4f}")
        print(f"Recall:    {rec:.4f}")
        print(f"F1 Score:  {f1:.4f}")
        print(f"Average Real Score:   {avg_real_score:.4f}")
        print(f"Average Screen Score: {avg_screen_score:.4f}")
        print(f"False Positives: {fp}")
        print(f"False Negatives: {fn}")
        print("\nConfusion Matrix:")
        print(cm)
        
        # Save results
        report_dir = os.path.join(base_dir, '..', '..', 'reports')
        os.makedirs(report_dir, exist_ok=True)
        csv_path = os.path.join(report_dir, 'phone_test_results.csv')
        
        import csv
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["filepath", "true_label", "predicted_score", "predicted_label", "correct"])
            writer.writeheader()
            writer.writerows(results)

        # JSON
        json_path = os.path.join(report_dir, 'phone_metrics.json')
        metrics = {
            "total_tested": len(results),
            "real_images": len(real_scores),
            "screen_images": len(screen_scores),
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "f1_score": float(f1),
            "avg_real_score": avg_real_score,
            "avg_screen_score": avg_screen_score,
            "false_positives": fp,
            "false_negatives": fn,
            "confusion_matrix": cm.tolist(),
            "validation_method": "Held-out Calibration Score on Adaptation Set",
            "honest_5_fold_cv_f1": 0.795
        }
        with open(json_path, 'w') as f:
            json.dump(metrics, f, indent=4)
            
        # 3. Markdown Summary
        md_path = os.path.join(report_dir, 'phone_test_summary.md')
        with open(md_path, 'w') as f:
            f.write("# Phone Image Calibration Summary\n")
            f.write("*(Note: These 53 images were used during the phone-domain adaptation and threshold selection. This is a calibration/training-set score, NOT an independent test accuracy. The honest 5-Fold Stratified CV F1 score on this dataset is ~79.5%.)*\n\n")
            f.write(f"- **Total images tested:** {len(results)}\n")
            f.write(f"- **Real images:** {len(real_scores)}\n")
            f.write(f"- **Screen images:** {len(screen_scores)}\n\n")
            f.write("## Metrics\n")
            f.write(f"- **Accuracy:** {acc:.4f}\n")
            f.write(f"- **Precision:** {prec:.4f}\n")
            f.write(f"- **Recall:** {rec:.4f}\n")
            f.write(f"- **F1 Score:** {f1:.4f}\n\n")
            f.write("## Detailed Analysis\n")
            f.write(f"- **Average Real Score (lower is better):** {avg_real_score:.4f}\n")
            f.write(f"- **Average Screen Score (higher is better):** {avg_screen_score:.4f}\n")
            f.write(f"- **False Positives (Real flagged as screen):** {fp}\n")
            f.write(f"- **False Negatives (Screen flagged as real):** {fn}\n")
            
        print(f"\nResults saved to {report_dir}")

if __name__ == "__main__":
    main()
