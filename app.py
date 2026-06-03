import streamlit as st
import cv2
import numpy as np
import faiss
import pickle
import insightface
from insightface.app import FaceAnalysis
import os

# --- ส่วนที่ต้องแก้/วางทับ ---
@st.cache_resource
def load_resources():
    # บังคับหาไฟล์ในโฟลเดอร์ปัจจุบันที่โปรแกรมทำงานอยู่
    index_path = os.path.join(os.getcwd(), "event.index")
    pkl_path = os.path.join(os.getcwd(), "image_paths.pkl")
    
    # ถ้าหาไฟล์ไม่เจอ ให้แจ้ง Error ในหน้าเว็บทันที ไม่ให้แอปค้าง
    if not os.path.exists(index_path) or not os.path.exists(pkl_path):
        st.error(f"ไม่พบไฟล์ระบบ! ตรวจสอบว่ามีไฟล์ event.index และ image_paths.pkl ใน GitHub หรือยัง")
        return None, None, None

    index = faiss.read_index(index_path)
    with open(pkl_path, "rb") as f:
        image_paths = pickle.load(f)
    
    app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    return index, image_paths, app
# ---------------------------

# เรียกใช้งานฟังก์ชัน
index, image_paths, app = load_resources()

# ตรวจสอบก่อนรันส่วนถัดไป
if index is not None:
    st.title("ระบบสแกนใบหน้าค้นหารูป")
    uploaded_file = st.file_uploader("อัปโหลดรูปของคุณ", type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img_guest = cv2.imdecode(file_bytes, 1)
        
        faces = app.get(img_guest)
        if faces:
            guest_emb = faces[0].normed_embedding.reshape(1, -1)
            distances, indices = index.search(guest_emb.astype('float32'), k=5)
            
            st.success("พบรูปที่ใกล้เคียงกับคุณ:")
            for idx in indices[0]:
                if idx != -1:
                    # ดึงชื่อไฟล์มาแสดงผลจากโฟลเดอร์ event_photos
                    st.image(os.path.join("event_photos", image_paths[idx]))
        else:
            st.warning("ไม่พบใบหน้าในรูป")
