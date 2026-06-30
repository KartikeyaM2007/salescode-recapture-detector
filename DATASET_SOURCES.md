# Dataset Sources

## ICL Single-Capture and Recaptured Image Database
*   **Source:** https://www.commsp.ee.ic.ac.uk/~pld/research/Rewind/Recapture/
*   **Description:** Contains thousands of real single-capture photos and recaptured photos (photos of LCD screens).

### Current Dataset State
**The full 8GB ICL dataset is integrated and active.**
The pipeline extracts images from `SingleCaptureImages.zip` into `dataset/real` and `RecapturedImages.zip` into `dataset/screen`, with full SHA256 deduplication and structural validation.

### Dataset Label Definitions
- **real (0) (`SingleCaptureImages`)**: Direct camera capture of a physical scene/object. May include books, printed text, signs, posters, water ripples, shiny objects, complex textures, buildings, color charts.
- **screen (1) (`RecapturedImages`)**: Recaptured/second-capture image, including screen or printout recapture. 

> [!WARNING]
> The `screen` class means recaptured/second-capture, not necessarily an image with a visible display bezel. In the ICL dataset, many recaptured images look like normal photos because the screen/printout boundary is cropped out. They may show color shift, contrast change, blur/softness, moiré or display texture, overexposure/clipping, screen/pixel noise, periodic frequency artifacts, compression-like artifacts, rotation/orientation differences, or loss of natural texture detail.

### Retraining
To perform retraining locally, execute `python scripts/prepare_icl_dataset.py --mode local --local-dir dataset/Data`.

- **Format**: PNG/JPG images (various resolutions, typically large).
- **Integration Status**: 100% Downloaded and Processed.
- **Data Leakage Notice**: The ICL dataset contains images of the exact same scene in both real and recaptured variants. We implemented a `GroupShuffleSplit` on the embedded scene ID in the filenames to prevent data leakage during training and test splits.

## ROSE Youtu Dataset (Skipped)
*   **Source:** https://rose1.ntu.edu.sg/dataset/faceLivenessDetection/
*   **Status:** Skipped because it requires creating an account, manually signing a release agreement, and waiting for manual approval. It could not be automated.
