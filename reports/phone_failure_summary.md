# Phone Failure Analysis

**Total Failures:** 22
- False Positives (Real flagged as Screen): 18
- False Negatives (Screen flagged as Real): 4

## Insights
- **WhatsApp Compression:** 22 out of 22 failed images were heavily compressed via WhatsApp.
- **Most Common Resolution of failures:** 960x1280

### Average Feature Values for False Positives
False positives (real images) are likely triggering on these features (high values typically indicate a screen):
- `fft_hf_ratio`: 0.7827
- `laplacian_var`: 424.6870
- `edge_density`: 0.0488
- `banding_score`: 0.0005

### Conclusion
The current features are heavily sensitive to high-frequency noise introduced by lossy JPEG compression. Before feature extraction, images must be resized/normalized and optionally smoothed to strip out compression blockiness while retaining true physical screen Moiré.
