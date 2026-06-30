import requests

img_path = 'dataset/my_photos/real/WhatsApp Image 2026-06-30 at 4.09.45 PM.jpeg'
with open(img_path, 'rb') as f:
    r = requests.post('http://127.0.0.1:8000/predict', files={'file': ('test.jpeg', f, 'image/jpeg')})
    d = r.json()
    print("Backend score:", d["score"])
    print("Backend threshold:", d["threshold"])
    print("Backend model_type:", d["model_type"])
    print("Backend rule_boost_total:", d["rule_boost_total"])
    print("Backend raw_model_score:", d["raw_model_score"])
