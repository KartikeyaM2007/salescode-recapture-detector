import os
import shutil

os.makedirs('manual_test/unknown/real', exist_ok=True)
os.makedirs('manual_test/unknown/screen', exist_ok=True)

brain_dir = r"C:\Users\USER\.gemini\antigravity-ide\brain\e6ca1744-1e1f-4043-b567-ff9fefaf44be"

files = {
    'selfie_person_1782829299972.png': 'real/selfie.png',
    'room_1782829339573.png': 'real/room.png',
    'books_1782829349811.png': 'real/books.png',
    'flower_1782829361666.png': 'real/flower.png',
    'outdoor_1782829373383.png': 'real/outdoor.png',
    'laptop_screen_1782829390369.png': 'screen/laptop.png'
}

for src, dst in files.items():
    src_path = os.path.join(brain_dir, src)
    if os.path.exists(src_path):
        shutil.copy(src_path, os.path.join('manual_test/unknown', dst))
        print(f"Copied {src} to {dst}")
