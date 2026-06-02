import streamlit as st
import cv2
import numpy as np
import requests

# 1. ปรับการตั้งค่าเพื่อให้เว็บโหลดหน้าตาขึ้นมาก่อน
st.set_page_config(page_title="Photo Finder", layout="wide")

# 2. ฟังก์ชันดึงรูปที่ปลอดภัย (ใช้ Cache ช่วยให้ไม่โหลดซ้ำซ้อน)
@st.cache_resource
def get_face_cascade():
    return cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

face_cascade = get_face_cascade()

# 3. ตัวแปรเก็บรูป (ให้เป็น Global เฉพาะใน session)
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []
    st.session_state["scanned_file_ids"] = set()

# 4. ปุ่มค้นหา (วางไว้บนสุด แขกเห็นปุ๊บกดได้ทันที 0 วิ)
st.title("📸 ระบบสแกนใบหน้า")
uploaded_file = st.file_uploader("อัปโหลดรูปเพื่อค้นหา", type=["jpg", "png"])

# 5. ระบบหลังบ้านแบบเบาที่สุด (ค่อยๆ ดึงทีละนิด)
def background_sync():
    # จำกัดแค่ 5 รูปพอต่อการรีเฟรชหน้าเว็บครั้งเดียว เพื่อไม่ให้ค้าง
    GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
    GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents&key={GOOGLE_API_KEY}&fields=files(id)&pageSize=20"
    
    try:
        files = requests.get(url, timeout=2).json().get('files', [])
        for f in files:
            if f['id'] not in st.session_state["scanned_file_ids"]:
                # ถ้าเจอรูปใหม่ค่อยดึงรูปเดียวจบแล้วหยุดไว้ก่อน
                dl_url = f"https://www.googleapis.com/drive/v3/files/{f['id']}?alt=media&key={GOOGLE_API_KEY}"
                img_data = requests.get(dl_url, timeout=2).content
                img = cv2.imdecode(np.frombuffer(img_data, np.uint8), 1)
                
                if img is not None:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.2, 5)
                    if len(faces) > 0:
                        st.session_state["face_images_db"].append({"img": cv2.cvtColor(img, cv2.COLOR_BGR2RGB), "raw": img_data})
                
                st.session_state["scanned_file_ids"].add(f['id'])
                break # ดึงทีละรูปพอ ไม่ต้องรีบ
    except: pass

# รันดึงรูปเบื้องหลัง
background_sync()

# ส่วนแสดงผล...
if uploaded_file:
    st.info("กำลังค้นหา...")
    # ... โค้ดสแกนใบหน้าเดิม ...
