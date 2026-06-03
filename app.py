import streamlit as st
import cv2
import numpy as np
import faiss
import pickle
from insightface.app import FaceAnalysis
import os

@st.cache_resource
def load_resources():
    # โหลดไฟล์ Index และ Path จากตำแหน่งที่แอปทำงานอยู่
    index = faiss.read_index("event.index")
    with open("image_paths.pkl", "rb") as f:
        image_paths = pickle.load(f)
    
    app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    return index, image_paths, app

index, image_paths, app = load_resources()

st.title("ระบบสแกนใบหน้าค้นหารูป")
uploaded_file = st.file_uploader("อัปโหลดรูปของคุณ", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img_guest = cv2.imdecode(file_bytes, 1)
    
    guest_faces = app.get(img_guest)
    if guest_faces:
        # ใช้ embedding จากรูปที่อัปโหลด
        guest_emb = guest_faces[0].normed_embedding.reshape(1, -1)
        distances, indices = index.search(guest_emb.astype('float32'), k=5)
        
        # --- แก้ไขส่วนการแสดงผลรูป (ลูป for idx in indices[0]:) ---
        st.success("พบรูปที่ใกล้เคียงกับคุณ:")
        for idx in indices[0]:
            if idx != -1:
                # ไม่ต้อง join แล้ว! อ่านชื่อไฟล์ตรงๆ จาก list
                file_name = image_paths[idx] 
                
                # เช็คว่าไฟล์มีอยู่จริงไหม (ในโฟลเดอร์ที่ app.py รันอยู่)
                if os.path.exists(file_name):
                    img_to_show = cv2.imread(file_name)
                    if img_to_show is not None:
                        img_to_show = cv2.cvtColor(img_to_show, cv2.COLOR_BGR2RGB)
                        st.image(img_to_show, use_container_width=True)
                    else:
                        st.error(f"ไฟล์เสีย: {file_name}")
                else:
                    # ถ้ายังแดง ให้มันโชว์ชื่อไฟล์ที่มันหาออกมาให้เห็นชัดๆ เลยครับ
                    st.error(f"หาไฟล์ชื่อ '{file_name}' ไม่เจอใน GitHub!")
