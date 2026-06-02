import streamlit as st
import cv2
import numpy as np

# ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง
st.set_page_config(page_title="Face Search System", layout="wide")

st.title("👤 ระบบสแกนใบหน้าหน้างานอีเวนต์ (Live Camera)")
st.write("👇 ยืนตรงหน้ากล้องแล้วกดปุ่ม **Take Photo** เพื่อสแกนหาชื่อได้เลยครับ")

# โหลดตัวตรวจจับใบหน้ามาตรฐานของ OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ใช้ Session State ในการจำข้อมูลใบหน้า
if "face_db" not in st.session_state:
    st.session_state["face_db"] = {}  # {ชื่อ: รูปใบหน้า}

# สร้างเมนูฝั่งซ้ายมือ (Sidebar)
st.sidebar.header("⚙️ เมนูการใช้งาน")
menu = ["🏠 หน้าหลัก (กล้องสแกนใบหน้า)", "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)"]
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
        st.error("❌ ไม่พบใบหน้าในรูปภาพ กรุณาขยับหน้าให้อยู่ตรงกลางกล้องชัดๆ ครับ")
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
            st.success(f"🎉 ตรวจพบใบหน้าในระบบ! ยินดีต้อนรับ: **{best_match}**")
        else:
            st.error("❌ ไม่พบข้อมูลบุคคลนี้ในระบบฐานข้อมูล (กรุณาลงทะเบียนกับแอดมินก่อนครับ)")


# --- หน้าที่ 1: หน้าหลักค้นหาใบหน้า (เปิดกล้องสดอย่างเดียว ไม่มีปุ่มเลือกวิธีสแกนให้งง) ---
if choice == "🏠 หน้าหลัก (กล้องสแกนใบหน้า)":
    if len(st.session_state["face_db"]) == 0:
        st.warning("⚠️ ระบบยังไม่มีข้อมูลใบหน้าต้นแบบ (กรุณาสลับไปเมนูแอดมินทางซ้ายมือเพื่อใส่รหัสผ่านและเพิ่มรูปภาพก่อนครับ)")
    else:
        # เปิดกล้องให้แขกส่องถ่ายรูปทันทีแบบไม่ต้องเลือก
        camera_img = st.camera_input("กล้องสแกนใบหน้า")
        if camera_img:
            process_and_search_face(camera_img.read())


# --- หน้าที่ 2: ฝั่งแอดมิน (ล็อกรหัสผ่านรหัส 2401) ---
elif choice == "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)":
    st.subheader("🔒 กรุณาใส่รหัสผ่านแอดมินเพื่อเข้าสู่ระบบ")
    
    password = st.text_input("กรอกรหัสผ่านหลังบ้าน:", type="password")
    
    if password == "2401":
        st.success("🔓 รหัสผ่านถูกต้อง! ยินดีต้อนรับแอดมิน")
        st.write("---")
        
        st.subheader("📥 เพิ่มรูปภาพใบหน้าต้นแบบเข้าสู่ระบบ")
        name = st.text_input("กรอกชื่อ-นามสกุล ของบุคคลในภาพ:")
        
        # หลังบ้านแอดมิน ถ่ายจากกล้องสดเก็บชื่อได้เลยเหมือนกัน ง่ายดีครับ
        camera_img = st.camera_input("ถ่ายรูปต้นแบบจากกล้อง", key="add_face_cam")
        img_bytes = None
        if camera_img:
            img_bytes = camera_img.read()
                
        if st.button("บันทึกข้อมูลใบหน้า") and name and img_bytes:
            file_bytes = np.asarray(bytearray(img_bytes), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                st.error("❌ ไม่พบใบหน้าในรูปภาพนี้ กรุณาขยับให้เห็นหน้าชัดเจนแล้วลองอีกครั้ง")
            else:
                x, y, w, h = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face_roi, (32, 32))
                
                st.session_state["face_db"][name] = face_resized.tolist()
                st.success(f"✔️ บันทึกใบหน้าของ '{name}' เข้าสู่ระบบเรียบร้อยแล้ว!")
                st.info(f"💡 ตอนนี้ในระบบมีข้อมูลใบหน้าทั้งหมด {len(st.session_state['face_db'])} คน")
                
    elif password != "":
        st.error("❌ รหัสผ่านไม่ถูกต้อง! แขกในงานห้ามเข้านะครับ")
