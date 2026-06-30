import os
import shutil
import random

os.makedirs('manual_test/unknown', exist_ok=True)

real_src = 'dataset/real'
screen_src = 'dataset/screen'

if os.path.exists(real_src) and os.path.exists(screen_src):
    real_images = [f for f in os.listdir(real_src) if f.endswith('.jpg') or f.endswith('.jpeg')]
    screen_images = [f for f in os.listdir(screen_src) if f.endswith('.jpg') or f.endswith('.jpeg')]
    
    selected_real = random.sample(real_images, 5)
    selected_screen = random.sample(screen_images, 5)
    
    for img in selected_real:
        shutil.copy(os.path.join(real_src, img), os.path.join('manual_test/unknown', f"real_{img}"))
        
    for img in selected_screen:
        shutil.copy(os.path.join(screen_src, img), os.path.join('manual_test/unknown', f"screen_{img}"))
        
    print("Copied random unseen ICL images to manual_test/unknown")
else:
    print("ICL dataset folders not found!")
