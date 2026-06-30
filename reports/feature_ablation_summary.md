# Feature Ablation Summary

| Ablated Group      |   Accuracy |   Precision |   Recall |       F1 |   False Positives |   False Negatives |
|:-------------------|-----------:|------------:|---------:|---------:|------------------:|------------------:|
| None (Baseline)    |   0.790909 |    0.722619 |        1 | 0.836557 |                11 |                 0 |
| brightness_color   |   0.810909 |    0.748571 |        1 | 0.852564 |                10 |                 0 |
| blur_sharpness     |   0.827273 |    0.760714 |        1 | 0.861172 |                 9 |                 0 |
| fft_global_freq    |   0.923636 |    0.885714 |        1 | 0.935897 |                 4 |                 0 |
| local_patch_fft    |   0.809091 |    0.744048 |        1 | 0.849744 |                10 |                 0 |
| moire_banding      |   0.829091 |    0.763095 |        1 | 0.863137 |                 9 |                 0 |
| jpeg_compression   |   0.809091 |    0.744048 |        1 | 0.849744 |                10 |                 0 |
| bezel_border       |   0.770909 |    0.704762 |        1 | 0.823736 |                12 |                 0 |
| perspective_rect   |   0.790909 |    0.722619 |        1 | 0.836557 |                11 |                 0 |
| glare_overexposure |   0.790909 |    0.722619 |        1 | 0.836557 |                11 |                 0 |
| printout_paper     |   0.809091 |    0.744048 |        1 | 0.849744 |                10 |                 0 |
