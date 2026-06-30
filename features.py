import cv2
import numpy as np

def extract_features(img: np.ndarray, log_callback=None):
    """
    Extracts a comprehensive set of handcrafted CV features from an image.
    Returns a flat feature vector (numpy array) and a dictionary of grouped features.
    
    If log_callback is provided, it will be called with status strings for frontend terminal logs.
    """
    
    def log(msg):
        if log_callback:
            log_callback(msg)

    features_dict = {}

    # 0. Scale Normalization & Denoising
    log("Applying scale normalization...")
    # Resize to 1024x1024 to standardize spatial frequencies across camera types
    img = cv2.resize(img, (1024, 1024))
    
    # 1. Brightness and Contrast Stats
    log("Extracting brightness and contrast...")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Light denoising for compression artifacts analysis
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    mean_brightness = np.mean(gray)
    std_contrast = np.std(gray)
    # Scale down brightness/contrast to reduce their impact as primary cues
    features_dict['brightness'] = float(mean_brightness) * 0.1 
    features_dict['contrast'] = float(std_contrast) * 0.1

    # 1.5 JPEG Compression / Blockiness Estimate
    log("Estimating JPEG compression artifacts...")
    # We estimate blockiness by comparing the image to a heavily compressed version of itself
    _, encoded = cv2.imencode('.jpg', gray, [int(cv2.IMWRITE_JPEG_QUALITY), 10])
    decoded = cv2.imdecode(encoded, cv2.IMREAD_GRAYSCALE)
    blockiness_diff = np.mean(np.abs(gray.astype(int) - decoded.astype(int)))
    # Compression alone is not a screen cue. Downweight it heavily.
    features_dict['compression_diff'] = float(blockiness_diff) * 0.01

    # 2. Saturation and Color Stats
    log("Measuring saturation and color stats...")
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mean_saturation = np.mean(hsv[:, :, 1])
    # Downweight saturation to avoid penalizing bright real objects like flowers
    features_dict['saturation'] = float(mean_saturation) * 0.1
    
    # 3. Blur / Sharpness (Laplacian variance)
    log("Measuring Laplacian sharpness...")
    laplacian_var = cv2.Laplacian(blurred, cv2.CV_64F).var()
    features_dict['laplacian_var'] = float(laplacian_var) * 0.1

    # 4. Edge Density (Canny/Sobel)
    log("Running Canny edge analysis...")
    edges = cv2.Canny(blurred, 100, 200)
    edge_density = np.sum(edges > 0) / edges.size
    features_dict['edge_density'] = float(edge_density) * 0.1

    # Sobel
    sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
    sobel_mag = np.sqrt(sobelx**2 + sobely**2)
    features_dict['sobel_mean'] = float(np.mean(sobel_mag)) * 0.1

    # 5. FFT High-Frequency Energy & Moiré
    log("Computing FFT frequency energy...")
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
    
    h, w = gray.shape
    cy, cx = h // 2, w // 2
    r = int(min(h, w) * 0.25)
    
    y_grid, x_grid = np.ogrid[:h, :w]
    mask = (x_grid - cx)**2 + (y_grid - cy)**2 > r**2
    
    high_freq_energy = np.mean(magnitude_spectrum[mask])
    low_freq_energy = np.mean(magnitude_spectrum[~mask])
    hf_ratio = high_freq_energy / (low_freq_energy + 1e-6)
    features_dict['fft_hf_ratio'] = float(hf_ratio)
    
    # Synthetic moire combo. Fix: Moire is periodic pattern on flat surface.
    # Scale down if scene has too much random edge texture (like flowers).
    flatness = max(0.0, 1.0 - (edge_density / 0.15))
    features_dict['moire_score'] = float(hf_ratio * edge_density * flatness * 100)

    # 5.5 Local Patch FFT
    log("Computing Local Patch FFT...")
    patch = gray[cy-64:cy+64, cx-64:cx+64]
    f_patch = np.fft.fftshift(np.fft.fft2(patch))
    mag_patch = 20 * np.log(np.abs(f_patch) + 1)
    # Exclude center cross
    mask_patch = np.ones_like(mag_patch, dtype=bool)
    mask_patch[64-5:64+5, :] = False
    mask_patch[:, 64-5:64+5] = False
    features_dict['local_fft_hf'] = float(np.mean(mag_patch[mask_patch]))

    # 6. Horizontal / Vertical Frequency Peaks
    # Summing energy along axes
    log("Checking horizontal/vertical frequency peaks...")
    h_energy = np.mean(np.abs(fshift[cy, :]))
    v_energy = np.mean(np.abs(fshift[:, cx]))
    # Downweight simple generic axes frequency to prevent overfitting
    features_dict['h_freq_peak'] = float(h_energy) * 0.01
    features_dict['v_freq_peak'] = float(v_energy) * 0.01
    
    # Diagonal energy (moiré directionality)
    diag1_energy = np.mean(np.diag(np.abs(fshift)))
    diag2_energy = np.mean(np.diag(np.fliplr(np.abs(fshift))))
    features_dict['diag_freq_peak'] = float(max(diag1_energy, diag2_energy)) * 0.01

    # 7. Banding / Posterization Score
    # Screens often have fewer unique colors or visible banding.
    log("Checking moiré and banding cues...")
    # Calculate unique colors in a resized patch to estimate banding
    small_img = cv2.resize(img, (64, 64))
    unique_colors = len(np.unique(small_img.reshape(-1, small_img.shape[2]), axis=0))
    banding_score = 1.0 / (unique_colors + 1)
    features_dict['banding_score'] = float(banding_score)

    # 8. Glare / Overexposure Ratio & Largest Patch
    log("Estimating glare/overexposure patches...")
    glare_mask = (gray > 240).astype(np.uint8)
    glare_ratio = np.sum(glare_mask) / gray.size
    features_dict['glare_ratio'] = float(glare_ratio)
    
    # Largest glare patch size
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(glare_mask, connectivity=8)
    largest_glare_patch = 0
    if num_labels > 1:
        # Index 0 is background
        largest_glare_patch = np.max(stats[1:, cv2.CC_STAT_AREA]) / gray.size
        
    # Fix: Sunlight isn't glare. Only boost if there is a screen rectangle or high moire
    if features_dict.get('moire_score', 0) < 1.0:
        largest_glare_patch *= 0.1
        
    features_dict['glare_patch_size'] = float(largest_glare_patch)

    # 9. Screen-border / Perspective Rectangle Cues
    log("Detecting screen-border perspective contours...")
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rect_score = 0.0
    perspective_score = 0.0
    if contours:
        c = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(c)
        x, y, w_b, h_b = cv2.boundingRect(c)
        bounding_area = w_b * h_b
        if bounding_area > 0:
            rect_score = area / bounding_area
            
        # Check for quadrilateral (perspective rectangle)
        epsilon = 0.02 * cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, epsilon, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            perspective_score = area / (gray.size + 1e-6)  # How much of the image is the screen
            
    features_dict['rect_contour_score'] = float(rect_score)
    features_dict['perspective_score'] = float(perspective_score)

    # 9.5 Black Bezel Score
    log("Detecting visible black bezel...")
    # Bezel is usually dark and near the boundary of the detected screen, or at the edges.
    # Simple proxy: percentage of very dark pixels near the image borders
    border_mask = np.ones_like(gray, dtype=np.uint8)
    margin = 50
    border_mask[margin:-margin, margin:-margin] = 0
    dark_pixels = (gray < 30).astype(np.uint8)
    bezel_pixels = np.sum(dark_pixels & border_mask)
    bezel_score = bezel_pixels / (np.sum(border_mask) + 1e-6)
    
    # NEW FIX: only trigger if there's an actual bright rectangular screen inside
    if rect_score < 0.1:
        bezel_score = 0.0 # dark border alone is not a bezel without a screen
        
    features_dict['bezel_score'] = float(bezel_score)
    
    # 9.6 Printout / Paper Texture
    log("Estimating printout paper texture...")
    # Paper has high-frequency but low-contrast noise. 
    # Use standard deviation of high-frequency components without strong edges
    no_edges_mask = (edges == 0).astype(np.float32)
    paper_noise = laplacian_var * np.mean(no_edges_mask) 
    
    # Fix: Only trigger if there are some straight lines/perspective to indicate a physical paper
    if perspective_score < 0.05:
        paper_noise *= 0.1
        
    features_dict['paper_texture'] = float(paper_noise)

    # 10. Compression / Blockiness estimate
    log("Estimating compression blockiness...")
    # Simple heuristic: differences across 8x8 block boundaries
    # Using small diff across rows divisible by 8
    if h > 8 and w > 8:
        r1, r2 = gray[7:-1:8, :], gray[8::8, :]
        min_r = min(r1.shape[0], r2.shape[0])
        row_diff = np.mean(np.abs(r1[:min_r].astype(np.float32) - r2[:min_r].astype(np.float32)))
        
        c1, c2 = gray[:, 7:-1:8], gray[:, 8::8]
        min_c = min(c1.shape[1], c2.shape[1])
        col_diff = np.mean(np.abs(c1[:, :min_c].astype(np.float32) - c2[:, :min_c].astype(np.float32)))
        
        blockiness = (row_diff + col_diff) / 2
    else:
        blockiness = 0
    features_dict['blockiness'] = float(blockiness)

    # Convert to flat array, sorted by key to ensure consistent ordering
    feature_keys = sorted(features_dict.keys())
    feature_vector = np.array([features_dict[k] for k in feature_keys], dtype=np.float32)

    log("Features extracted successfully.")
    
    return feature_vector, features_dict

def get_feature_names():
    # Return consistent names by generating them on a dummy image
    dummy = np.zeros((32, 32, 3), dtype=np.uint8)
    _, f_dict = extract_features(dummy)
    return sorted(f_dict.keys())
