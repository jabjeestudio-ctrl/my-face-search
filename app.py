import streamlit as st
import cv2
import numpy as np
import requests

# ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง
st.set_page_config(page_title="Photo Finder System", layout="wide")

st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายในงาน (เวอร์ชันดาวน์โหลด & ส่งไลน์)")
st.write("👇 แขกอัปโหลดรูปตัวเอง เพื่อค้นหารูปทั้งหมดในงาน สามารถกดดาวน์โหลดหรือแชร์เข้า LINE ได้ทันที")

# 🛠️ จุดสำคัญ: กรอกข้อมูลกูเกิลของน้าตรงนี้ให้ถูกต้อง (ห้ามลบเครื่องหมายคำพูดออกนะน้า)
GDRIVE_FOLDER_ID = "https://drive.google.com/drive/folders/1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0?usp=sharing"
GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"

# โหลดตัวตรวจจับใบหน้ามาตรฐานของ OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ใช้ Session State ในการจำข้อมูลใบหน้าและรูปภาพเต็ม
if "scanned_file_ids" not in st.session_state:
    st.session_state["scanned_file_ids"] = set()
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []  # [{"feat": feature, "img": image_rgb, "img_id": id, "raw_bytes": bytes}]

# ฟังก์ชันยิงผ่าน Google API ดึงรายชื่อไฟล์รูปภาพแบบถูกต้องตามกฎกูเกิล
def fetch_all_file_ids_via_api():
    if not GDRIVE_FOLDER_ID or "วาง_Folder_ID" in GDRIVE_FOLDER_ID or "วาง_API_Key" in GOOGLE_API_KEY:
        return []
    
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents+and+mimeType+contains+'image/'&key={GOOGLE_API_KEY}&fields=files(id)"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            files_data = response.json().get('files', [])
            return [f['id'] for f in files_data]
    except:
        pass
    return []

# ฟังก์ชันแอบเช็กและดูดรูปภาพใหม่เข้ามาระบบสแกนหน้าแบบเรียลไทม์เบื้องหลัง
def auto_sync_gdrive():
    current_file_ids = fetch_all_file_ids_via_api()
    new_file_ids = [fid for fid in current_file_ids if fid not in st.session_state["scanned_file_ids"]]
    
    if new_file_ids:
        for f_idx, file_id in enumerate(new_file_ids):
            try:
                download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={GOOGLE_API_KEY}"
                req_file = requests.get(download_url, timeout=10)
                
                if req_file.status_code == 200:
                    raw_bytes = req_file.content
                    file_bytes = np.asarray(bytearray(raw_bytes), dtype=np.uint8)
                    image = cv2.imdecode(file_bytes, 1)
                    
                    if image is not None:
                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                        
                        if len(faces) > 0:
                            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            img_id = f"gdrive_{file_id}_{f_idx}"
                            
                            for (x, y, w, h) in faces:
                                face_roi = gray[y:y+h, x:x+w]
                                face_resized = cv2.resize(face_roi, (32, 32)).tolist()
                                
                                st.session_state["face_images_db"].append({
                                    "feat": face_resized,
                                    "img": image_rgb,
                                    "img_id": img_id,
                                    "raw_bytes": raw_bytes
                                })
                    st.session_state["scanned_file_ids"].add(file_id)
            except:
                continue

# 🔄 สั่งระบบอัปเดตเรียลไทม์ทุกครั้งที่มีแขกเปิดหน้าจอใช้งาน
auto_sync_gdrive()

# สร้างเมนูฝั่งซ้ายมือ (Sidebar)
st.sidebar.header("⚙️ เมนูการใช้งาน")
menu = ["🏠 หน้าหลัก (สำหรับแขกสแกนรูป)", "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)"]
choice = st.sidebar.radio("เลือกหน้าต่างที่ต้องการ:", menu)

# --- ปุ่มเคลียร์ข้อมูลด่วนฝั่ง Sidebar ---
if choice == "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)":
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ ล้างคลังรูปภาพและบังคับดึงใหม่จากไดรฟ์"):
        st.session_state["face_images_db"] = []
        st.session_state["scanned_file_ids"] = set()
        st.sidebar.success("ล้างข้อมูลสำเร็จ! กำลังเริ่มโหลดภาพจากไดรฟ์ใหม่...")
        st.rerun()

# --- หน้าที่ 1: หน้าหลักค้นหาใบหน้า (ระบบซ่อมแซมปุ่มแชร์ LINE) ---
if choice == "🏠 หน้าหลัก (สำหรับแขกสแกนรูป)":
    total_photos = len(st.session_state["scanned_file_ids"])
    if total_photos == 0:
        st.warning("⚠️ คลังรูปภาพใน Google Drive ยังเป็น 0 รูป หรือรหัส
