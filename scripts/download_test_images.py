import os
import requests

os.makedirs('manual_test/unknown/real', exist_ok=True)
os.makedirs('manual_test/unknown/screen', exist_ok=True)

images = {
    'real/selfie.jpg': 'https://upload.wikimedia.org/wikipedia/commons/a/a0/Selfie_stick_at_the_Taj_Mahal.jpg',
    'real/room.jpg': 'https://upload.wikimedia.org/wikipedia/commons/4/41/Room_in_a_house.jpg',
    'real/books.jpg': 'https://upload.wikimedia.org/wikipedia/commons/e/e0/Stack_of_books.jpg',
    'real/flower.jpg': 'https://upload.wikimedia.org/wikipedia/commons/a/a5/Flower_poster_2.jpg',
    'real/outdoor.jpg': 'https://upload.wikimedia.org/wikipedia/commons/1/1a/Bachalpseeflowers.jpg',
    'screen/laptop_screen.jpg': 'https://upload.wikimedia.org/wikipedia/commons/8/82/MacBook_Pro_13%E2%80%B3_Late_2011_Screen.jpg',
    'screen/monitor_bezel.jpg': 'https://upload.wikimedia.org/wikipedia/commons/c/cd/LCD_monitor.jpg',
    'screen/printout.jpg': 'https://upload.wikimedia.org/wikipedia/commons/5/52/Printed_page.jpg',
    'screen/screen_no_bezel.jpg': 'https://upload.wikimedia.org/wikipedia/commons/b/b3/Pixels_in_a_TFT_screen.jpg'
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for name, url in images.items():
    try:
        path = os.path.join('manual_test/unknown', name)
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                f.write(r.content)
            print(f"Downloaded {name}")
        else:
            print(f"Failed to download {name}: Status {r.status_code}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
