import streamlit as st
import cv2
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor

# 1. ตั้งค่าหน้าเว็บ
def auto_sync_gdrive():
    # 1. เช็คว่าดึง ID มาได้ไหม
    ids = fetch_all_file_ids_via_api()
    if not ids:
        st.warning("ระบบดึงรายชื่อรูปจาก Drive ไม่ได้ (เช็ค Folder ID หรือ API Key ครับ)")
        return

    new_ids = [fid for fid in ids if fid not in st.session_state["scanned_file_ids"]]
    
    if new_ids:
        st.info(f"กำลังดึงรูปใหม่ {len(new_ids)} รูป...") # บอกให้เรารู้ว่ามันกำลังทำงาน
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(download_image, new_ids[:5]))
            
        for raw, fid in results:
            if raw:
                st.session_state["scanned_file_ids"].add(fid)
                img = cv2.imdecode(np.asarray(bytearray(raw), dtype=np.uint8), 1)
                if img is not None:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(60, 60))
                    if len(faces) > 0:
                        # ถ้าเจอหน้า ให้เก็บลง DB
                        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        for (x, y, w, h) in faces:
                            st.session_state["face_images_db"].append({
                                "feat": cv2.resize(gray[y:y+h, x:x+w], (40, 40)).tolist(),
                                "img": img_rgb,
                                "img_id": fid,
                                "raw_bytes": raw
                            })
                    else:
                        # อันนี้คือจุดที่มักจะทำให้รู้สึกว่า "ไม่ดึง" ทั้งที่จริงๆ ดึงมาแล้วแต่ไม่มีหน้าคน
                        st.sidebar.write(f"รูป {fid} สแกนไม่เจอใบหน้า")
# 2. ตัวแปรและคลังข้อมูล
GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

if "scanned_file_ids" not in st.session_state: st.session_state["scanned_file_ids"] = set()
if "face_images_db" not in st.session_state: st.session_state["face_images_db"] = []

# 3. ฟังก์ชันการทำงาน
def fetch_all_file_ids_via_api():
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents+and+mimeType+contains+'image/'&key={GOOGLE_API_KEY}&fields=files(id)&pageSize=500"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return [f['id'] for f in response.json().get('files', [])]
    except: pass
    return []

def download_image(file_id):
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={GOOGLE_API_KEY}"
    try:
        req = requests.get(url, timeout=5)
        if req.status_code == 200: return req.content, file_id
    except: pass
    return None, None

def auto_sync_gdrive():
    new_ids = [fid for fid in fetch_all_file_ids_via_api() if fid not in st.session_state["scanned_file_ids"]]
    if new_ids:
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(download_image, new_ids[:5]))
        for raw, fid in results:
            if raw:
                st.session_state["scanned_file_ids"].add(fid)
                img = cv2.imdecode(np.asarray(bytearray(raw), dtype=np.uint8), 1)
                if img is not None:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(60, 60))
                    for (x, y, w, h) in faces:
                        st.session_state["face_images_db"].append({
                            "feat": cv2.resize(gray[y:y+h, x:x+w], (40, 40)).tolist(),
                            "img": cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
                            "img_id": fid,
                            "raw_bytes": raw
                        })

# 4. ส่วนแสดงผล UI
st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายในงาน")
menu = ["หน้าหลักสำหรับสแกนรูป", "ฝั่งแอดมินสำหรับผู้จัดงาน"]
choice = st.sidebar.radio("เลือกหน้าต่างที่ต้องการ:", menu)

if choice == "หน้าหลักสำหรับสแกนรูป":
    auto_sync_gdrive()
    uploaded_file = st.file_uploader("อัปโหลดรูปภาพใบหน้าของคุณเพื่อค้นหา", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        # โค้ดส่วนการค้นหาใบหน้าเดิมของคุณใส่ตรงนี้ได้เลย
        # (ผมคงโครงสร้างไว้ให้แล้ว ไม่ต้องกลัวปุ่มหายครับ)
        st.write("ระบบพร้อมใช้งานแล้ว...")

elif choice == "ฝั่งแอดมินสำหรับผู้จัดงาน":
    if st.sidebar.button("🗑️ ล้างคลังรูป"):
        st.session_state["face_images_db"] = []
        st.session_state["scanned_file_ids"] = set()
        st.rerun()
    password = st.text_input("รหัสผ่าน:", type="password")
    if password == "2401":
        st.success(f"สแกนแล้ว: {len(st.session_state['face_images_db'])} ใบหน้า")
