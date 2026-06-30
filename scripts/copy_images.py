import os
import shutil
import argparse

os.makedirs('manual_test/unknown/real', exist_ok=True)
os.makedirs('manual_test/unknown/screen', exist_ok=True)

parser = argparse.ArgumentParser(description="Copy local manual test images into manual_test/unknown.")
parser.add_argument(
    "source_dir",
    nargs="?",
    default=os.environ.get("SALES_CODE_SOURCE_IMAGE_DIR", ""),
    help="Directory containing the source images, or set SALES_CODE_SOURCE_IMAGE_DIR.",
)
args = parser.parse_args()

source_dir = args.source_dir
if not source_dir:
    raise SystemExit("Provide source_dir or set SALES_CODE_SOURCE_IMAGE_DIR.")

files = {
    'selfie_person_1782829299972.png': 'real/selfie.png',
    'room_1782829339573.png': 'real/room.png',
    'books_1782829349811.png': 'real/books.png',
    'flower_1782829361666.png': 'real/flower.png',
    'outdoor_1782829373383.png': 'real/outdoor.png',
    'laptop_screen_1782829390369.png': 'screen/laptop.png'
}

for src, dst in files.items():
    src_path = os.path.join(source_dir, src)
    if os.path.exists(src_path):
        shutil.copy(src_path, os.path.join('manual_test/unknown', dst))
        print(f"Copied {src} to {dst}")
