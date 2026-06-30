# Context for ChatGPT

## Assignment Details

This is the "SalesCode Spot the Fake Photo" ML assignment. We classify images as real (0) or screen (1) using a fast, cheap model.

## What has already been done

- Project frontend, backend, and docs are fully completed and verified working.
- **Documentation Update**: README polished with verified examples, screenshot section fixed, metric chart fallback added, methodology and phone-deployability explanation improved. No model logic changed.
- **Documentation Update**: Added author name (Kartikeya) and prominent, highly readable Accuracy Highlights to the top of the README.
- **Hugging Face Deployment:** Project is fully containerized with a multi-stage Dockerfile. FastAPI serves the built React frontend on port 7860.
- **The frontend UI** is a professional 12-column SOC (Security Operations Center) dashboard using React, Vite, Tailwind CSS v4, Framer Motion. Build passes (`npm run build` ✓).
- **Current model status:** Fully trained using a **Hybrid-Domain Calibration Pipeline** on the 8GB ICL dataset. Phone-Adapted XGBoost (21 features). Threshold: **0.65**.
- **Dataset Label Definitions**:
  - `real (0)`: Direct camera capture of a physical scene/object.
  - `screen (1)`: Recaptured/second-capture image. May not have a visible bezel. May show color shift, blur, moiré, pixel noise, or compression artifacts.
- **User Phone Dataset Path:** `dataset/my_photos/real` and `dataset/my_photos/screen`.

## Current Metrics

| Metric | Value | Method |
|--------|-------|--------|
| ICL Accuracy | ~98.9% | GroupShuffleSplit (leakage-free) |
| ICL F1 | ~99.2% | GroupShuffleSplit |
| Phone CV F1 (honest) | **~79.5%** | 5-Fold Stratified CV |
| Phone Calibration Score | 100% | Same 53 images used for threshold selection — calibration only, NOT independent |
| Threshold | **0.65** | Manually selected |

## Risk Band Definitions (frontend + backend)

- **0.00–0.35**: Likely Real
- **0.35–0.65**: Borderline / Needs Review
- **0.65–1.00**: Likely Recaptured/Screen

Prediction logic: `final_score >= 0.65` → screen, else → real.

## Scoring Formula

```
final_score = clamp(raw_model_score + rule_boost_total, 0, 1)
```

* **Fraud Score Range**: `[0.0, 1.0]`. 
* **Prediction Labels**: `0 = real photo`, `1 = recapture/screen`
* **Threshold**: We consider `> 0.65` as Recapture (Screen). Below `0.35` is safe, and `0.35` to `0.65` is a grey area.

## Tech Stack
* **Model**: XGBoost (Phone-Adapted)
* **Features**: 21 handcrafted CV/Frequency features
* **Backend**: FastAPI
* **Frontend**: React, Vite, Tailwind CSS v4, Framer Motion, Recharts

## UI/UX
* **Theme**: Dark, forensic, Security Operations Center (SOC) style with subtle ambient starfield/galaxy/scanline `ForensicBackground`.
* **Layout**: 12-column responsive grid with glassmorphic cards (increased background opacity and blur for depth).
* **Visuals**: Animated authentic terminal logs, node-based workflow tracking, compact HTML/CSS feature metric rows, and a dynamic circular fraud gauge.

## Current Focus
* Maintaining the premium frontend experience while ensuring the underlying API and XGBoost model logic remains untouched.
* The frontend implements a "UI Telemetry Correction Pass" which distinguishes raw feature values from risk interpretations (e.g. downgrading high CV feature alerts if the model scores the image as real, labeling them "Contextual / Organic"). No model logic or `predict.py` behavior has been changed.

## Phone-Adapted CV Strategy & Feature Audit

Because of constraints (no deep learning), we relied on OpenCV CV features. To fix false positives on real textures:

1. **Deep Feature Audit Toolkit**: `scripts/audit_features.py` and `scripts/feature_ablation.py` revealed naive `fft_hf_ratio` and `moire_score` fired on natural flower/texture edges.
2. **Contextual Feature Refinement**: `features.py` now requires structural context:
    - **Contextual Moiré:** Flatness penalty prevents triggering on dense organic scenes.
    - **Contextual Bezel & Glare:** Require screen-like rectangular contour (`rect_contour_score`).
    - **Downweighted Global FFT:** 0.1 → 0.01, forces reliance on local blockiness.
3. **Model Training**: Phone-Adapted XGBoost on mixed ICL + Phone data.
4. **Conservative Rule Boosts**: Multi-cue only, capped at 0.15 total.
5. **Scoring Integrity**: `--no-rules` flag, transparent raw/boost/final in all outputs.

## Fresh Unseen Sanity Test Results (manual_test/unknown/)

- 10 images tested (5 real, 4 screen + 2 borderline)
- 5/5 real images correctly predicted (avg score: 0.145)
- 3/4 clearly-screened images correctly predicted (avg score: 0.720)
- 2 false negatives: a borderline flower photo (0.41) and a synthetically generated laptop image (0.29 — no real recapture artifacts)
- 0 false positives

## CLI Verification

- `python predict.py image.jpg` → single float (e.g., `0.4870`) ✓
- `python predict.py image.jpg --json` → full JSON with raw_model_score, rule_boost_total, final_score, threshold, predicted_label, model_type ✓
- `python predict.py image.jpg --json --no-rules` → rule layer bypassed ✓
- CLI score == Backend API score for same image ✓

## Current Repo Structure

```text
<project-root>/
  - backend/
    - app.py
  - frontend/
    - package.json
    - index.html
    - vite.config.js
    - src/
      - main.jsx
      - App.jsx
      - index.css
      - components/
        - FraudGauge.jsx
        - FeatureBarChart.jsx
        - TerminalLogs.jsx
        - WorkflowAnimation.jsx
    - public/
      - sample_photos/
        - real/ (6 samples)
        - screen/ (6 samples)
        - manifest.json
  - dataset/
    - real/
    - screen/
    - my_photos/
      - real/ (25 images)
      - screen/ (28 images)
  - reports/
    - phone_test_results.csv
    - phone_metrics.json
    - phone_test_summary.md
    - sanity_predictions.csv
    - sanity_summary.md
  - scripts/
    - evaluate_phone_images.py
    - sanity_test_predictions.py
    - prepare_icl_dataset.py
    - validate_dataset.py
    - audit_features.py
    - feature_ablation.py
  - manual_test/
    - unknown/
      - real/
      - screen/
  - APPROACH.md
  - DATASET_SOURCES.md
  - RUNBOOK.md
  - PROJECT_STATE.md
  - knowledge.md
  - changes.md
  - forchatgpt.md
  - predict.py
  - features.py
  - train.py
  - model.joblib
  - model_metadata.json
  - requirements.txt
  - submission/
    - SalesCode_Recapture_Detector.zip
```

## Important Commands

- Run Prediction: `python predict.py <image_path>`
- Run Prediction (JSON): `python predict.py <image_path> --json`
- Run Backend: `uvicorn backend.app:app --host 127.0.0.1 --port 8000`
- Run Frontend Dev: `cd frontend && npm run dev`
- Evaluate Phone Images: `python scripts/evaluate_phone_images.py`
- Sanity Test: `python scripts/sanity_test_predictions.py --input manual_test/unknown`
- Compile Check: `python -m py_compile predict.py train.py features.py backend/app.py`
- Frontend Build: `cd frontend && npm run build`

## Current Risks/Limitations

The pipeline is highly functional. The phone validation set has only 53 images. While `evaluate_phone_images.py` yields 100% accuracy on this set, this is a **calibration/training-set score** because these exact images were used to select the 0.65 threshold. The honest 5-Fold Stratified CV generalization score is ~79.5% F1. No production accuracy claim is made.

## Final Status

- **Frontend build:** PASS ✓
- **Backend py_compile:** PASS ✓
- **CLI normal mode:** Single float output ✓
- **CLI JSON mode:** Full breakdown ✓
- **CLI vs Backend score match:** EXACT ✓
- **Submission ZIP:** `submission/SalesCode_Recapture_Detector.zip` ✓
