import json
import subprocess
import os
import joblib

def test_contract():
    print("Testing Prediction Contract...")
    
    # 1. Test model class direction
    model_path = "model.joblib"
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        classes = list(model.classes_)
        assert classes == [0, 1] or classes == ['0', '1'], f"Expected [0, 1], got {classes}"
        print("[PASS] Class order is correct (class 1 is screen).")
    
    # 2. Test predict.py output via CLI JSON
    # Use any valid image for the test
    image_to_test = "frontend/public/sample_photos/real/real_001.jpg"
    cmd = ["python", "predict.py", image_to_test, "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, "CLI prediction failed."
    
    # Parse the last line as JSON (in case logs were printed before)
    output = result.stdout.strip().split('\n')[-1]
    data = json.loads(output)
    
    # Extract fields
    raw = data["raw_model_score"]
    boost = data["rule_boost_total"]
    final = data["final_score"]
    threshold = data["threshold"]
    label = data["predicted_label"]
    
    print(f"CLI JSON Output: raw={raw}, boost={boost}, final={final}")
    
    # 3. Contract checks
    assert 0 <= final <= 1.0, f"Final score out of bounds: {final}"
    if final >= threshold:
        assert label == 1, "Label should be 1 if final >= threshold"
    else:
        assert label == 0, "Label should be 0 if final < threshold"
        
    if raw == 0 and boost == 0:
        assert final != 1.0, "If raw=0 and boost=0, final cannot be 1.0"
        
    print("[PASS] CLI JSON contract passed.")
    
    # 4. Check backend consistency
    # We can test by importing app.py directly or checking the structure
    # Here we just check that the CLI outputs the exact same fields as expected by the backend
    expected_fields = ["raw_model_score", "rule_boost_total", "final_score", "threshold", "predicted_label"]
    for field in expected_fields:
        assert field in data, f"Missing field in JSON output: {field}"
        
    print("[PASS] Backend field consistency passed.")
    print("All prediction contracts passed successfully.")

if __name__ == "__main__":
    test_contract()
