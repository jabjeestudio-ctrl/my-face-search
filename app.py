import streamlit as st
import face_recognition
import chromadb
import numpy as np
from PIL import Image
import os

# 1. ตั้งค่าระบบฐานข้อมูลในเครื่อง
chroma_client = chromadb.PersistentClient(path="my_vector_db")
collection = chroma_client.get_or_create_collection(name="gallery_faces")

IMAGE_STORE_DIR = "all_gallery_images"
if not os.path.exists(IMAGE_STORE_DIR):
    os.makedirs(IMAGE_STORE_DIR)

# 2. หน้าตาเว็บไซต์
st.set_page_config(page_title="ระบบสแกนใบหน้า", layout="wide")
st.title("🔍 ระบบค้นหาภาพถ่ายด้วยใบหน้า (เวอร์ชันปกติ)")

tab1, tab2 = st.tabs(["👤 สำหรับผู้ใช้งาน (สแกนหน้าค้นหา)", "⚙️ สำหรับแอดมิน (อัปโหลดรูปเข้าคลัง)"])

# แท็บที่ 1: ฝั่งผู้ใช้งาน
with tab1:
    st.header("อัปโหลดรูปหน้าตรงของคุณเพื่อค้นหา")
    user_file = st.file_uploader("เลือกรูปถ่ายหน้าชัดๆ", type=["jpg", "jpeg", "png"], key="user_search")
    
    if user_file is not None:
        user_img = Image.open(user_file)
        st.image(user_img, caption="รูปของคุณ", width=200)
        
        if st.button("🚀 เริ่มสแกนค้นหาภาพ"):
            image_np = np.array(user_img.convert('RGB'))
            user_encodings = face_recognition.face_encodings(image_np)
            
            if len(user_encodings) > 0:
                my_face_vector = user_encodings[0].tolist()
                
                with st.spinner("🔍 กำลังค้นหาใบหน้าที่คล้ายกัน..."):
                    results = collection.query(query_embeddings=[my_face_vector], n_results=10)
                
                found_paths = []
                if results['distances'] and len(results['distances'][0]) > 0:
                    for dist, metadata in zip(results['distances'][0], results['metadatas'][0]):
                        if dist < 0.4:  
                            found_paths.append(metadata['file_path'])
                
                found_paths = list(set(found_paths))
                
                if len(found_paths) > 0:
                    st.success(f"🎉 เจอรูปภาพของคุณทั้งหมด {len(found_paths)} รูป")
                    cols = st.columns(3)
                    for idx, path in enumerate(found_paths):
                        with cols[idx % 3]:
                            if os.path.exists(path):
                                st.image(path, use_container_width=True)
                else:
                    st.warning("😔 ไม่พบรูปภาพของคุณในคลังระบบเลย")
            else:
                st.error("❌ AI มองไม่เห็นใบหน้า กรุณาเปลี่ยนรูปใหม่ครับ")

# แท็บที่ 2: ฝั่งแอดมิน
with tab2:
    st.header("อัปโหลดรูปภาพทั้งหมดเข้าสู่ระบบ")
    gallery_files = st.file_uploader("เลือกรูปภาพคลังภาพ (เลือกพร้อมกันได้หลายรูป)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="admin_upload")
    
    if st.button("📤 บันทึกรูปภาพทั้งหมดเข้าสมองกล AI"):
        if gallery_files:
            face_counter = 0
            progress_bar = st.progress(0)
            
            for index, uploaded_file in enumerate(gallery_files):
                save_path = os.path.join(IMAGE_STORE_DIR, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                check_id = f"{uploaded_file.name}_face_0"
                existing = collection.get(ids=[check_id])
                
                if len(existing['ids']) == 0:
                    try:
                        img_data = face_recognition.load_image_file(save_path)
                        face_locations = face_recognition.face_locations(img_data)
                        face_encodings = face_recognition.face_encodings(img_data, face_locations)
                        
                        for i, encoding in enumerate(face_encodings):
                            face_unique_id = f"{uploaded_file.name}_face_{i}"
                            collection.add(
                                embeddings=[encoding.tolist()],
                                metadatas=[{"file_path": save_path}],
                                ids=[face_unique_id]
                            )
                            face_counter += 1
                    except:
                        pass
                progress_bar.progress((index + 1) / len(gallery_files))
            st.success(f"✅ บันทึกใบหน้าใหม่สำเร็จ {face_counter} ใบหน้า")
        else:
            st.error("❌ กรุณาเลือกไฟล์รูปภาพก่อนกดปุ่มครับ")