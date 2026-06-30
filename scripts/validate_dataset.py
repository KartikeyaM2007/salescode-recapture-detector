import os
import glob
import hashlib
from PIL import Image

DATASET_ROOT = os.path.join(os.path.dirname(__file__), '..', 'dataset')
REAL_DIR = os.path.join(DATASET_ROOT, 'real')
SCREEN_DIR = os.path.join(DATASET_ROOT, 'screen')

def hash_file(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def validate_dataset():
    print("Validating dataset...")
    
    real_images = glob.glob(os.path.join(REAL_DIR, '*.*'))
    screen_images = glob.glob(os.path.join(SCREEN_DIR, '*.*'))
    
    all_images = real_images + screen_images
    
    print(f"Real images found: {len(real_images)}")
    print(f"Screen images found: {len(screen_images)}")
    print(f"Total images: {len(all_images)}")
    
    if len(all_images) == 0:
        print("Dataset is empty. Exiting.")
        return

    print("Class balance:")
    print(f"  Real: {len(real_images) / len(all_images) * 100:.2f}%")
    print(f"  Screen: {len(screen_images) / len(all_images) * 100:.2f}%")

    extensions = {}
    corrupted = 0
    hashes = set()
    duplicates = 0
    widths = []
    heights = []

    for img_path in all_images:
        ext = os.path.splitext(img_path)[1].lower()
        extensions[ext] = extensions.get(ext, 0) + 1
        
        try:
            with Image.open(img_path) as img:
                img.verify()
            # reopen to get size since verify() might close/invalidate state
            with Image.open(img_path) as img:
                w, h = img.size
                widths.append(w)
                heights.append(h)
                
            hsh = hash_file(img_path)
            if hsh in hashes:
                duplicates += 1
            hashes.add(hsh)
                
        except Exception:
            corrupted += 1

    print("\nExtensions distribution:")
    for ext, count in extensions.items():
        print(f"  {ext}: {count}")
        
    print(f"\nCorrupted/Unreadable images: {corrupted}")
    print(f"Duplicate hashes found (across entire dataset): {duplicates}")
    
    if len(widths) > 0:
        print(f"\nResolution stats:")
        print(f"  Width : min={min(widths)}, max={max(widths)}, avg={sum(widths)/len(widths):.1f}")
        print(f"  Height: min={min(heights)}, max={max(heights)}, avg={sum(heights)/len(heights):.1f}")
        
    print("\nValidation complete.")

if __name__ == "__main__":
    validate_dataset()
