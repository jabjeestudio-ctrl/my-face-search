import streamlit as st
import cv2
import numpy as np
import requests

st.set_page_config(page_title="Photo Finder", layout="wide")

# ตั้งค่า ID ของคุณ
FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

st.title("📸 ค้นหารูปถ่ายของคุณในงาน")

# เก็บรูปไว้ในหน่วยความจำ
if "db" not in st.session_state: st.session_state.db = []

# 1. หลังบ้าน: ดึงรูปจาก Drive (กดปุ่มเดียวพอ)
if st.sidebar.button("ดึงรูปจาก Google Drive"):
    url = f"https://www.googleapis.com/drive/v3/files?q='{FOLDER_ID}'+in+parents&key={API_KEY}"
    files = requests.get(url).json().get('files', [])
    st.session_state.db = []
    with st.spinner("กำลังดึงข้อมูล..."):
        for f in files:
            img_url = f"https://www.googleapis.com/drive/v3/files/{f['id']}?alt=media&key={API_KEY}"
            img_data = requests.get(img_url).content
            img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                st.session_state.db.append({"img": img, "raw": img_data})
    st.sidebar.success(f"ดึงรูปเสร็จแล้ว {len(st.session_state.db)} รูป")

# 2. หน้าบ้าน: แขกอัปโหลดรูป
uploaded = st.file_uploader("อัปโหลดรูปใบหน้าของคุณ", type=["jpg", "png"])

if uploaded and st.session_state.db:
    user_img = cv2.imdecode(np.frombuffer(uploaded.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
    
    st.write("ระบบกำลังค้นหา...")
    found = False
    for item in st.session_state.db:
        gray = cv2.cvtColor(item["img"], cv2.COLOR_BGR2GRAY)
        # ตรวจจับใบหน้า
        if len(face_cascade.detectMultiScale(gray, 1.1, 4)) > 0:
            st.image(item["img"], caption="เจอรูปนี้ในงาน!")
            st.download_button("ดาวน์โหลดรูปนี้", item["raw"], "my_photo.jpg")
            found = True
    if not found: st.error("ไม่พบรูปที่ตรงกัน")
elif uploaded and not st.session_state.db:
    st.error("กดปุ่ม 'ดึงรูปจาก Google Drive' ที่เมนูด้านซ้ายก่อนครับ")
