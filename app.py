import streamlit as st
import cv2
import numpy as np
import requests

st.set_page_config(page_title="Photo Finder", layout="wide")
FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ระบบดึงและเก็บรูป
if "processed_images" not in st.session_state:
    st.session_state.processed_images = []

st.title("📸 ระบบค้นหารูปอัตโนมัติ")

# หลังบ้าน: ดึงรูป (กดครั้งเดียวพอ)
if st.sidebar.button("ดึงรูปจากไดร์ฟ"):
    url = f"https://www.googleapis.com/drive/v3/files?q='{FOLDER_ID}'+in+parents&key={API_KEY}"
    files = requests.get(url).json().get('files', [])
    st.session_state.processed_images = []
    for f in files:
        img_url = f"https://www.googleapis.com/drive/v3/files/{f['id']}?alt=media&key={API_KEY}"
        img_data = requests.get(img_url).content
        img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
        if img is not None:
            st.session_state.processed_images.append({"img": img, "raw": img_data})
    st.sidebar.success(f"ดึงมาแล้ว {len(st.session_state.processed_images)} รูป")

# หน้าบ้าน: แขกอัปโหลดรูป
uploaded = st.file_uploader("อัปโหลดรูปหน้าของคุณ")
if uploaded and st.session_state.processed_images:
    user_img = cv2.imdecode(np.frombuffer(uploaded.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
    user_face = face_cascade.detectMultiScale(user_img, 1.1, 4)
    
    if len(user_face) > 0:
        found = False
        for item in st.session_state.processed_images:
            gray = cv2.cvtColor(item["img"], cv2.COLOR_BGR2GRAY)
            if len(face_cascade.detectMultiScale(gray, 1.1, 4)) > 0:
                st.image(item["img"], caption="เจอรูปคุณแล้ว!")
                st.download_button("ดาวน์โหลดรูปนี้", item["raw"], "result.jpg")
                found = True
        if not found: st.error("ไม่พบรูปที่ตรงกับใบหน้า")
    else:
        st.error("อัปโหลดรูปที่เห็นหน้าชัดๆ")
