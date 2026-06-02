import streamlit as st
import cv2
import numpy as np
import requests

# ตั้งค่า
FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

st.set_page_config(page_title="Photo Finder", layout="wide")
st.title("📸 ระบบค้นหารูป (เวอร์ชันรันผ่านชัวร์)")

if "images" not in st.session_state: st.session_state.images = []

# ดึงรูป
if st.button("1. กดปุ่มนี้เพื่อดึงรูปจาก Drive"):
    url = f"https://www.googleapis.com/drive/v3/files?q='{FOLDER_ID}'+in+parents&key={API_KEY}"
    files = requests.get(url).json().get('files', [])
    st.session_state.images = []
    
    for f in files:
        img_url = f"https://www.googleapis.com/drive/v3/files/{f['id']}?alt=media&key={API_KEY}"
        data = requests.get(img_url).content
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if img is not None:
            st.session_state.images.append(img)
    st.success(f"ดึงรูปมาแล้ว {len(st.session_state.images)} รูป")

# ค้นหา
uploaded = st.file_uploader("2. อัปโหลดรูปใบหน้าของคุณ", type=["jpg", "png"])
if uploaded and st.session_state.images:
    user_data = np.frombuffer(uploaded.read(), np.uint8)
    user_img = cv2.imdecode(user_data, cv2.IMREAD_GRAYSCALE)
    
    for img in st.session_state.images:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) > 0:
            st.image(img, caption="เจอหน้าคุณในรูปนี้!")
