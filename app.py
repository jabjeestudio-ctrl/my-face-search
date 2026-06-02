import streamlit as st
import cv2
import numpy as np
import requests
import face_recognition

st.set_page_config(page_title="Photo Finder PRO", layout="wide")

# ตั้งค่า
GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"

if "scanned_file_ids" not in st.session_state: st.session_state["scanned_file_ids"] = set()
if "face_images_db" not in st.session_state: st.session_state["face_images_db"] = []

def auto_sync_gdrive():
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents&key={GOOGLE_API_KEY}"
    files = requests.get(url).json().get('files', [])
    for f in files:
        if f['id'] not in st.session_state["scanned_file_ids"]:
            img_url = f"https://www.googleapis.com/drive/v3/files/{f['id']}?alt=media&key={GOOGLE_API_KEY}"
            data = requests.get(img_url).content
            img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # ใช้ AI สแกนใบหน้า (แม่นกว่า OpenCV เดิมมาก)
            encs = face_recognition.face_encodings(rgb)
            if encs:
                st.session_state["face_images_db"].append({"enc": encs[0], "img": rgb, "raw": data})
            st.session_state["scanned_file_ids"].add(f['id'])

# เมนู
menu = st.sidebar.radio("เลือกหน้า:", ["หน้าบ้าน (แขก)", "หลังบ้าน (แอดมิน)"])

if menu == "หลังบ้าน (แอดมิน)":
    st.title("⚙️ จัดการระบบ")
    if st.button("ดึงรูปจากไดร์ฟและสแกนใบหน้า"):
        with st.spinner("กำลังประมวลผล..."):
            auto_sync_gdrive()
            st.success("สแกนเสร็จสิ้น!")
    st.write(f"จำนวนรูปที่สแกนแล้ว: {len(st.session_state['scanned_file_ids'])}")

elif menu == "หน้าบ้าน (แขก)":
    st.title("📸 ค้นหารูปของคุณ")
    up = st.file_uploader("อัปโหลดรูปหน้าของคุณ", type=["jpg", "png"])
    if up:
        user_encs = face_recognition.face_encodings(face_recognition.load_image_file(up))
        if user_encs:
            found = False
            for item in st.session_state["face_images_db"]:
                # เปรียบเทียบใบหน้าด้วย AI
                if face_recognition.compare_faces([item["enc"]], user_encs[0], tolerance=0.5)[0]:
                    st.image(item["img"], caption="เจอรูปนี้ในงาน!")
                    st.download_button("ดาวน์โหลดรูป", item["raw"], "photo.jpg")
                    found = True
            if not found: st.warning("ไม่พบใบหน้าของคุณ")
        else: st.error("ไม่พบใบหน้าในรูป")
