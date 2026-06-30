---
title: SalesCode Recapture Detector
Live Link : https://huggingface.co/spaces/Kartikeym2007/salescode-recapture-detector
---

# SalesCode Recapture Detector

**Author:** Kartikeya

This project detects whether an input image is a direct real photo or a recaptured image, such as a photo of a screen or printout. The output is a single score from `0` to `1`.

- `0` means real photo
- `1` means screen, printout, or recaptured photo

The normal command line contract is:

```bash
python predict.py image.jpg
```

Normal output is one float only:

```text
0.4870
```

## Summary

I built this as a small CPU friendly computer vision pipeline. The model does not look for objects in the image. It looks for capture artifacts: moire patterns, display banding, glare, compression, blur, local frequency spikes, rectangular screen cues, and paper or print texture.

The final classifier is a Phone Adapted XGBoost model trained on handcrafted image features. A conservative rule layer is applied after the raw model score, but only when multiple screen or print cues agree.

```text
final_score = clamp(raw_model_score + rule_boost_total, 0, 1)
```

Decision threshold:

```text
final_score >= 0.65 -> recaptured
final_score < 0.65  -> real
```

## Method

The image is resized and converted into grayscale and color spaces for feature extraction. I extract 21 numeric features covering:

- brightness, contrast, and saturation
- Laplacian sharpness and Sobel edge strength
- edge density
- global and local FFT energy
- moire and banding cues
- glare and overexposed patch size
- rectangular contour and perspective cues
- black bezel estimate
- paper texture estimate
- JPEG compression and blockiness

Those features are passed into the XGBoost model. The rule layer then adds a small boost only for strong paired evidence such as bezel plus moire, perspective plus glare, or paper texture plus banding.

## Why This Approach

A direct photo and a recaptured photo can show the same flower, room, book, or building. The useful signal is usually not the subject. It is the second capture process.

That is why I used image processing and frequency analysis instead of a large raw pixel model. The result is small, fast, explainable, and practical to run on a CPU.

## Metrics

| Metric | Value | Validation Method | Notes |
| --- | ---: | --- | --- |
| ICL Accuracy | ~98.9% | GroupShuffleSplit | Grouped split to reduce scene leakage |
| ICL F1 | ~99.2% | GroupShuffleSplit | Lab dataset metric |
| Phone CV F1 | ~79.5% | 5 fold stratified CV | Honest small phone set estimate |
| Phone Calibration Score | 100% | Same 53 phone images used for threshold selection | Calibration only |
| Threshold | 0.65 | Selected after calibration | Final decision threshold |

The 100% phone calibration score is not an independent benchmark. Those 53 images were also involved in selecting the threshold. The more honest phone domain estimate is the 5 fold CV result of about 79.5% F1. I am not claiming production accuracy from the small phone set.

## Risk Bands

| Score Range | Label | Meaning |
| --- | --- | --- |
| `0.00` to `0.35` | Likely real | Strong direct photo evidence |
| `0.35` to `0.65` | Borderline | Mixed or ambiguous evidence |
| `0.65` to `1.00` | Likely recaptured | Strong screen or print evidence |

## Example Behavior

| File | Ground Truth | Score | Prediction | Notes |
| --- | --- | ---: | --- | --- |
| `real/outdoor.png` | Real | 0.07 | Real | Direct outdoor scene |
| `real/books.png` | Real | 0.40 | Borderline real | Direct object photo with texture/compression |
| `flower_screen.jpeg` | Screen | 0.98 | Screen | Recaptured screen example |
| `screen/laptop.png` | Screen ambiguous | 0.29 | Miss | Synthetic example lacked real recapture artifacts |

Borderline results are expected on difficult cases. Some real images contain high frequency natural texture, and some recaptured images do not show a clear bezel or obvious screen artifact.

## Feature Refinement

Early versions overreacted to natural texture. Flower petals, fabric, sunlight, windows, labels, and posters can trigger frequency or contour features even when the image is a real direct photo.

I fixed that by making the screen cues more contextual:

- moire is reduced when the surrounding area is dense organic texture
- glare and bezel cues require stronger rectangular screen context
- global FFT energy is downweighted so the model depends more on local artifact evidence
- rule boosts require multiple cues instead of a single noisy feature

This made the scores easier to audit and reduced false positives on natural scenes.

## Final Configuration

| Item | Value |
| --- | --- |
| Model | Phone Adapted XGBoost |
| Feature count | 21 |
| Threshold | 0.65 |
| Normal output | Single float from 0 to 1 |
| Debug mode | `--json` |
| Rule bypass | `--json --no-rules` |

## Dataset Notes

The training work used the ICL Single Capture and Recaptured Image Database along with a small personal phone photo set. The full raw datasets are intentionally not included in this repository. See [DATASET_SOURCES.md](DATASET_SOURCES.md) for source and label details.

## Running Locally

```bash
pip install -r requirements.txt
python predict.py path/to/image.jpg
python predict.py path/to/image.jpg --json
uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Docker

```bash
docker build -t salescode-recapture-detector .
docker run --rm -p 7860:7860 salescode-recapture-detector
```

Then open:

```text
http://127.0.0.1:7860/
http://127.0.0.1:7860/health
```

## Files

- `predict.py` is the required command line predictor.
- `features.py` extracts the 21 handcrafted features.
- `model.joblib` is the trained XGBoost model.
- `model_metadata.json` stores threshold and feature metadata.
- `backend/app.py` serves the API and built frontend.
- `frontend/` contains the dashboard.
- `reports/` contains validation and debugging summaries.
