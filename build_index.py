import cv2
import numpy as np
import faiss
import os
import pickle
from insightface.app import FaceAnalysis

# ตั้งค่า AI
app = FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

# เตรียมฐานข้อมูล
image_paths = []
embeddings = []

print("กำลังสแกนรูปในงาน...")
for filename in os.listdir("event_photos"):
    if filename.endswith((".jpg", ".png")):
        img_path = os.path.join("event_photos", filename)
        img = cv2.imread(img_path)
        faces = app.get(img)
        for face in faces:
            embeddings.append(face.normed_embedding)
            image_paths.append(img_path)

# สร้าง Index ด้วย FAISS
embeddings = np.array(embeddings, dtype='float32')
index = faiss.IndexFlatIP(512) # 512 คือขนาดของ vector ใบหน้า
index.add(embeddings)

# บันทึกข้อมูลลงไฟล์
faiss.write_index(index, "event.index")
with open("image_paths.pkl", "wb") as f:
    pickle.dump(image_paths, f)

print("สร้าง Index เสร็จสิ้น!")