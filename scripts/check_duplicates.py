import os
import glob
import cv2
import hashlib

def get_md5(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_phash(filepath):
    # simple custom pHash implementation
    img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    img = cv2.resize(img, (8, 8))
    avg = img.mean()
    bits = (img > avg).flatten()
    # convert bits to hex string
    res = 0
    for i, b in enumerate(bits):
        if b:
            res |= 1 << i
    return hex(res)

def check_duplicates():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "dataset", "my_photos")
    real_files = glob.glob(os.path.join(base_dir, "real", "*.*"))
    screen_files = glob.glob(os.path.join(base_dir, "screen", "*.*"))
    
    hashes = {}
    phashes = {}
    
    all_files = real_files + screen_files
    print(f"Checking {len(all_files)} files for duplicates...")
    
    exact_dupes = []
    near_dupes = []
    
    for f in all_files:
        md5 = get_md5(f)
        if md5 in hashes:
            exact_dupes.append((f, hashes[md5]))
        else:
            hashes[md5] = f
            
        phash = get_phash(f)
        if phash and phash in phashes:
            near_dupes.append((f, phashes[phash]))
        else:
            phashes[phash] = f
            
    print("\n--- EXACT DUPLICATES ---")
    if exact_dupes:
        for f1, f2 in exact_dupes:
            print(f"{os.path.basename(f1)} == {os.path.basename(f2)}")
    else:
        print("None found.")
        
    print("\n--- PERCEPTUAL DUPLICATES ---")
    if near_dupes:
        for f1, f2 in near_dupes:
            print(f"{os.path.basename(f1)} ~~ {os.path.basename(f2)}")
    else:
        print("None found.")

if __name__ == "__main__":
    check_duplicates()
