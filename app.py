import streamlit as st
import cv2
import numpy as np
import requests

# 🎯 ไม้ตาย: ตรวจจับ LINE แล้วดีดตัวออกทันที แขกจะได้ใช้แอปกล้องหลักของเครื่องได้เต็มประสิทธิภาพ
st.markdown(
    """
    <script>
    if (navigator.userAgent.indexOf('Line') > -1) {
        var currentUrl = window.location.href;
        if (currentUrl.indexOf('?') > -1) {
            window.location.href = currentUrl + '&openExternalBrowser=1';
        } else {
            window.location.href = currentUrl + '?openExternalBrowser=1';
        }
    }
    </script>
    """,
    unsafe_allow_html=True
)

# 1. ตั้งค่าหน้าเว็บกว้าง
st.set_page_config(page_title="Photo Finder System", layout="wide")

st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายในงาน (เวอร์ชันสลับแอปกล้องใหญ่)")
st.write("👇 แขกจิ้มปุ่มด้านล่างเพื่อเปิดกล้องถ่ายรูป หรือเลือกรูปในเครื่องได้ทันทีครับ")

# 🛠️ 2. รหัสเชื่อมต่อ Google Drive ของน้า
GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

if "scanned_file_ids" not in st.session_state:
    st.session_state["scanned_file_ids"] = set()
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []

# ฟังก์ชันดึงรายชื่อไฟล์จาก Google Drive
def fetch_all_file_ids_via_api():
    if not GDRIVE_FOLDER_ID or "1PKox87" not in GDRIVE_FOLDER_ID:
        return []
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents+and+mimeType+contains+'image/'&key={GOOGLE_API_KEY}&fields=files(id)&pageSize=200"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            files_data = response.json().get('files', [])
            return [f['id'] for f in files_data]
    except:
        pass
    return []

# ฟังก์ชันดึงรูปภาพจาก Drive เมื่อกดปุ่มอัปเดต
def manual_sync_gdrive():
    current_file_ids = fetch_all_file_ids_via_api()
    new_file_ids = [fid for fid in current_file_ids if fid not in st.session_state["scanned_file_ids"]]
    
    if not new_file_ids:
        return 0
        
    count = 0
    for f_idx, file_id in enumerate(new_file_ids):
        try:
            download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={GOOGLE_API_KEY}"
            req_file = requests.get(download_url, timeout=5)
            if req_file.status_code == 200:
                raw_bytes = req_file.content
                file_bytes = np.asarray(bytearray(raw_bytes), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, 1)
                
                if image is not None:
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(70, 70))
                    
                    if len(faces) > 0:
                        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        img_id = f"gdrive_{file_id}_{f_idx}"
                        
                        for (x, y, w, h) in faces:
                            face_roi = gray[y:y+h, x:x+w]
                            face_resized = cv2.resize(face_roi, (40, 40))
                            st.session_state["face_images_db"].append({
                                "feat": face_resized.tolist(),
                                "img": image_rgb,
                                "img_id": img_id,
                                "raw_bytes": raw_bytes
                            })
                st.session_state["scanned_file_ids"].add(file_id)
                count += 1
        except:
            continue
    return count

# 7. สร้างเมนูฝั่งซ้ายมือ (Sidebar)
st.sidebar.header("⚙️ เมนูควบคุมระบบ")

st.sidebar.markdown("### 🔄 อัปเดตคลังรูปถ่าย")
if st.sidebar.button("⚡ กดเพื่อดึงรูปใหม่จาก Drive", use_container_width=True):
    with st.sidebar.spinner("กำลังดึงข้อมูล..."):
        added = manual_sync_gdrive()
        st.sidebar.success(f"ดึงรูปภาพใหม่สำเร็จ {added} รูป!")
        st.rerun()

st.sidebar.markdown("---")
menu = ["หน้าหลักสำหรับสแกนรูป", "ฝั่งแอดมินสำหรับผู้จัดงาน"]
choice = st.sidebar.radio("เลือกหน้าต่างที่ต้องการ:", menu)

if choice == "ฝั่งแอดมินสำหรับผู้จัดงาน":
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ ล้างคลังรูปภาพทั้งหมด"):
        st.session_state["face_images_db"] = []
        st.session_state["scanned_file_ids"] = set()
        st.sidebar.success("ล้างข้อมูลเรียบร้อย!")
        st.rerun()

# --- หน้าที่ 1: หน้าหลักค้นหาใบหน้า ---
if choice == "หน้าหลักสำหรับสแกนรูป":
    
    # 🎯 จุดเปลี่ยนสำคัญ: เพิ่มคำสั่งดึงแอปกล้องถ่ายรูปหลักของมือถือ แขกจะถ่ายสดได้ไฟล์ใหญ่ชัดเจนชัวร์ครับน้า
    uploaded_file = st.file_uploader(
        "📸 จิ้มที่ปุ่มด้านล่างเพื่อ [ถ่ายรูปสดจากกล้อง] หรือ [เลือกรูปภาพในเครื่อง]", 
        type=["jpg", "jpeg", "png"], 
        accept_raw_bytes=True,
        key="camera_or_file"
    )
    
    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
        
        if len(faces) == 0:
            st.error("❌ ไม่พบใบหน้าในรูปภาพที่ส่งมา กรุณาใช้รูปหน้าตรงชัดเจนครับ")
        else:
            x, y, w, h = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_roi, (40, 40))
            
            matched_items = []
            seen_images = set()
            query_face = np.array(face_resized, dtype=np.float32)
            
            for item in st.session_state["face_images_db"]:
                db_face = np.array(item["feat"], dtype=np.float32)
                res = cv2.matchTemplate(db_face, query_face, cv2.TM_CCOEFF_NORMED)
                similarity = res[0][0]
                
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
                        line_share_url = "https://social-plugins.line.me/lineit/share?url=https://yiday4hy.streamlit.app"
                        st.markdown(f'<a href="{line_share_url}" target="_blank"><button style="background-color:#06C755; color:white; border:none; padding:8px 16px; border-radius:4px; cursor:pointer; width:100%; font-weight:bold;">🟢 ส่งต่อ / แชร์เว็บเข้า LINE</button></a>', unsafe_allow_html=True)
                        st.write("")
            else:
                st.error("❌ ไม่พบรูปภาพที่ตรงกับใบหน้าของคุณในคลังภาพ")

# --- หน้าที่ 2: ฝั่งแอดมิน ---
elif choice == "ฝั่งแอดมินสำหรับผู้จัดงาน":
    st.subheader("🔒 กรุณาใส่รหัสผ่านแอดมินเพื่อเข้าสู่ระบบ")
    password = st.text_input("กรอกรหัสผ่านหลังบ้าน:", type="password")
    if password == "2401":
        st.success("🔓 รหัสผ่านถูกต้อง!")
        st.write("---")
        st.subheader("🤖 ระบบเชื่อมต่อ Google Drive เรียลไทม์")
        unique_photos = len(st.session_state["scanned_file_ids"])
        st.info(f"💡 ตอนนี้ในคลังมีรูปภาพที่สแกนเสร็จพร้อมใช้งานแล้วทั้งหมด: {unique_photos} รูป")
    elif password != "":
        st.error("❌ รหัสผ่านไม่ถูกต้อง!")
