# Project State

## Current Phase: UI Polish Pass Complete (Pending Final Handoff)

## Recent Accomplishments
1. Refactored the frontend React application into a premium, animated SOC/forensic-style dashboard.
2. Implemented complex staggered animations in the Recharts feature chart and typewriter effects in the terminal logs.
3. Enhanced the FraudGauge with dynamic bands and a 0.65 threshold marker.
4. Added `ForensicBackground`, an ambient layer with parallax star drift, nebula haze, and scanlines (respecting reduced motion), without interfering with readability.
5. Updated the Backend API to group features into `Screen & Print Cues` and `Compression` for telemetry processing.
6. Implemented authentic "Honest post-result logging" by removing fake `setInterval` UI delays.
7. Conducted a strict UI Fix Pass: Fixed Feature Telemetry empty states ("Awaiting feature vector"), replaced bulky Recharts with compact native metric rows (resolving huge blank gaps and ugly scrollbars), and improved bottom-row card alignment. No backend or model logic was altered.
8. **UI Telemetry Correction Pass**: Configured the frontend to separate raw feature magnitudes from risk interpretations (contextual downgrading) and added a Top Evidence explanation panel to ensure honest presentation without implying raw metrics equal fraud. No model logic or `predict.py` behavior was changed.
9. Successfully tested backend compilation and frontend Vite build.
10. **Hugging Face Docker Deployment**: Created a multi-stage `Dockerfile`, updated `backend/app.py` to serve the compiled React UI statically on port 7860, and added `check_deployment_package.py`. The project is now fully containerized and deployable to a Hugging Face Space.
11. **Documentation Update**: README polished with verified examples, screenshot section fixed, metric chart fallback added, methodology and phone-deployability explanation improved. No model logic changed.
12. **Documentation Update**: Added author name (Kartikeya) and prominent, highly readable Accuracy Highlights to the top of the README.

## Previous Accomplishments
The project has been completed end-to-end. The full 8GB ICL dataset was successfully extracted and processed, the model was retrained using XGBoost, phone-domain adaptation was applied, a feature audit fixed false positives on natural textures, and the frontend/backend/CLI have been verified consistent.

## Completed Actions
- [x] Initial heuristic-based predictor built.
- [x] Refactored feature extraction into `features.py` (21 features).
- [x] `scripts/prepare_icl_dataset.py` implemented and verified.
- [x] `scripts/validate_dataset.py` implemented.
- [x] `train.py` updated with Phone-Adapted XGBoost strategy (5-Fold CV model selection).
- [x] `predict.py` outputs clean float in normal mode, full JSON in `--json` mode, `--no-rules` flag works.
- [x] Documentation (`DATASET_SOURCES.md`, `APPROACH.md`, `README.md`, `RUNBOOK.md`, `knowledge.md`, `changes.md`) updated.
- [x] Created `backend/app.py` FastAPI server with `/health` and `/predict` endpoints.
- [x] Frontend overhauled into professional SOC dashboard. Build passes.
- [x] **Extracted the full 8GB ICL Dataset into dataset/real and dataset/screen.**
- [x] **Switched to XGBoost for model training (GPU for training, CPU for inference).**
- [x] **Completed final training on 2,344 images with Leakage-Free Grouped Splits (~98.9% accuracy).**
- [x] **Phone-domain adaptation: mixed ICL + Phone training, 5-Fold CV selection, threshold 0.65.**
- [x] **Deep feature audit: fixed naive FFT/moiré overfiring on natural textures (flowers, fabric).**
- [x] **Contextual feature refinement: moiré flatness penalty, bezel/glare require rect_contour_score.**
- [x] **Scoring integrity: raw_model_score / rule_boost_total / final_score separated in all outputs.**
- [x] **Frontend risk bands updated: 0–0.35 Real, 0.35–0.65 Borderline, 0.65–1.0 Screen.**
- [x] **Threshold display cleaned: shows 0.65 not 0.6500000000000001.**
- [x] **Backend risk bands match frontend (borderline / needs review zone added).**
- [x] **Fresh unseen sanity test run on manual_test/unknown/ — 8/10 correct.**
- [x] **CLI vs Backend consistency verified: exact score match on same image.**
- [x] **Submission ZIP created: submission/SalesCode_Recapture_Detector.zip.**

## Current Model Metrics
**Core Architecture:** Phone-Adapted XGBoost Classifier (21 features, max_depth=10, 100 estimators)
**Threshold:** 0.65

### ICL Dataset Validation (GroupShuffleSplit — Leakage-Free)
- **Accuracy:** ~98.9%
- **F1 Score:** ~99.2%
- **ROC AUC:** ~99.97%
*Note: These metrics reflect the model's ability to classify high-resolution laboratory conditions cleanly.*

### Real-World Phone Validation (Before Adaptation)
- **Accuracy:** 55.10%
- **F1 Score:** 66.67%

### Real-World Phone Validation (After Phone-Adapted CV & Feature Audit)
- **Adaptation Strategy:** Contextual feature refinement, mixed ICL+Phone training, 5-Fold CV selection, threshold 0.65.
- **F1 Score:** ~79.5% (5-Fold CV on 53 phone images)
- **Calibration Score (same set):** 100% — NOT an independent test. These images were used to select the threshold.

### Fresh Unseen Sanity Test (manual_test/unknown/)
- **Images tested:** 10 (5 real, 4 screen, 1 borderline misclassified)
- **Correct:** 8/10 (80%)
- **False Positives:** 0 (no real images wrongly called screen)
- **False Negatives:** 2 (borderline flower photo at 0.41, synthetic laptop image at 0.29)

## Final Verification Status
- `python -m py_compile predict.py train.py features.py backend/app.py` → **PASS**
- `npm run build` (frontend) → **PASS** (727 modules, ~820ms)
- `python predict.py image.jpg` → **single float output** ✓
- `python predict.py image.jpg --json` → **full JSON** ✓
- CLI score == Backend API score → **EXACT MATCH** ✓

## Next Actions
None. Project is submission-ready. No production accuracy claims are made.
