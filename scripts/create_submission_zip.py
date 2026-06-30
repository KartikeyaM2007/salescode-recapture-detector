import os
import zipfile

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_dir = os.path.join(base, "submission")
os.makedirs(out_dir, exist_ok=True)
zip_path = os.path.join(out_dir, "SalesCode_Recapture_Detector.zip")

# Files and directories to include
includes = [
    "predict.py",
    "features.py",
    "model.joblib",
    "model_metadata.json",
    "requirements.txt",
    "APPROACH.md",
    "README.md",
    "DATASET_SOURCES.md",
    "train.py",
    "scripts",
    "reports",
]

# Patterns to exclude
exclude_dirs = {"__pycache__", ".venv", "venv", "node_modules", ".git"}
exclude_exts = {".pyc", ".zip", ".tar", ".gz"}

def should_exclude(path):
    parts = path.replace("\\", "/").split("/")
    for part in parts:
        if part in exclude_dirs:
            return True
    _, ext = os.path.splitext(path)
    if ext in exclude_exts:
        return True
    return False

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for item in includes:
        full = os.path.join(base, item)
        if os.path.isfile(full):
            if not should_exclude(full):
                zf.write(full, item)
                print(f"  Added file: {item}")
        elif os.path.isdir(full):
            for root, dirs, files in os.walk(full):
                # Prune excluded dirs in-place
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                for file in files:
                    filepath = os.path.join(root, file)
                    if should_exclude(filepath):
                        continue
                    arcname = os.path.relpath(filepath, base)
                    zf.write(filepath, arcname)
                    print(f"  Added: {arcname}")

print(f"\nZIP created: {zip_path}")
print(f"ZIP size: {os.path.getsize(zip_path) / 1024 / 1024:.2f} MB")

# List contents
with zipfile.ZipFile(zip_path, 'r') as zf:
    names = zf.namelist()
    print(f"Total files: {len(names)}")
