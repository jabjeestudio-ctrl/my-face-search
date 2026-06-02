import streamlit as st
import cv2
import numpy as np
import requests

# 1. ตั้งค่าหน้าเว็บกว้าง
st.set_page_config(page_title="Photo Finder", layout="wide")

st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายในงาน (เปิดปุ๊บ ติดปั๊บ 0 วินาที)")

# 🛠️ ตั้งค่า Google Drive
GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# จำข้อมูลไว้ในหน่วยความจำเว็บ
if "scanned_file_ids" not in st.session_state:
    st.session_state["scanned_file_ids"] = set()
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []

# --- ระบบหลังบ้าน: ดึงข้อมูลทีละน้อย ---
def background_sync():
    # ดึงรายชื่อไฟล์มาแค่ ID (เร็วมาก)
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents&key={GOOGLE_API_KEY}&fields=files(id)&pageSize=100"
    try:
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            files = res.json().get('files', [])
            # สแกนแค่รูปที่ยังไม่เคยสแกน (ทีละ 3 รูปพอ เพื่อไม่ให้เว็บค้าง)
            new_files = [f for f in files if f['id'] not in st.session_state["scanned_file_ids"]][:3]
            for f in new_files:
                dl_url = f"https://www.googleapis.com/drive/v3/files/{f['id']}?alt=media&key={GOOGLE_API_KEY}"
                img_data = requests.get(dl_url, timeout=3).content
                img = cv2.imdecode(np.frombuffer(img_data, np.uint8), 1)
                if img is not None:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.2, 5)
                    if len(faces) > 0:
                        st.session_state["face_images_db"].append({"img": cv2.cvtColor(img, cv2.COLOR_BGR2RGB), "raw": img_data, "feat": cv2.resize(gray[faces[0][1]:faces[0][1]+faces[0][3], faces[0][0]:faces[0][0]+faces[0][2]], (40, 40)).tolist()})
                st.session_state["scanned_file_ids"].add(f['id'])
    except: pass

# --- จุดสำคัญ: แสดงปุ่มอัปโหลดก่อน! ---
# แขกเข้าเว็บมา จะเห็นปุ่มนี้ทันทีใน 0 วินาที
uploaded_file = st.file_uploader("📸 [ถ่ายรูปสด] หรือ [เลือกรูปจากเครื่อง] เพื่อเริ่มค้นหา", type=["jpg", "png"], key="search")

# หลังจากวาดปุ่มเสร็จ ค่อยให้ระบบหลังบ้านไปทำงาน
background_sync()

# ส่วนค้นหา
if uploaded_file:
    st.info("กำลังค้นหา...")
    # ... ใส่โค้ดเปรียบเทียบใบหน้าของคุณที่นี่ ...

# เมนูแอดมิน
st.sidebar.write(f"📊 รูปในคลังพร้อมสแกน: {len(st.session_state['face_images_db'])} รูป")
