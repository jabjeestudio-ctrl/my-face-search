import streamlit as st
import cv2
import numpy as np
import requests
import re

# ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง
st.set_page_config(page_title="Photo Finder System", layout="wide")

st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายในงาน (เวอร์ชันดาวน์โหลด & ส่งไลน์)")
st.write("👇 แขกอัปโหลดรูปตัวเอง เพื่อค้นหารูปทั้งหมดในงาน สามารถกดดาวน์โหลดหรือแชร์เข้า LINE ได้ทันที")

# 🛠️ จุดสำคัญ: น้าก๊อปปี้ "ลิงก์แชร์โฟลเดอร์ Google Drive" (ลิงก์เต็มๆ) มาวางในเครื่องหมายคำพูดตรงนี้ได้เลยครับ!
GDRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0?usp=sharing"

# โหลดตัวตรวจจับใบหน้ามาตรฐานของ OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ใช้ Session State ในการจำข้อมูลใบหน้าและรูปภาพเต็ม
if "scanned_file_ids" not in st.session_state:
    st.session_state["scanned_file_ids"] = set()
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []

# ฟังก์ชันดึง ID รูปภาพจากกูเกิลไดรฟ์แบบแม่นยำสูง
def fetch_all_file_ids_from_url(url):
    try:
        # ดึง Folder ID ออกมาจากลิงก์แชร์โดยอัตโนมัติ
        match = re.search(r'folders/([A-Za-z0-9_-]+)', url)
        if not match:
            match = re.search(r'id=([A-Za-z0-9_-]+)', url)
        
        if match:
            folder_id = match.group(1)
            # วิ่งไปแกะโค้ดหน้าเว็บจากกูเกิลเพื่อดึงรายการไฟล์รูปภาพ
            folder_url = f"https://drive.google.com/embeddedfolderview?id={folder_id}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(folder_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # ค้นหารหัสไฟล์รูปภาพทั้งหมดในหน้านั้น
                file_ids = re.findall(r'\"([A-Za-z0-9_-]{25,50})\"', response.text)
                valid_ids = [fid for fid in file_ids if not fid.startswith('entry_') and len(fid) > 30]
                return list(set(valid_ids))
        return []
    except:
        return []

# ฟังก์ชันตรวจเช็กและแอบดึงรูปใหม่เข้าคลังอัตโนมัติเบื้องหลัง
def auto_sync_gdrive():
    if not GDRIVE_FOLDER_URL or "เอา_ลิงก์แชร์โฟลเดอร์" in GDRIVE_FOLDER_URL:
        return
        
    current_file_ids = fetch_all_file_ids_from_url(GDRIVE_FOLDER_URL)
    new_file_ids = [fid for fid in current_file_ids if fid not in st.session_state["scanned_file_ids"]]
    
    if new_file_ids:
        for f_idx, file_id in enumerate(new_file_ids):
            try:
                download_url = f"https://docs.google.com/uc?export=download&id={file_id}"
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

# 🔄 รันระบบดูดรูปอัตโนมัติเบื้องหลังทันที
auto_sync_gdrive()

# สร้างเมนูฝั่งซ้ายมือ (Sidebar)
st.sidebar.header("⚙️ เมนูการใช้งาน")
menu = ["🏠 หน้าหลัก (สำหรับแขกสแกนรูป)", "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)"]
choice = st.sidebar.radio("เลือกหน้าต่างที่ต้องการ:", menu)

# --- ปุ่มเคลียร์ข้อมูลด่วนฝั่ง Sidebar ---
if choice == "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)":
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ ล้างคลังรูปภาพทั้งหมดในระบบ"):
        st.session_state["face_images_db"] = []
        st.session_state["scanned_file_ids"] = set()
        st.sidebar.success("ล้างข้อมูลเรียบร้อยแล้ว!")

# --- หน้าที่ 1: หน้าหลักค้นหาใบหน้า (ระบบซ่อมแซมปุ่มแชร์ LINE) ---
if choice == "🏠 หน้าหลัก (สำหรับแขกสแกนรูป)":
    if len(st.session_state["face_images_db"]) == 0:
        st.warning("⚠️ กำลังดึงคลังรูปภาพจาก Google Drive หรือคลังภาพในไดรฟ์ยังว่างอยู่ครับ (หากเพิ่งอัปโหลดรูปภาพลงไดรฟ์ กรุณารอสัก 1-2 นาที แล้วรีเฟรชหน้าเว็บนะครับ)")
    else:
        uploaded_file = st.file_uploader("อัปโหลดรูปภาพใบหน้าของคุณเพื่อค้นหารูปทั้งหมดในงาน", type=["jpg", "jpeg", "png"], key="search_photo")
        
        if uploaded_file:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                st.error("❌ ไม่พบใบหน้าในรูปภาพที่ส่งมา กรุณาใช้รูปที่เห็นหน้าตรงชัดเจนครับ")
            else:
                x, y, w, h = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face_roi, (32, 32)).tolist()
                
                matched_items = []
                seen_images = set()
                
                for item in st.session_state["face_images_db"]:
                    diff = np.sum(np.abs(np.array(item["feat"]) - np.array(face_resized)))
                    
                    if diff < 38000:  # เกณฑ์แม่นยำสูงตรงปก
                        if item["img_id"] not in seen_images:
                            matched_items.append(item)
                            seen_images.add(item["img_id"])
                
                # --- แสดงผลลัพธ์ ---
                if len(matched_items) > 0:
                    st.success(f"🎉 เจอรูปถ่ายของคุณในระบบทั้งหมด {len(matched_items)} รูปครับ! 👇")
                    
                    cols = st.columns(2)
                    for idx, item in enumerate(matched_items):
                        with cols[idx % 2]:
                            st.image(item["img"], caption=f"รูปที่ {idx + 1} (ชัดเต็มพิกเซล)", use_container_width=True)
                            
                            st.download_button(
                                label=f"📥 ดาวน์โหลดรูปที่ {idx + 1}",
                                data=item["raw_bytes"],
                                file_name=f"event_photo_{idx+1}.jpg",
                                mime="image/jpeg",
                                key=f"dl_{idx}"
                            )
                            
                            line_share_url = "https://social-plugins.line.me/lineit/share?url=" + "https://yiday4hy.streamlit.app"
                            st.markdown(f'<a href="{line_share_url}" target="_blank"><button style="background-color:#06C755; color:white; border:none; padding:8px 16px; border-radius:4px; cursor:pointer; width:100%; font-weight:bold;">🟢 ส่งต่อ / แชร์เว็บเข้า LINE</button></a>', unsafe_allow_html=True)
                            st.write("") 
                else:
                    st.error("❌ ไม่พบรูปภาพที่ตรงกับใบหน้าของคุณในคลังภาพ")

# --- หน้าที่ 2: ฝั่งแอดมิน (ล็อกรหัส 2401 แจ้งสถานะ Google Drive) ---
elif choice == "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)":
    st.subheader("🔒 กรุณาใส่รหัสผ่านแอดมินเพื่อเข้าสู่ระบบ")
    password = st.text_input("กรอกรหัสผ่านหลังบ้าน:", type="password")
    
    if password == "2401":
        st.success("🔓 รหัสผ่านถูกต้อง! ยินดีต้อนรับแอดมิน")
        st.write("---")
        
        st.subheader("🤖 ระบบเชื่อมต่อ Google Drive เรียลไทม์")
        unique_photos = len(st.session_state["scanned_file_ids"])
        st.info(f"💡 ตอนนี้ระบบตรวจจับและดึงไฟล์รูปภาพมาจากไดรฟ์ได้แล้วทั้งหมด: {unique_photos} รูป")
        st.write("✨ ตากล้องโยนรูปเข้าไดรฟ์ ระบบฝั่งแขกจะดึงไปสแกนเองอัตโนมัติเลยครับ ชิลๆ!")
                
    elif password != "":
        st.error("❌ รหัสผ่านไม่ถูกต้อง!")
