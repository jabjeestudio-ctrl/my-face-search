import streamlit as st
import cv2
import numpy as np
import faiss
import pickle
from insightface.app import FaceAnalysis
import os

@st.cache_resource
def load_resources():
    index = faiss.read_index("event.index")
    with open("image_paths.pkl", "rb") as f:
        image_paths = pickle.load(f)
    app = FaceAnalysis(providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    return index, image_paths, app

index, image_paths, app = load_resources()

st.title("ระบบสแกนใบหน้า")
uploaded_file = st.file_uploader("อัปโหลดรูป", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img_guest = cv2.imdecode(file_bytes, 1)
    
    guest_faces = app.get(img_guest)
    if guest_faces:
        guest_emb = guest_faces[0].normed_embedding.reshape(1, -1)
        distances, indices = index.search(guest_emb.astype('float32'), k=5)
        
        for idx in indices[0]:
            if idx != -1:
                file_name = image_paths[idx] 
                # นี่คือจุดที่แก้: บังคับเอาชื่อไฟล์มาต่อกับ folder ตรงนี้
                file_path = os.path.join("event_photos", file_name)
                
                if os.path.exists(file_path):
                    img = cv2.imread(file_path)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    st.image(img, use_container_width=True)
                else:
                    st.error(f"หาไฟล์ไม่เจอที่: {file_path}")