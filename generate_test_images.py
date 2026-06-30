import numpy as np
import cv2
import os

# Create a "real" looking image (smooth gradient)
real_img = np.zeros((256, 256, 3), dtype=np.uint8)
for i in range(256):
    real_img[:, i] = (i, i, i)
cv2.imwrite('test_synthetic_real.jpg', real_img)

# Create a "screen" looking image (high frequency grid / moire simulation)
screen_img = np.zeros((256, 256, 3), dtype=np.uint8)
for i in range(256):
    for j in range(256):
        if (i % 4 == 0) or (j % 4 == 0):
            screen_img[i, j] = (255, 255, 255)
        else:
            screen_img[i, j] = (50, 50, 50)
cv2.imwrite('test_synthetic_screen.jpg', screen_img)

print("Created synthetic test images.")
