# Project Runbook

## Setup
Ensure you have Python 3.8+ installed.
```bash
pip install -r requirements.txt
```

## Prepare Dataset
```bash
python scripts/prepare_icl_dataset.py --mode sample   # small sample
python scripts/prepare_icl_dataset.py --mode full-icl  # full dataset
```

## Validate Dataset
```bash
python scripts/validate_dataset.py
```

## Train the Model (Phone-Adapted Strategy)
```bash
python train.py --data dataset --phone-data dataset/my_photos --mode phone-adapted
```
*Evaluates 4 strategies (ICL Base, Threshold-Calibrated, Phone-Adapted, Rule-Boosted Hybrid) using 5-Fold Stratified Cross-Validation on phone images and saves the best model.*

## Run Prediction (CLI)
```bash
# Normal mode — single float output
python predict.py path/to/image.jpg

# JSON mode — full breakdown
python predict.py path/to/image.jpg --json

# No-rules mode — bypass rule layer
python predict.py path/to/image.jpg --json --no-rules
```

## Evaluate on Phone Images (Calibration)
```bash
python scripts/evaluate_phone_images.py
```
> **Note:** This yields 100% accuracy on the 53-image calibration set (the same images used for threshold selection). This is NOT an independent test. The honest 5-Fold CV F1 is ~79.5%.

## Run Fresh Unseen Sanity Test
```bash
python scripts/sanity_test_predictions.py --input manual_test/unknown
# Results saved to reports/sanity_predictions.csv and reports/sanity_summary.md
```

## Run Backend API
```bash
uvicorn backend.app:app --host 127.0.0.1 --port 8000
```
- `/health` — model status, metadata, phone metrics
- `/predict` — POST multipart image, returns full JSON breakdown

## Run Frontend Dashboard
```bash
cd frontend
npm run dev
# Access at http://localhost:5173
```

## Build Frontend (Production)
```bash
cd frontend
npm run build
```

## Compile Check (All Python files)
```bash
python -m py_compile predict.py train.py features.py scripts/evaluate_phone_images.py scripts/prepare_icl_dataset.py scripts/validate_dataset.py backend/app.py
```

## Risk Bands
- **0.00–0.35**: Likely Real
- **0.35–0.65**: Borderline / Needs Review
- **0.65–1.00**: Likely Recaptured/Screen
- **Decision threshold:** 0.65

## Submission ZIP
```
submission/SalesCode_Recapture_Detector.zip
```
Contains: predict.py, features.py, model.joblib, model_metadata.json, requirements.txt, APPROACH.md, README.md, DATASET_SOURCES.md, train.py, scripts/, reports/
