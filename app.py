import streamlit as st
import cv2
import numpy as np
import os

# ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง
st.set_page_config(page_title="Photo Finder System", layout="wide")

st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายในงาน (เวอร์ชันคลังรูป GitHub)")
st.write("👇 แขกอัปโหลดรูปตัวเอง เพื่อค้นหารูปทั้งหมดในงาน สามารถกดดาวน์โหลดหรือแชร์เข้า LINE ได้ทันที")

# โหลดตัวตรวจจับใบหน้ามาตรฐานของ OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ใช้ Session State ในการจำข้อมูลใบหน้าและรูปภาพเต็ม
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []

# ฟังก์ชันอ่านรูปภาพทั้งหมดจากโฟลเดอร์ photos ในโปรเจกต์อัตโนมัติ
def load_photos_from_local_folder():
    folder_path = "photos"
    # เคลียร์คลังเก่าเพื่อความอัปเดตสดใหม่เวลาเพิ่มรูป
    st.session_state["face_images_db"] = []
    
    if not os.path.exists(folder_path):
        return 0
        
    success_img_count = 0
    # วิ่งไล่อ่านทุกไฟล์ในโฟลเดอร์ photos
    for idx, file_name in enumerate(os.listdir(folder_path)):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, "rb") as f:
                    raw_bytes = f.read()
                
                file_bytes = np.asarray(bytearray(raw_bytes), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, 1)
                
                if image is not None:
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    
                    if len(faces) > 0:
                        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        img_id = f"local_{file_name}_{idx}"
                        
                        for (x, y, w, h) in faces:
                            face_roi = gray[y:y+h, x:x+w]
                            face_resized = cv2.resize(face_roi, (32, 32)).tolist()
                            
                            st.session_state["face_images_db"].append({
                                "feat": face_resized,
                                "img": image_rgb,
                                "img_id": img_id,
                                "raw_bytes": raw_bytes
                            })
                        success_img_count += 1
            except:
                continue
    return success_img_count

# 🔄 รันระบบดึงรูปจากโฟลเดอร์ขึ้นระบบอัตโนมัติทันที
total_photos = load_photos_from_local_folder()

# สร้างเมนูฝั่งซ้ายมือ (Sidebar)
st.sidebar.header("⚙️ เมนูการใช้งาน")
st.sidebar.info(f"📊 จำนวนรูปภาพในคลังตอนนี้: {total_photos} รูป")
st.sidebar.write("💡 วิธีเพิ่มรูปหน้างาน: แค่กดอัปโหลดรูปภาพเข้าไปในโฟลเดอร์ `photos` บน GitHub ของน้าได้เลยครับ ระบบจะอัปเดตเองทันที!")

# --- หน้าหลักค้นหาใบหน้า ---
if total_photos == 0:
    st.warning("⚠️ คลังรูปภาพในโฟลเดอร์ `photos` ยังว่างอยู่ครับ (กรุณาอัปโหลดไฟล์รูปภาพเข้าไปในโฟลเดอร์ photos บน GitHub ก่อนครับน้า)")
else:
    uploaded_file = st.file_uploader("อัปโหลดรูปภาพใบหน้าของคุณเพื่อค้นหารูปทั้งหมดในงาน", type=["jpg", "jpeg", "png"], key="search_photo")
    
    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            st.error("❌ ไม่พบใบหน้าในรูปภาพที่ส่งมา กรุณาใช้รูปที่เห็นหน้าตรงชัดเจนครับ")
        else:
            x, y, w, h = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_roi, (32, 32)).tolist()
            
            matched_items = []
            seen_images = set()
            
            for item in st.session_state["face_images_db"]:
                diff = np.sum(np.abs(np.array(item["feat"]) - np.array(face_resized)))
                
                if diff < 38000:  # เกณฑ์แม่นยำสูงตรงปก
                    if item["img_id"] not in seen_images:
                        matched_items.append(item)
                        seen_images.add(item["img_id"])
            
            # --- แสดงผลลัพธ์ ---
            if len(matched_items) > 0:
                st.success(f"🎉 เจอรูปถ่ายของคุณในระบบทั้งหมด {len(matched_items)} รูปครับ! 👇")
                
                cols = st.columns(2)
                for idx, item in enumerate(matched_items):
                    with cols[idx % 2]:
                        st.image(item["img"], caption=f"รูปที่ {idx + 1} (ชัดเต็มพิกเซล)", use_container_width=True)
                        
                        st.download_button(
                            label=f"📥 ดาวน์โหลดรูปที่ {idx + 1}",
                            data=item["raw_bytes"],
                            file_name=f"event_photo_{idx+1}.jpg",
                            mime="image/jpeg",
                            key=f"dl_{idx}"
                        )
                        
                        line_share_url = "https://social-plugins.line.me/lineit/share?url=" + "https://yiday4hy.streamlit.app"
                        st.markdown(f'<a href="{line_share_url}" target="_blank"><button style="background-color:#06C755; color:white; border:none; padding:8px 16px; border-radius:4px; cursor:pointer; width:100%; font-weight:bold;">🟢 ส่งต่อ / แชร์เว็บเข้า LINE</button></a>', unsafe_allow_html=True)
                        st.write("") 
            else:
                st.error("❌ ไม่พบรูปภาพที่ตรงกับใบหน้าของคุณในคลังภาพ")
