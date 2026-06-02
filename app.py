import streamlit as st
import cv2
import numpy as np

# ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง
st.set_page_config(page_title="Face Search System", layout="wide")

st.title("👤 ระบบค้นหาใบหน้าหน้างานอีเวนต์ (Upload Photo)")
st.write("👇 กดปุ่มด้านล่างเพื่ออัปโหลดรูปภาพใบหน้าและสแกนหาชื่อได้เลยครับ")

# โหลดตัวตรวจจับใบหน้ามาตรฐานของ OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ใช้ Session State ในการจำข้อมูลใบหน้า
if "face_db" not in st.session_state:
    st.session_state["face_db"] = {}  # {ชื่อ: รูปใบหน้า}

# สร้างเมนูฝั่งซ้ายมือ (Sidebar)
st.sidebar.header("⚙️ เมนูการใช้งาน")
menu = ["🏠 หน้าหลัก (อัปโหลดรูปสแกน)", "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)"]
choice = st.sidebar.radio("เลือกหน้าต่างที่ต้องการ:", menu)

# --- ปุ่มเคลียร์ข้อมูลด่วนฝั่ง Sidebar ---
if choice == "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)":
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ ล้างข้อมูลใบหน้าทั้งหมดในระบบ"):
        st.session_state["face_db"] = {}
        st.sidebar.success("ล้างข้อมูลเรียบร้อยแล้ว!")

# --- ฟังก์ชันช่วยประมวลผลสแกนและค้นหาใบหน้า ---
def process_and_search_face(image_bytes):
    file_bytes = np.asarray(bytearray(image_bytes), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # ตรวจหาใบหน้า
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) == 0:
        st.error("❌ 不พบใบหน้าในรูปภาพนี้ กรุณาใช้รูปที่เห็นใบหน้าตรงชัดเจนครับ")
    else:
        x, y, w, h = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        face_resized = cv2.resize(face_roi, (32, 32)).tolist()
        
        best_match = None
        min_diff = float("inf")
        
        # เปรียบเทียบกับฐานข้อมูลชั่วคราว
        for db_name, db_feat in st.session_state["face_db"].items():
            diff = np.sum(np.abs(np.array(db_feat) - np.array(face_resized)))
            if diff < min_diff:
                min_diff = diff
                best_match = db_name
        
        # แสดงผลลัพธ์ถ้าความต่างไม่เกินเกณฑ์
        if best_match and min_diff < 50000:  
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 4)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            st.image(image_rgb, caption="ผลการสแกนใบหน้า", use_container_width=True)
            st.success(f"
