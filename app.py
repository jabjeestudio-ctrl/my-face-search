import streamlit as st
import cv2
import numpy as np
import requests
import time

# 🎯 ระบบดีดตัวทะลวง LINE
st.markdown(
    """
    <script>
    if (navigator.userAgent.indexOf('Line') > -1) {
        window.location.href = window.location.href + '?openExternalBrowser=1';
    }
    </script>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Photo Finder", layout="wide")

# เชื่อมต่อ Google Drive (ใส่ ID และ API ของน้า)
GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ใช้ session_state เก็บรูปเพื่อให้มัน "ค้างไว้" ไม่หายแม้คนอื่นจะเข้ามาเล่น
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []
    st.session_state["scanned_file_ids"] = set()

# 🚀 ระบบดึงรูปอัตโนมัติแบบเงียบๆ (ไม่ต้องกดปุ่ม)
def auto_sync():
    # ดึงแค่ ID มาเช็คก่อน (เร็วมาก)
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents+and+mimeType+contains+'image/'&key={GOOGLE_API_KEY}&fields=files(id)&pageSize=50"
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            files = response.json().get('files', [])
            for f in files:
                fid = f['id']
                if fid not in st.session_state["scanned_file_ids"]:
                    # ดึงไฟล์รูปมาทีละรูป
                    dl_url = f"https://www.googleapis.com/drive/v3/files/{fid}?alt=media&key={GOOGLE_API_KEY}"
                    img_req = requests.get(dl_url, timeout=3)
                    if img_req.status_code == 200:
                        img_arr = np.frombuffer(img_req.content, np.uint8)
                        image = cv2.imdecode(img_arr, 1)
                        if image is not None:
                            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            faces = face_cascade.detectMultiScale(gray, 1.2, 5)
                            if len(faces) > 0:
                                st.session_state["face_images_db"].append({"img": image, "raw": img_req.content, "feat": gray[faces[0][1]:faces[0][1]+faces[0][3], faces[0][0]:faces[0][0]+faces[0][2]]})
                    st.session_state["scanned_file_ids"].add(fid)
    except:
        pass

# รันระบบดึงรูปอัตโนมัติ (แขกจะยังกดอัปโหลดได้ทันทีโดยไม่ติดค้าง)
auto_sync()

st.title("📸 สแกนหน้าค้นหารูปภาพ")
uploaded_file = st.file_uploader("📸 ถ่ายรูปหรือเลือกรูปจากเครื่อง", type=["jpg", "png"], key="search")

if uploaded_file:
    # ... (โค้ดสแกนใบหน้าเหมือนเดิม) ...
    st.success("กำลังค้นหา...")
    # (เพิ่ม logic ค้นหาจาก st.session_state["face_images_db"] ตรงนี้)
