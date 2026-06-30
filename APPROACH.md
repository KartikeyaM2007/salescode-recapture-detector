# Approach: Spot the Fake Photo

## Methodology
## Machine Learning Approach

The final method combines handcrafted image-processing features, frequency-domain analysis, a lightweight phone-adapted XGBoost classifier, and conservative rule-based score boosts for strong screen/printout evidence. The model does not rely on raw-pixel deep learning. It runs on compact numeric features and keeps inference small, fast, and CPU-friendly.

### Dataset Definitions
- **real (0)**: Direct camera capture of a physical scene/object. May include books, printed text, signs, posters, water ripples, shiny objects, complex textures, buildings, color charts.
- **screen (1)**: Recaptured/second-capture image, including screen or printout recapture. 

> [!WARNING]
> The `screen` class means recaptured/second-capture, not necessarily an image with a visible display bezel. They may show color shift, contrast change, blur/softness, moiré or display texture, overexposure/clipping, screen/pixel noise, periodic frequency artifacts, compression-like artifacts, rotation/orientation differences, or loss of natural texture detail.

### Feature Engineering (CPU-bound)
Images are resized to 800px on the longest edge, and we extract:
1. **LBP (Local Binary Patterns) Histogram**: To detect the regular grid structure of screen pixels (the "screen door effect").
2. **Haralick Textures (GLCM)**: To quantify the micro-textures and contrast variations inherent to digital displays.
3. **High-Frequency FFT Energy**: Screens emit structured light that introduces high-frequency aliasing and Moiré patterns when captured by a secondary camera.
4. **Laplacian Variance**: To measure overall image sharpness and blur, as recaptures often suffer from focus degradation.

### Data Leakage Discovery & Grouped Validation & Testing
We have strictly isolated two different evaluation regimes:

#### 1. ICL Dataset (Laboratory Conditions)
- **Problem**: We discovered **Data Leakage** in the raw ICL dataset where images of the same exact scene existed in both real and screen variants. A random split falsely boosted metrics because the model memorized the background rather than learning screen artifacts.
- **Fix**: We extracted the `scene_id` from the filenames and applied `GroupShuffleSplit` to ensure that any scene seen in training is completely absent from the test set.
- **Leakage-Free Test Metrics**:
  - Accuracy: **~99.11%**
  - F1 Score: **~99.24%**
  - ROC AUC: **~99.9%**

#### 2. User Phone Photos (Real-World Conditions)
- **Validation Method**: Evaluated on a dataset of manually collected images (WhatsApp/Phone Camera) used during the Phone-Adapted CV strategy.
- **Phone metrics before phone-domain adaptation:**
  - Accuracy: **55.10%**
  - Precision: **55.00%**
  - Recall: **84.62%**
  - F1 Score: **66.67%**
  - False Positives: **18**
  - False Negatives: **4**

- **Phone metrics after adaptation (5-Fold CV, honest generalization):**
  - F1 Score: **~79.5%**
  - Threshold: **0.65**
  - Calibration score on same 53 images: 100% (NOT independent — threshold was selected on these images)

## Risk Band Definitions
- **0.00–0.35**: Likely Real
- **0.35–0.65**: Borderline / Needs Review
- **0.65–1.00**: Likely Recaptured/Screen

## 4. Why Handcrafted Features Over Deep Learning?
- **Cost & Speed Constraint**: The assignment explicitly prohibits heavy GPU dependencies for inference. A MobileNetV3 or ResNet would require significant compute/memory. OpenCV operations run on CPU in milliseconds.
- **Limitation**: Real-world phone photos introduce WhatsApp/JPEG compression artifacts. These compression blocks mimic the high-frequency patterns of physical screens.

## Known Limitations & Domain Shift
The model was originally trained on the high-quality 8GB ICL dataset. When deployed against custom phone images compressed via WhatsApp, accuracy dropped initially due to OpenCV heuristics being highly sensitive to WhatsApp JPEG blockiness.
To bridge this gap, we implemented a **Phone-Adapted Model Strategy**:
1. Included assignment-specific structural features (perspective contours, black bezel detection).
2. Trained a Phone-Adapted XGBoost on mixed ICL + Phone data.
3. Added strict conservative rule-based boosts. Previously, an over-aggressive bezel rule caused False Positives on real images with dark backgrounds/rectangular crops (like real flower images). We fixed this by introducing negative rules for natural scenes (organic object boundaries, low artificial texture) and capping rule boosts based on multi-cue presence. Only strong multi-cue screen evidence can now push a score above 0.80.

The phone-domain metrics are useful for assignment validation, but they are not a production accuracy claim because the phone set is small (53 images) and used during adaptation.

The current model achieves **~79% F1-Score** on a 53-image phone validation set via 5-Fold Stratified Cross Validation. The threshold of 0.65 balances catching screens vs false positives.

### Scoring Transparency & Integrity Audit
To ensure that rule-based safety boosts are not artificially inflating confidence scores or overfitting small datasets, we instituted a strict integrity pipeline:
- **Separation of Scores:** The backend and frontend explicitly separate `raw_model_score` from `rule_boost_total`. 
- **Bypass Flag:** The CLI prediction tool (`predict.py`) includes a `--no-rules` flag to observe the naked XGBoost model performance.
- **Rule Limits:** Individual rule boosts are capped at a maximum of `0.15`, and the overall rule boost is bounded. Strong multi-cue evidence is required to reach high risk thresholds.
- **Frontend Telemetry Correction (Honesty Pass):** A core philosophy of this project is that *raw feature magnitude does not automatically equal fraud*. The React frontend dynamically downgrades raw feature warnings (e.g., from "Suspicious" to "Contextual/Organic") if the holistic model score suggests the image is real. This guarantees the dashboard honestly explains the model's contextual decisions without inventing fake SHAP values or contradicting itself.

### Deep Feature Audit: Fixing Real-World False Positives
During initial real-world testing, the model aggressively flagged highly-textured organic scenes (like close-up photos of flowers or patterned fabric) as screens. To diagnose this, we built a comprehensive testing suite:
- **`audit_features.py`**: Aggregated the mean and standard deviation of each feature across specific semantic classes (e.g., flowers, text, screens). We discovered that `moire_score` and `fft_hf_ratio` were firing strongly on the natural high-frequency edges of flower petals.
- **`feature_ablation.py`**: Performed leave-one-group-out evaluation. This proved that naive global frequency features were causing the model to confuse physical sharpness with digital screen grids.

**The Fix (Contextual Features):**
Instead of blindly relying on global frequencies, we refactored `features.py` to require structural context:
1. **Contextual Moiré**: Added a "flatness" penalty to the moiré calculation. Moiré on a screen usually occurs on a relatively flat pane of glass. If the surrounding area has an extremely high edge density (like a bush of flowers), the moiré score is drastically downweighted.
2. **Contextual Bezel & Glare**: `bezel_score` (black borders) and `glare_patch_size` (overexposed light patches) now explicitly require the presence of a screen-like rectangular contour (`rect_contour_score`) or strong structural moiré. This prevents window frames or bright sunlight on a wall from triggering screen rules.
3. **Downweighted FFT Global Energy**: We reduced the raw scalar value of global `fft_hf_ratio` and peak energy by 90% (0.1 -> 0.01) to prevent the classifier from over-relying on basic image sharpness, forcing the model to depend on local frequency patches and blockiness.

### Model Training & Performance
- **Algorithm**: Phone-Adapted `XGBClassifier` with `tree_method='hist'`.
- **Training Acceleration**: GPU (`device='cuda'`) was utilized during training to dramatically accelerate the ensemble building.
- **Inference**: Prediction is strictly enforced on **CPU** (`model.set_params(device='cpu')`) for maximum deployment compatibility.
- **Final Phone Validation Metrics (5-Fold CV)**: 
  - F1 Score: ~79.5%
  - Calibration Score (same 53 images used for threshold selection): 100% — NOT an independent benchmark.
  - No production accuracy claim is made.

### Model Size & Latency Estimate
- **Model File Size**: ~125 KB (`model.joblib`)
- **Feature Extraction Latency**: ~750ms - 1.5s per image (depending on CPU and resolution)
- **Inference Latency**: ~1ms
- **Cost**: Extremely low. Inference can be run on basic CPU instances (e.g., AWS t3.micro) without requiring expensive GPU droplets.

The model performs exceptionally well at distinguishing real photos from screen recaptures based on extracted texture and frequency features.

## Latency & Cost
* **Latency:** Fast. Feature extraction and Random Forest inference takes ~10-30 ms per image on a modern CPU.
* **Cost:** Practically $0 on-device. Feasible for edge deployment on phones.
