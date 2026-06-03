import cv2
import numpy as np
import faiss
import os
import pickle
from insightface.app import FaceAnalysis

# เตรียมโมเดล AI
app = FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

image_paths = []
embeddings = []

# สแกนรูปในโฟลเดอร์ event_photos
folder = "event_photos"
print(f"กำลังสแกนรูปในโฟลเดอร์ {folder}...")

for filename in os.listdir(folder):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        img_path = os.path.join(folder, filename)
        img = cv2.imread(img_path)
        if img is None: continue
        
        faces = app.get(img)
        for face in faces:
            embeddings.append(face.normed_embedding)
            image_paths.append(os.path.basename(img_path)

if embeddings:
    embeddings = np.array(embeddings, dtype='float32')
    index = faiss.IndexFlatIP(512)
    index.add(embeddings)

    faiss.write_index(index, "event.index")
    with open("image_paths.pkl", "wb") as f:
        pickle.dump(image_paths, f)
    print("สร้างไฟล์ event.index และ image_paths.pkl สำเร็จแล้ว!")
else:
    print("ไม่พบใบหน้าในรูปภาพ กรุณาตรวจสอบโฟลเดอร์ event_photos")
