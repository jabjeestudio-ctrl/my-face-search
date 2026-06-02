import streamlit as st
import cv2
import numpy as np
import requests

# ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง
st.set_page_config(page_title="Photo Finder System", layout="wide")

st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายในงาน (เวอร์ชันดาวน์โหลด & ส่งไลน์)")
st.write("👇 ตากล้องโยนรูปเข้าไดรฟ์ แขกสแกนหน้าตรงนี้ระบบดึงภาพใหม่ให้อัตโนมัติเลยครับ")

# 🛠️ รหัสเชื่อมต่อ Google Drive ของน้า (ล็อคค่าเดิมที่น้าทำผ่านแล้วไว้ให้เลยครับ)
GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"

# โหลดตัวตรวจจับใบหน้ามาตรฐานของ OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ใช้ Session State ในการจำข้อมูลใบหน้าและรูปภาพเต็ม
if "scanned_file_ids" not in st.session_state:
    st.session_state["scanned_file_ids"] = set()
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []

# ฟังก์ชันดึงรายชื่อไฟล์รูปภาพผ่าน Google API
def fetch_all_file_ids_via_api():
    if not GDRIVE_FOLDER_ID or "วาง_Folder" in GDRIVE_FOLDER_ID or "วาง_API" in GOOGLE_API_KEY:
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

# ฟังก์ชันดึงรูปภาพใหม่เข้ามาระบบสแกนหน้าเบื้องหลัง
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
                        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(70, 70))
                        
                        if len(faces) > 0:
                            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            img_id = f"gdrive_{file_id}_{f_idx}"
                            
                            for (x, y, w, h) in faces:
                                face_roi = gray[y:y+h, x:x+w]
                                face_resized = cv2.resize(face_roi, (40, 40)) # ปรับขนาดเพิ่มความละเอียดมิติใบหน้า
                                
                                st.session_state["face_images_db"].append({
                                    "feat": face_resized.tolist(),
                                    "img": image_rgb,
                                    "img_id": img_id,
                                    "raw_bytes": raw_bytes
                                })
                    st.session_state["scanned_file_ids"].add(file_id)
            except:
                continue

# 🔄 รันระบบอัปเดตอัตโนมัติ
auto_sync_gdrive()

# สร้างเมนูฝั่งซ้ายมือ (Sidebar)
st.sidebar.header("⚙️ เมนูการใช้งาน")
menu = ["🏠 หน้าหลัก (สำหรับแขกสแกนรูป)", "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)"]
choice = st.sidebar.radio("เลือกหน้าต่างที่ต้องการ:", menu)

# --- ปุ่มเคลียร์ข้อมูลด่วนฝั่ง Sidebar ---
if choice == "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)":
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ ล้างคลังรูปภาพและบังคับดึงใหม่"):
        st.session_state["face_images_db"] = []
        st.session_state["scanned_file_ids"] = set()
        st.sidebar.success("กำลังโหลดภาพจากไดรฟ์ใหม่...")
        st.rerun()

# --- หน้าที่ 1: หน้าหลักค้นหาใบหน้า ---
if choice == "🏠 หน้าหลัก (สำหรับแขกสแกนรูป)":
    total_photos = len(st.session_state["scanned_file_ids"])
    if total_photos == 0:
        st.warning("⚠️ คลังรูปภาพยังเป็น 0 รูป หรือตั้งค่าผิดพลาด (กรุณาเช็กการกรอกรหัสที่บรรทัด 13-14 ครับ)")
    else:
        uploaded_file = st.file_uploader("อัปโหลดรูปภาพใบหน้าของคุณเพื่อค้นหารูปในงาน", type=["jpg", "jpeg", "png"], key="search_photo")
        
        if uploaded_file:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(70, 70))
            
            if len(faces) == 0:
                st.error("❌ ไม่พบใบหน้าในรูปภาพที่ส่งมา กรุณาใช้รูปหน้าตรงชัดเจนครับ")
            else:
                x, y, w, h = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face_roi, (40, 40))
                
                matched_items = []
                seen_images = set()
                
                # แปลงใบหน้าที่แขกส่งมาเป็น numpy array เพื่อคำนวณแบบละเอียด
                query_face = np.array(face_resized, dtype=np.float32)
                
                for item in st.session_state["face_images_db"]:
                    db_face = np.array(item["feat"], dtype=np.float32)
                    
                    # ใช้สูตรทางคณิตศาสตร์ OpenCV คำนวณหาความคล้ายคลึงของโครงสร้างหน้า (Template Matching แบบละเอียด)
                    res = cv2.matchTemplate(db_face, query_face, cv2.TM_CCOEFF_NORMED)
                    similarity = res[0][0] # ยิ่งเข้าใกล้ 1.0 ยิ่งแปลว่าหน้าคนเดียวกันเป๊ะ
                    
                    # 🎯 ปรับปรุงเกณฑ์ความแม่นยำใหม่: ปรับมาที่ 0.50 เพื่อให้ดึงรูปคู่รูปกลุ่มได้เก่งและง่ายขึ้น
                    if similarity > 0.50:
                        if item["img_id"] not in seen_images:
                            matched_items.append(item)
                            seen_images.add(item["img_id"])
                
                if len(matched_items) > 0:
                    st.success(f"🎉 เจอรูปถ่ายของคุณในระบบทั้งหมด {len(matched_items)} รูปครับ! 👇")
                    cols = st.columns(2)
                    for idx, item in enumerate(matched_items):
                        with cols[idx % 2]:
                            st.image(item["img"], caption=f"รูปที่ {idx + 1}", use_container_width=True)
                            st.download_button(label=f"📥 ดาวน์โหลดรูปที่ {idx + 1}", data=item["raw_bytes"], file_name=f"photo_{idx+1}.jpg", mime="image/jpeg", key=f"dl_{idx}")
                            line_share_url = "https://social-plugins.line.me/lineit/share?url=https://yiday4hy.
