import os
import streamlit as st
import faiss
import pickle
from insightface.app import FaceAnalysis

@st.cache_resource
def load_resources():
    # บังคับให้หาไฟล์ในตำแหน่งที่สคริปต์ทำงานอยู่
    base_path = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(base_path, "event.index")
    pkl_path = os.path.join(base_path, "image_paths.pkl")
    
    index = faiss.read_index(index_path)
    with open(pkl_path, "rb") as f:
        image_paths = pickle.load(f)
        
    app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    return index, image_paths, app
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
