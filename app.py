import streamlit as st
import cv2
import numpy as np
import requests

# 🎯 ตั้งค่าให้แถบเมนู (Sidebar) กางออกอัตโนมัติทันทีที่เปิดเว็บ
st.set_page_config(page_title="Photo Finder System", layout="wide", initial_sidebar_state="expanded")

st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายในงาน")
st.write("👇 แขกจิ้มปุ่มด้านล่างเพื่อถ่ายรูปสด หรือเลือกรูปภาพในเครื่องได้ทันทีครับ")

# รหัสเชื่อมต่อ Google Drive
GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

if "scanned_file_ids" not in st.session_state:
    st.session_state["scanned_file_ids"] = set()
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []

def fetch_all_file_ids_via_api():
    if not GDRIVE_FOLDER_ID or "1PKox87" not in GDRIVE_FOLDER_ID:
        return []
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents+and+mimeType+contains+'image/'&key={GOOGLE_API_KEY}&fields=files(id)&pageSize=200"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return [f['id'] for f in response.json().get('files', [])]
    except:
        pass
    return []

def manual_sync_gdrive():
    current_file_ids = fetch_all_file_ids_via_api()
    new_file_ids = [fid for fid in current_file_ids if fid not in st.session_state["scanned_file_ids"]]
    if not new_file_ids: return 0
    count = 0
    for file_id in new_file_ids:
        try:
            download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={GOOGLE_API_KEY}"
            req_file = requests.get(download_url, timeout=5)
            if req_file.status_code == 200:
                raw_bytes = req_file.content
                image = cv2.imdecode(np.asarray(bytearray(raw_bytes), dtype=np.uint8), 1)
                if image is not None:
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.2, 5)
                    if len(faces) > 0:
                        st.session_state["face_images_db"].append({"img": cv2.cvtColor(image, cv2.COLOR_BGR2RGB), "raw_bytes": raw_bytes, "feat": cv2.resize(gray[faces[0][1]:faces[0][1]+faces[0][3], faces[0][0]:faces[0][0]+faces[0][2]], (40, 40)).tolist()})
                st.session_state["scanned_file_ids"].add(file_id)
                count += 1
        except: continue
    return count

# --- เมนูควบคุมด้านซ้ายมือ (Sidebar) ---
st.sidebar.header("⚙️ เมนูควบคุมระบบ")
if st.sidebar.button("⚡ กดเพื่อดึงรูปใหม่จาก Drive", use_container_width=True):
    with st.sidebar.spinner("กำลังโหลด..."):
        added = manual_sync_gdrive()
        st.sidebar.success(f"ดึงรูปใหม่สำเร็จ {added} รูป!")
        st.rerun()

st.sidebar.markdown("---")
menu = ["หน้าหลักสำหรับสแกนรูป", "ฝั่งแอดมินสำหรับผู้จัดงาน"]
choice = st.sidebar.radio("เลือกเมนู:", menu)

# --- หน้าหลัก ---
if choice == "หน้าหลักสำหรับสแกนรูป":
    uploaded_file = st.file_uploader("📸 ถ่ายรูปหรือเลือกรูปจากเครื่องเพื่อค้นหา", type=["jpg", "png"], key="search")
    if uploaded_file:
        # (ระบบสแกนหน้าเดิมของน้า)
        st.info("กำลังประมวลผลการค้นหา...")
        # ... logic การสแกนหน้า ...

elif choice == "ฝั่งแอดมินสำหรับผู้จัดงาน":
    password = st.text_input("รหัสผ่าน:", type="password")
    if password == "2401":
        st.success("🔓 รหัสผ่านถูกต้อง!")
        if st.button("🗑️ ล้างคลังรูปภาพทั้งหมด"):
            st.session_state["face_images_db"] = []
            st.session_state["scanned_file_ids"] = set()
            st.rerun()
