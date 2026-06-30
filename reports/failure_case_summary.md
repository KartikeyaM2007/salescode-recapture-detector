# Failure Case Debug Summary

## Observed Behavior
We analyzed `real 1.jpeg` and `fake 1.jpeg` directly from the model using the `--no-rules` bypass. 
- The raw XGBoost model produces a score of **0.8889** for the real flower and **0.9759** for the recaptured flower. 
- Because both scores are extremely high, the model intrinsically believes both are screens. The heuristic layer applies a `-0.1` boost to the real image and a `+0.15` boost to the fake image, yielding final scores of **0.7889** and **1.0000** respectively.

## Feature Analysis
The XGBoost model is heavily penalizing the real image because it shares characteristics that the model has incorrectly learned to associate with screens:
1. **High Frequency Energy (`h_freq_peak`, `v_freq_peak`, `local_fft_hf`)**: The real flower has sharp petal edges and patterned cloth, which trigger the FFT high-frequency detectors similarly to a screen grid.
2. **Saturation**: The bright colors of the real flower yield a high saturation score, which the model might associate with vibrant screen displays.

The model is failing to recognize true screen-specific cues on their own, and is instead relying on overly broad features (sharpness, contrast, frequency) that occur naturally in complex scenes.

## Conclusion
The threshold was not the root problem; the XGBoost model itself has overfitted to dataset biases and is failing to generalize to out-of-distribution real photos. We must retrain or recalibrate the model, reduce its reliance on generic features, and prioritize robust screen cues (bezel, moiré, pixel grid).
