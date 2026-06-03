import cv2
import numpy as np
import faiss
import os
import pickle
from insightface.app import FaceAnalysis

app = FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

image_paths = []
embeddings = []

folder = "event_photos"
for filename in os.listdir(folder):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        img_path = os.path.join(folder, filename)
        img = cv2.imread(img_path)
        if img is None: continue
        
        faces = app.get(img)
        for face in faces:
            embeddings.append(face.normed_embedding)
            # ตัดโฟลเดอร์ทิ้ง ให้เหลือแค่ชื่อไฟล์ (เช่น '1.jpg')
            image_paths.append(filename) 

if embeddings:
    embeddings = np.array(embeddings, dtype='float32')
    index = faiss.IndexFlatIP(512)
    index.add(embeddings)
    faiss.write_index(index, "event.index")
    with open("image_paths.pkl", "wb") as f:
        pickle.dump(image_paths, f)
    print("สร้างไฟล์ใหม่สำเร็จ!")