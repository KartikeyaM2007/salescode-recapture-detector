import os
import urllib.request
import zipfile
import glob
import csv
import hashlib
import sys
from tqdm import tqdm
import argparse

# Config
DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "dataset")
RAW_DIR = os.path.join(DATASET_DIR, "raw", "icl")
REAL_DIR = os.path.join(DATASET_DIR, "real")
SCREEN_DIR = os.path.join(DATASET_DIR, "screen")
MANIFEST_FILE = os.path.join(DATASET_DIR, "dataset_manifest.csv")

# ICL Dataset URLs
FULL_SINGLE_URL = "https://www.commsp.ee.ic.ac.uk/~pld/research/Rewind/Recapture/TestImages/SingleCaptureImages.zip"
FULL_RECAP_URL = "https://www.commsp.ee.ic.ac.uk/~pld/research/Rewind/Recapture/TestImages/RecapturedImages.zip"
SAMPLE_URL = "https://www.commsp.ee.ic.ac.uk/~tt1410/experiments/recapturedetection/resources/SubjectiveTestImages.zip"

def setup_dirs():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(REAL_DIR, exist_ok=True)
    os.makedirs(SCREEN_DIR, exist_ok=True)

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_file(url, dest):
    if os.path.exists(dest):
        print(f"Skipping download, file exists: {dest}")
        return
    print(f"Downloading {url}...")
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, dest, reporthook=t.update_to)

def extract_zip(zip_path, extract_to):
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def hash_file_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as afile:
        buf = afile.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(65536)
    return hasher.hexdigest()

def get_image_info(filepath):
    """Returns (is_valid, width, height)."""
    try:
        from PIL import Image
        with Image.open(filepath) as img:
            img.verify()  # verify checks for corruption without reading the whole file
        # To get size we might need to reopen if verify() messes up state in some older PIL versions
        with Image.open(filepath) as img:
            img.load() # full check
            width, height = img.size
        return True, width, height
    except Exception:
        return False, 0, 0

def process_images():
    manifest_data = []
    seen_hashes = set()
    
    print("Processing Images into real/screen folders...")
    
    # Optional label map for subjective images if present
    labels_map = {}
    for labels_file in glob.glob(os.path.join(RAW_DIR, '**', 'labels.txt'), recursive=True):
        try:
            with open(labels_file, 'r') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        filename = parts[0]
                        label_str = parts[1].strip().lower()
                        if label_str == "original captured":
                            labels_map[filename] = "real"
                        elif label_str == "recaptured":
                            labels_map[filename] = "screen"
        except Exception as e:
            print(f"Warning: Could not read labels file {labels_file}: {e}")
        
    all_files = glob.glob(os.path.join(RAW_DIR, '**', '*.*'), recursive=True)
    
    for filepath in tqdm(all_files):
        filepath_lower = filepath.lower()
        if not (filepath_lower.endswith('.jpg') or filepath_lower.endswith('.jpeg') or filepath_lower.endswith('.png') or filepath_lower.endswith('.bmp') or filepath_lower.endswith('.tif') or filepath_lower.endswith('.tiff')):
            continue
            
        filename = os.path.basename(filepath)
        
        # Determine label based on directory or filename
        label = None
        if filename in labels_map:
            label = labels_map[filename]
        elif "singlecaptureimages" in filepath_lower:
            label = "real"
        elif "recapturedimages" in filepath_lower:
            label = "screen"
        elif "single" in filename.lower() or "original" in filename.lower():
            label = "real"
        elif "recaptured" in filename.lower() or "rc" in filename.lower():
            label = "screen"
            
        if not label:
            continue
            
        dest_dir = REAL_DIR if label == "real" else SCREEN_DIR
                
        is_valid, width, height = get_image_info(filepath)
        if not is_valid:
            continue
            
        file_hash = hash_file_sha256(filepath)
        if file_hash in seen_hashes:
            continue
            
        seen_hashes.add(file_hash)
        
        dest_path = os.path.join(dest_dir, filename)
        
        # Resolve conflicts
        counter = 1
        base_name, ext = os.path.splitext(filename)
        while os.path.exists(dest_path):
            dest_path = os.path.join(dest_dir, f"{base_name}_{counter}{ext}")
            counter += 1
            
        # Copy file
        with open(filepath, 'rb') as f_src:
            with open(dest_path, 'wb') as f_dst:
                f_dst.write(f_src.read())
                
        manifest_data.append({
            "filepath": dest_path,
            "label": label,
            "original_source_path": filepath,
            "source_dataset": "ICL_Dataset",
            "source_url": "",
            "license_or_usage_note": "Academic use only",
            "width": width,
            "height": height,
            "sha256": file_hash
        })

    # Save manifest
    with open(MANIFEST_FILE, 'w', newline='', encoding='utf-8') as csvf:
        fieldnames = ["filepath", "label", "original_source_path", "source_dataset", "source_url", "license_or_usage_note", "width", "height", "sha256"]
        writer = csv.DictWriter(csvf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_data)
        
    print(f"Manifest saved to {MANIFEST_FILE}")
    
    # Print counts
    real_count = len([x for x in manifest_data if x["label"] == "real"])
    screen_count = len([x for x in manifest_data if x["label"] == "screen"])
    print(f"Final counts -> Real: {real_count}, Screen: {screen_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and prepare the ICL dataset.")
    parser.add_argument("--mode", type=str, choices=["sample", "full-icl", "manual", "local"], default="manual", help="Which mode to run.")
    parser.add_argument("--local-dir", type=str, help="Directory containing the local ZIP files for --mode local")
    args = parser.parse_args()

    setup_dirs()

    if args.mode == "local":
        if not args.local_dir:
            print("ERROR: --local-dir must be provided for --mode local.")
            sys.exit(1)
            
        single_zip = os.path.join(args.local_dir, "SingleCaptureImages.zip")
        recap_zip = os.path.join(args.local_dir, "RecapturedImages.zip")
        
        if not os.path.exists(single_zip) or not os.path.exists(recap_zip):
            print(f"ERROR: Local ZIP files not found in {args.local_dir}.")
            print(f"Expected: \n - {single_zip}\n - {recap_zip}")
            sys.exit(1)
            
        print(f"Found local ZIP files in {args.local_dir}. Proceeding with extraction.")
        extract_zip(single_zip, os.path.join(RAW_DIR, "SingleCaptureImages"))
        extract_zip(recap_zip, os.path.join(RAW_DIR, "RecapturedImages"))
        process_images()
        
    elif args.mode == "sample":
        print("Running in SAMPLE mode (66MB). This is for pipeline validation only.")
        sample_zip = os.path.join(os.path.dirname(RAW_DIR), "SubjectiveTestImages.zip")
        download_file(SAMPLE_URL, sample_zip)
        extract_zip(sample_zip, os.path.join(RAW_DIR, "SubjectiveTestImages"))
        process_images()
        
    elif args.mode == "full-icl":
        print("WARNING: Running in FULL-ICL mode. This will download ~8GB of data.")
        single_zip = os.path.join(os.path.dirname(RAW_DIR), "SingleCaptureImages.zip")
        recap_zip = os.path.join(os.path.dirname(RAW_DIR), "RecapturedImages.zip")
        download_file(FULL_SINGLE_URL, single_zip)
        download_file(FULL_RECAP_URL, recap_zip)
        extract_zip(single_zip, os.path.join(RAW_DIR, "SingleCaptureImages"))
        extract_zip(recap_zip, os.path.join(RAW_DIR, "RecapturedImages"))
        process_images()
        
    elif args.mode == "manual":
        print("Running in MANUAL mode. Place your own images directly in dataset/real/ and dataset/screen/.")
        print(f"Folders created at: {REAL_DIR} and {SCREEN_DIR}")
