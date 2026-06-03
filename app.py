import streamlit as st
import cv2
import numpy as np
import faiss
import pickle
from insightface.app import FaceAnalysis

# 1. โหลด Index และ Model (ทำครั้งเดียวตอนเปิดเว็บ)
@st.cache_resource
def load_resources():
    index = faiss.read_index("event.index")
    with open("image_paths.pkl", "rb") as f:
        image_paths = pickle.load(f)
    app = FaceAnalysis(providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    return index, image_paths, app

index, image_paths, app = load_resources()

st.title("ระบบค้นหารูปงานอีเวนต์ด้วยใบหน้า")
uploaded_file = st.file_uploader("อัปโหลดรูปหน้าของคุณ", type=['jpg', 'jpeg', 'png'])

# 2. กระบวนการค้นหาเมื่อแขกอัปโหลดรูป
if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img_guest = cv2.imdecode(file_bytes, 1)
    
    # สแกนหาใบหน้าแขก
    guest_faces = app.get(img_guest)
    
    if guest_faces:
        # ดึงค่าใบหน้าแขก
        guest_emb = guest_faces[0].normed_embedding.reshape(1, -1)
        
        # ค้นหาใน Index (หา 5 รูปที่ใกล้เคียงที่สุด)
        distances, indices = index.search(guest_emb.astype('float32'), k=5)
        
        st.success("พบรูปภาพที่ใกล้เคียงกับคุณ:")
        
        # แสดงรูปภาพ
        for idx in indices[0]:
            if idx != -1:
                st.image(image_paths[idx], caption="รูปที่พบในงาน")
    else:
        st.warning("ไม่พบใบหน้าในรูป กรุณาลองใหม่")