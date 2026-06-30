# SalesCode Project Knowledge Base

## Assignment Objective
Given one image, detect whether it's a **real photo** (0) or a **photo of a screen** (recapture) (1). Output a fraud score between 0 and 1. Final accuracy must be measured after training on the full ICL dataset or the user's own labeled phone dataset.

## Expected Input/Output Behavior
- **Input:** Single image path (JPG/PNG).
- **Output:** A numeric fraud score between 0 and 1 printed to standard output. 0 = real photo, 1 = photo of a screen.
- **CLI:** `python predict.py path/to/image.jpg` → single float
- **JSON mode:** `python predict.py path/to/image.jpg --json` → full breakdown
- **No-rules mode:** `python predict.py path/to/image.jpg --json --no-rules` → bypass rule layer

## Dataset Label Definitions
- **real (0)**: Direct camera capture of a physical scene/object. May include books, printed text, signs, posters, water ripples, shiny objects, complex textures, buildings and monuments, color charts.
- **screen (1)**: Recaptured/second-capture image, including screen or printout recapture.

> [!WARNING]
> The `screen` class means recaptured/second-capture, not necessarily an image with a visible display bezel. They may show color shift, contrast change, blur/softness, moiré or display texture, overexposure/clipping, screen/pixel noise, periodic frequency artifacts, compression-like artifacts, rotation/orientation differences, or loss of natural texture detail.

## Current Model Architecture
**Phone-Adapted XGBoost Classifier**
- 21 handcrafted features (frequency, texture, structural, color)
- Threshold: **0.65**
- Preprocessing: 1024×1024 resize + Gaussian blur
- Scoring: `final_score = clamp(raw_model_score + rule_boost_total, 0, 1)`
- Rule boosts: multi-cue only (bezel+moiré, perspective+glare, paper+banding), capped at +0.10 per pair

## Risk Bands
- **0.00–0.35**: Likely Real
- **0.35–0.65**: Borderline / Needs Review  
- **0.65–1.00**: Likely Recaptured/Screen

## Current Metrics

| Metric | Value | Method |
|--------|-------|--------|
| ICL Accuracy | ~98.9% | GroupShuffleSplit (leakage-free) |
| ICL F1 | ~99.2% | GroupShuffleSplit |
| Phone Honest F1 | ~79.5% | 5-Fold Stratified CV |
| Phone Calibration | 100% | Calibration set (same images used for threshold selection) |

## Implementation Summary
The current model uses **XGBoost Classifier** with 21 manually engineered features, trained on the **ICL Dataset** (~2,344 images). We discovered and fixed a **Data Leakage** issue by implementing `GroupShuffleSplit` on scene IDs.

### Phone-Adapted Strategy
1. **Assignment-Specific Features**: `bezel_score`, `perspective_score`, `glare_patch_size`, `paper_texture`, `rect_contour_score`.
2. **Scale Normalization**: 1024×1024 + light Gaussian Blur to strip WhatsApp macro-blockiness.
3. **5-Fold CV Model Selection**: 4 strategies evaluated; Phone-Adapted XGBoost selected.
4. **Rule-Based Safety Boosts**: Multi-cue only, conservative, capped.

### Feature Audit (fixing false positives on natural textures)
- **Problem**: Naive `fft_hf_ratio` and `moire_score` fired on natural high-frequency edges (flowers, fabric).
- **Fix 1**: Contextual Moiré — flatness penalty so dense organic scenes don't trigger.
- **Fix 2**: Contextual Bezel & Glare — require `rect_contour_score` presence.
- **Fix 3**: Downweighted global FFT (0.1 → 0.01 scalar weight).

## Current File Structure
- `predict.py`: CLI entrypoint, scoring logic, rule boosts
- `features.py`: 21-feature extraction (contextual, audited)
- `train.py`: Phone-adapted XGBoost training with 5-Fold CV
- `model.joblib`: Trained model
- `model_metadata.json`: threshold=0.65, feature list, ICL metrics
- `backend/app.py`: FastAPI /predict and /health
- `frontend/src/App.jsx`: SOC dashboard with borderline zone visualization
- `scripts/evaluate_phone_images.py`: Calibration evaluation
- `scripts/sanity_test_predictions.py`: Fresh unseen test runner

## Dependencies
- `opencv-python`, `numpy`, `Pillow`, `scikit-learn`, `xgboost`, `joblib`, `fastapi`, `uvicorn`

## Latency/Cost Notes
- **Feature extraction:** ~750ms–1.5s per image (CPU)
- **Inference:** ~1ms
- **Model size:** ~360 KB
- **Cost:** Practically free on CPU inference.
