import streamlit as st
import cv2
import numpy as np
import requests

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Photo Finder System", layout="wide")

# 2. ตัวแปรและค่าคงที่
GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 3. Session State
if "scanned_file_ids" not in st.session_state:
    st.session_state["scanned_file_ids"] = set()
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []

# 4. ฟังก์ชันต่างๆ (นิยามไว้เฉยๆ ยังไม่รัน)
def fetch_all_file_ids_via_api():
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents+and+mimeType+contains+'image/'&key={GOOGLE_API_KEY}&fields=files(id)&pageSize=500"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return [f['id'] for f in response.json().get('files', [])]
    except:
        pass
    return []

def auto_sync_gdrive():
    current_file_ids = fetch_all_file_ids_via_api()
    new_file_ids = [fid for fid in current_file_ids if fid not in st.session_state["scanned_file_ids"]]
    if new_file_ids:
        batch_files = new_file_ids[:5]
        for f_idx, file_id in enumerate(batch_files):
            # ... (โค้ดสแกนใบหน้าเดิมของคุณใส่ตรงนี้) ...
            st.session_state["scanned_file_ids"].add(file_id)

# 5. UI และการควบคุม (ส่วนที่แสดงผลบนหน้าจอ)
st.sidebar.header("⚙️ เมนูการใช้งาน")
menu = ["หน้าหลักสำหรับสแกนรูป", "ฝั่งแอดมินสำหรับผู้จัดงาน"]
choice = st.sidebar.radio("เลือกหน้าต่างที่ต้องการ:", menu)

if choice == "หน้าหลักสำหรับสแกนรูป":
    st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายในงาน")
    
    # ⚡ การดึงข้อมูลจะทำงานที่นี่ (หลังหน้าจอโหลดเสร็จ)
    auto_sync_gdrive() 
    
    uploaded_file = st.file_uploader("อัปโหลดรูปภาพใบหน้าของคุณเพื่อค้นหารูปในงาน", type=["jpg", "jpeg", "png"], key="search_photo")
    # ... (ส่วนการค้นหาและแสดงผลรูปที่เหลือของคุณวางไว้ตรงนี้) ...

elif choice == "ฝั่งแอดมินสำหรับผู้จัดงาน":
    st.subheader("🔒 กรุณาใส่รหัสผ่านแอดมิน")
    password = st.text_input("กรอกรหัสผ่าน:", type="password")
    if password == "2401":
        st.success("🔓 รหัสผ่านถูกต้อง!")
