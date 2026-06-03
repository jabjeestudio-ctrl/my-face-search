import streamlit as st
import cv2
import numpy as np
import faiss
import pickle
import insightface
from insightface.app import FaceAnalysis
import os

# แก้บรรทัดที่ 11 ใน app.py ให้เป็นแบบนี้ครับ
@st.cache_resource
def load_resources():
    if not os.path.exists("event.index"):
        st.error("ไม่พบไฟล์ event.index ในระบบ! กรุณาตรวจสอบการอัปโหลด")
        return None, None, None
        
    index = faiss.read_index("event.index")
    # ... (ส่วนที่เหลือเหมือนเดิม)

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
                # --- แก้บรรทัดนี้ให้ไปดึงรูปจากโฟลเดอร์ ---
                st.image(os.path.join("event_photos", image_paths[idx]))
                # ----------------------------------------
    else:
        st.warning("ไม่พบใบหน้าในรูป")
