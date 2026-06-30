import numpy as np
import cv2
import os

os.makedirs("sample_images", exist_ok=True)

# These are smoke-test images only and are not used for accuracy claims.

# 1. Real-like image (Smooth gradient, no high-freq noise, no banding)
real_img = np.zeros((256, 256, 3), dtype=np.uint8)
for i in range(256):
    real_img[:, i] = (i, i, i)
# Add slight smooth blur
real_img = cv2.GaussianBlur(real_img, (5, 5), 0)
cv2.imwrite(os.path.join("sample_images", "real_like_test.jpg"), real_img)

# 2. Screen-like image (High edge density, moiré grid, banding)
screen_img = np.zeros((256, 256, 3), dtype=np.uint8)
# Add a grid pattern
screen_img[::4, :] = 255
screen_img[:, ::4] = 255
# Add severe banding
screen_img = (screen_img // 64) * 64
cv2.imwrite(os.path.join("sample_images", "screen_like_test.jpg"), screen_img)

print("Generated sample_images/real_like_test.jpg and sample_images/screen_like_test.jpg")
