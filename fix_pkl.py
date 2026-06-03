import os
import pickle

# เอาไฟล์ .pkl ออกจากเครื่องก่อน แล้วรันโค้ดนี้
folder = "event_photos"
image_paths = []

for filename in os.listdir(folder):
    if filename.endswith((".jpg", ".png")):
        # ใส่แค่ชื่อไฟล์เข้าไป ห้ามใส่ชื่อ folder
        image_paths.append(filename) 

with open("image_paths.pkl", "wb") as f:
    pickle.dump(image_paths, f)
print("สร้าง image_paths.pkl ใหม่แล้ว (เก็บแค่ชื่อไฟล์):", image_paths)