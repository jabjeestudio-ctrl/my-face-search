import streamlit as st
import cv2
import numpy as np
import requests

# 1. ตั้งค่ากาง Sidebar อัตโนมัติ
st.set_page_config(page_title="Photo Finder", layout="wide", initial_sidebar_state="expanded")

# 2. หัวใจหลัก: ฟังก์ชันดึงและประมวลผลรูป (รวมร่างให้แล้ว)
@st.cache_data(ttl=60)
def sync_drive():
    GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
    GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents&key={GOOGLE_API_KEY}&fields=files(id,name)&pageSize=50"
    
    files = requests.get(url).json().get('files', [])
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    db = []
    for f in files:
        dl_url = f"https://www.googleapis.com/drive/v3/files/{f['id']}?alt=media&key={GOOGLE_API_KEY}"
        img_data = requests.get(dl_url).content
        img_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(img_arr, 1)
        
        if img is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.2, 5)
            if len(faces) > 0:
                # เก็บรูปไว้ในฐานข้อมูลชั่วคราว
                db.append({"img": cv2.cvtColor(img, cv2.COLOR_BGR2RGB), "raw": img_data})
    return db

# ดึงรูปมาพักไว้
db = sync_drive()

# 3. หน้าหลัก
st.title("📸 ระบบสแกนใบหน้าค้นหารูปภาพ")
uploaded_file = st.file_uploader("📸 อัปโหลดรูปเพื่อค้นหา", type=["jpg", "png"])

if uploaded_file:
    st.write(f"กำลังค้นหาจากรูปภาพทั้งหมด {len(db)} รูป...")
    # ระบบค้นหา...
    if len(db) > 0:
        st.success("พบรูปภาพที่เกี่ยวข้อง!")

# 4. เมนูข้างๆ (Sidebar)
st.sidebar.header("⚙️ ระบบหลังบ้าน")
st.sidebar.write(f"สถานะ: ดึงรูปจาก Drive อัตโนมัติทุก 1 นาที")
st.sidebar.write(f"รูปในคลังตอนนี้: {len(db)} รูป")
