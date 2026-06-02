import streamlit as st
import cv2
import numpy as np
import requests

# ตั้งค่าหน้าเว็บให้ Sidebar กางออกอัตโนมัติ
st.set_page_config(page_title="Photo Finder", layout="wide", initial_sidebar_state="expanded")

# ระบบทะลวง LINE
st.markdown("""
    <script>
    if (navigator.userAgent.indexOf('Line') > -1) {
        window.location.href = window.location.href + '?openExternalBrowser=1';
    }
    </script>
""", unsafe_allow_html=True)

st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายในงาน")

# ตั้งค่าฐานข้อมูลและเชื่อมต่อ Drive
GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

if "scanned_file_ids" not in st.session_state:
    st.session_state["scanned_file_ids"] = set()
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []

# ฟังก์ชันดึงรูปภาพ (ไม่ให้หน้าเว็บหลักค้าง)
def sync_background():
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents&key={GOOGLE_API_KEY}&fields=files(id)&pageSize=50"
    try:
        res = requests.get(url, timeout=3).json().get('files', [])
        for f in res:
            if f['id'] not in st.session_state["scanned_file_ids"]:
                dl = f"https://www.googleapis.com/drive/v3/files/{f['id']}?alt=media&key={GOOGLE_API_KEY}"
                img_data = requests.get(dl, timeout=3).content
                img = cv2.imdecode(np.frombuffer(img_data, np.uint8), 1)
                if img is not None:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.2, 5)
                    if len(faces) > 0:
                        st.session_state["face_images_db"].append({"img": cv2.cvtColor(img, cv2.COLOR_BGR2RGB), "raw": img_data, "feat": cv2.resize(gray[faces[0][1]:faces[0][1]+faces[0][3], faces[0][0]:faces[0][0]+faces[0][2]], (40, 40)).tolist()})
                st.session_state["scanned_file_ids"].add(f['id'])
    except: pass

sync_background()

# ส่วนของแขก (0 วิ)
uploaded_file = st.file_uploader("📸 [ถ่ายรูปสด] หรือ [เลือกรูปภาพในเครื่อง]", type=["jpg", "png"])

if uploaded_file:
    st.info("ระบบกำลังค้นหาจากคลังภาพ...")
    # โค้ดสแกนเปรียบเทียบหน้า...

# เมนูหลังบ้าน
st.sidebar.header("⚙️ ระบบหลังบ้าน")
st.sidebar.write(f"จำนวนรูปที่สแกนแล้ว: {len(st.session_state['face_images_db'])} รูป")
