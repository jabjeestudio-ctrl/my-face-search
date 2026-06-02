import streamlit as st
import cv2
import numpy as np
import requests

# 1. ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง
st.set_page_config(page_title="Photo Finder System", layout="wide")

# --- CSS ปรับแต่งหน้าตาให้สวยงาม ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    h1, h2, h3 { color: #1e1e1e !important; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stFileUploader"] { background-color: white; border: 2px dashed #4a90e2; border-radius: 15px; padding: 20px; }
    div.stButton > button { background-color: #4a90e2; color: white; border-radius: 10px; border: none; font-weight: 600; padding: 10px 20px; }
    div.stButton > button:hover { background-color: #357abd; }
    img { border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายในงาน")
st.write("👇 ตากล้องโยนรูปเข้าไดรฟ์ ระบบจะทยอยดึงภาพมาสแกนให้โดยอัตโนมัติครับ")

# 🛠️ 2. รหัสเชื่อมต่อ Google Drive
GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"

# 3. โหลดตัวตรวจจับใบหน้า
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 4. ใช้ Session State
if "scanned_file_ids" not in st.session_state: st.session_state["scanned_file_ids"] = set()
if "face_images_db" not in st.session_state: st.session_state["face_images_db"] = []

def fetch_all_file_ids_via_api():
    if not GDRIVE_FOLDER_ID or "1PKox87" not in GDRIVE_FOLDER_ID: return []
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents+and+mimeType+contains+'image/'&key={GOOGLE_API_KEY}&fields=files(id)&pageSize=500"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200: return [f['id'] for f in response.json().get('files', [])]
    except: pass
    return []

def auto_sync_gdrive():
    current_file_ids = fetch_all_file_ids_via_api()
    new_file_ids = [fid for fid in current_file_ids if fid not in st.session_state["scanned_file_ids"]]
    if new_file_ids:
        batch_files = new_file_ids[:5]
        for f_idx, file_id in enumerate(batch_files):
            try:
                download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={GOOGLE_API_KEY}"
                req_file = requests.get(download_url, timeout=5)
                if req_file.status_code == 200:
                    raw_bytes = req_file.content
                    image = cv2.imdecode(np.asarray(bytearray(raw_bytes), dtype=np.uint8), 1)
                    if image is not None:
                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(60, 60))
                        if len(faces) > 0:
                            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            for (x, y, w, h) in faces:
                                face_resized = cv2.resize(gray[y:y+h, x:x+w], (40, 40))
                                st.session_state["face_images_db"].append({
                                    "feat": face_resized.tolist(), "img": image_rgb, 
                                    "img_id": f"gdrive_{file_id}_{f_idx}", "raw_bytes": raw_bytes
                                })
                    st.session_state["scanned_file_ids"].add(file_id)
            except: continue

auto_sync_gdrive()

# 7. เมนู
choice = st.sidebar.radio("เลือกหน้าต่าง:", ["หน้าหลักสำหรับสแกนรูป", "ฝั่งแอดมินสำหรับผู้จัดงาน"])

if choice == "หน้าหลักสำหรับสแกนรูป":
    uploaded_file = st.file_uploader("อัปโหลดรูปใบหน้าของคุณ", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
        if len(faces) == 0: st.error("❌ ไม่พบใบหน้า กรุณาอัปโหลดรูปที่เห็นหน้าชัดเจนครับ")
        else:
            x, y, w, h = faces[0]
            query_face = np.array(cv2.resize(gray[y:y+h, x:x+w], (40, 40)), dtype=np.float32)
            matched_items = [item for item in st.session_state["face_images_db"] 
                             if cv2.matchTemplate(np.array(item["feat"], dtype=np.float32), query_face, cv2.TM_CCOEFF_NORMED)[0][0] > 0.50]
            
            if matched_items:
                st.success(f"🎉 เจอรูปถ่ายของคุณ {len(matched_items)} รูป!")
                cols = st.columns(3)
                for idx, item in enumerate(matched_items):
                    with cols[idx % 3]:
                        st.image(item["img"], use_container_width=True)
                        st.download_button("📥 ดาวน์โหลด", item["raw_bytes"], f"photo_{idx}.jpg", use_container_width=True)
            else: st.warning("❌ ไม่พบรูปที่ตรงกัน")

elif choice == "ฝั่งแอดมินสำหรับผู้จัดงาน":
    if st.text_input("กรอกรหัสผ่าน:", type="password") == "2401":
        st.info(f"💡 จำนวนรูปที่สแกนแล้ว: {len(st.session_state['scanned_file_ids'])} รูป")
        if st.button("🗑️ ล้างคลังรูปภาพ"):
            st.session_state["face_images_db"] = []; st.session_state["scanned_file_ids"] = set(); st.rerun()
