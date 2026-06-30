# Changelog

## [Current Phase] UI Polish & Telemetry Enhancements
- Refactored `frontend/src/App.jsx` with a responsive 12-column grid and interactive, glassmorphic cards.
- Added dark, forensic-themed styles, background animations (scanlines/noise), and custom layout components in `frontend/src/index.css`.
- Updated `backend/app.py` `/predict` endpoint to return grouped features (`Screen & Print Cues`, `Compression`) for better UI telemetry.
- Updated `FraudGauge.jsx` to support dynamic color banding (Success/Warning/Danger) and an explicit 0.65 threshold marker.
- Updated `FeatureBarChart.jsx` to include staggered `framer-motion` animations and highlight highly suspicious features in red.
- Updated `TerminalLogs.jsx` with a realistic step-by-step typewriter reveal effect and a blinking cursor.
- Updated `WorkflowAnimation.jsx` with an animated node-flow diagram mapping directly to the actual backend pipeline steps (e.g., CV Extraction, Freq Analysis, XGBoost).
- Added `ForensicBackground.jsx` implementing a subtle animated starfield, parallax drift, galaxy haze, and scanline radar background that fully respects `prefers-reduced-motion`.
- Implemented "Honest post-result logging" by removing fake UI delays. `TerminalLogs` and `WorkflowAnimation` now correctly wait for the backend payload before revealing actual telemetry.
- **UI Fix Pass**: Completely rewrote `FeatureBarChart.jsx` to use native HTML/CSS compact metric rows (dropping `recharts`, which halved the bundle size). Fixed Feature Telemetry empty states ("Awaiting feature vector"), removed empty floating section labels, improved bottom-row card layout consistency (`min-h-[380px]`), and polished Sample Library styling. No model logic or predict.py behavior was changed.
- **UI Telemetry Correction Pass**: Updated `FeatureBarChart.jsx` and `App.jsx` to distinguish raw feature values from risk interpretations. Added contextual logic (e.g., high CV features on a real image are flagged as "Contextual/Organic" rather than "Suspicious"). Added a "Top Evidence" interpretation section to explain how features combine. Absolutely no model logic, metrics, or `predict.py` behavior was changed.
- **Hugging Face Deployment Preparation**: Created a multi-stage `Dockerfile`, updated `backend/app.py` endpoints to `/api/` and mounted the React `frontend/dist` directory to serve everything from FastAPI on port 7860. Updated `.dockerignore` to exclude large files. Added `DEPLOYMENT.md` and `check_deployment_package.py`.
- **Documentation Update**: README polished with verified examples, screenshot section fixed, metric chart fallback added, methodology and phone-deployability explanation improved. No model logic changed.
- **Documentation Update**: Added author name (Kartikeya) and prominent, highly readable Accuracy Highlights to the top of the README.
- Ran successful frontend build (`npm run build`) and backend compile check (`python -m py_compile`).

## [Previous Phase] Model Handover & Refinement

| Step | File | Description | Tested? |
|------|------|-------------|---------|
| 1 | `knowledge.md` | Created project knowledge base | N/A |
| 2 | `changes.md` | Created changelog | N/A |
| 3 | `forchatgpt.md` | Context file created | N/A |
| 4 | `PROJECT_STATE.md` | State file created | N/A |
| 5 | `RUNBOOK.md` | Setup and run instructions | N/A |
| 6 | `predict.py` | Added Moiré pattern & edge heuristic logic | Yes — float output |
| 7 | `features.py` | Refactored features out of predict | Yes — imports cleanly |
| 8 | `train.py` | Implemented XGBoost training logic | Yes — model trained |
| 9 | `scripts/prepare_icl_dataset.py` | Downloader & preparer | Yes — labels.txt parsed |
| 10 | `backend/app.py` | FastAPI server | Yes — py_compile passed |
| 11 | `frontend/` | React + Vite UI | Yes — npm run build passed |
| 12 | `features.py` | Expanded to 21 CV features | Yes — retrained model |
| 13 | `predict.py` | Cleaned output formatting, `--json` and `--no-rules` flags | Yes — clean float + JSON |
| 14 | `frontend/src/App.jsx` | SOC dashboard UI overhaul | Yes — build passed |

## Post-ICL Changes

### Phone-Domain Adaptation
- Evaluated 53 custom phone photos. Baseline accuracy: 55.10%, F1: 66.67%.
- Implemented Phone-Adapted Strategy: 1024×1024 normalization, Gaussian blur denoising, new structural features (perspective, bezel, glare, paper texture, rect_contour_score).
- Used 5-Fold Stratified CV to select best model. Phone-Adapted XGBoost selected.
- Threshold set to 0.65. Honest 5-Fold CV F1: ~79.5%.

### Feature Audit (fixing real-world false positives)
- Built `scripts/audit_features.py` and `scripts/feature_ablation.py`.
- Discovered `fft_hf_ratio` and `moire_score` falsely triggered on flower petals and natural textures.
- **Fixed** via contextual feature refinement:
  - Contextual Moiré: flatness penalty added.
  - Contextual Bezel & Glare: require `rect_contour_score`.
  - Downweighted global FFT scalar (0.1 → 0.01).
- Rule boosts made conservative: multi-cue only, capped at +0.10.
- Scoring integrity: `raw_model_score` / `rule_boost_total` / `final_score` separated everywhere.

### Metric Transparency Fix
- Frontend previously showed misleading 100% phone accuracy (calibration score).
- Fixed to show honest ~79.5% 5-Fold CV F1.
- `reports/phone_metrics.json` now includes `validation_method` and `honest_5_fold_cv_f1` fields.
- `reports/phone_test_summary.md` relabeled as calibration summary.

### Frontend Risk Band Update
- Added borderline zone: 0.35–0.65 = "Borderline / Needs Review" (yellow).
- Updated prediction logic: `>= 0.65` = screen, `0.35–0.65` = borderline, `< 0.35` = real.
- Threshold display cleaned: uses `parseFloat(val).toFixed(2)` to show `0.65`.
- Backend `get_risk_level()` updated to match frontend bands.

### Final Verification (2026-06-30)
1. `python -m py_compile predict.py train.py features.py backend/app.py` → **PASS**
2. `npm run build` (frontend) → **PASS** (727 modules, 820ms)
3. `python predict.py real_image.jpg` → **0.4870** (single float) ✓
4. `python predict.py screen_image.jpg` → **0.9761** (single float) ✓
5. `python predict.py real_image.jpg --json` → full JSON with all required fields ✓
6. `python predict.py real_image.jpg --json --no-rules` → rule layer bypassed ✓
7. CLI score == Backend API score for same image → **EXACT MATCH** ✓
8. Fresh unseen sanity test (manual_test/unknown/): 8/10 correct, 0 false positives ✓
9. Submission ZIP created: `submission/SalesCode_Recapture_Detector.zip` ✓
