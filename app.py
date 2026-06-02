import streamlit as st
import cv2
import numpy as np

# ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง
st.set_page_config(page_title="Face Search System", layout="wide")

st.title("👤 ระบบสแกนและค้นหาใบหน้า (Cloud Version)")
st.write("เวอร์ชันเสถียรสูง รันบนเซิร์ฟเวอร์ Streamlit ได้ทันที ไม่ติดล็อกฐานข้อมูล")

# โหลดตัวตรวจจับใบหน้ามาตรฐานของ OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ใช้ Session State ในการจำข้อมูลใบหน้า
if "face_db" not in st.session_state:
    st.session_state["face_db"] = {}  # {ชื่อ: รูปใบหน้า}

# สร้างเมนูฝั่งซ้ายมือ (Sidebar) ให้โผล่แน่นอน
st.sidebar.header("⚙️ เมนูการใช้งาน")
menu = ["🏠 หน้าหลัก (ค้นหาใบหน้า)", "📥 ฝั่งแอดมิน (เพิ่มรูปภาพใบหน้า)"]
choice = st.sidebar.radio("เลือกหน้าต่างที่ต้องการ:", menu)

# --- ปุ่มเคลียร์ข้อมูลกรณีอยากล้างระบบ ---
if st.sidebar.button("🗑️ ล้างข้อมูลใบหน้าทั้งหมด"):
    st.session_state["face_db"] = {}
    st.sidebar.success("ล้างข้อมูลเรียบร้อยแล้ว!")

# --- หน้าที่ 1: หน้าหลักค้นหาใบหน้า ---
if choice == "🏠 หน้าหลัก (ค้นหาใบหน้า)":
    st.subheader("🔍 อัปโหลดรูปภาพเพื่อค้นหาบุคคล")
    
    if len(st.session_state["face_db"]) == 0:
        st.warning("⚠️ ยังไม่มีข้อมูลใบหน้าในระบบ (กรุณาสลับไปที่เมนู '📥 ฝั่งแอดมิน (เพิ่มรูปภาพใบหน้า)' ที่แถบซ้ายมือก่อนครับ)")
    else:
        uploaded_file = st.file_uploader("อัปโหลดรูปภาพที่ต้องการสแกนหาตัวตน", type=["jpg", "jpeg", "png"], key="search_face")
        
        if uploaded_file:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                st.error("❌ ไม่พบใบหน้าในรูปภาพที่ส่งมา")
            else:
                x, y, w, h = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face_roi, (32, 32)).tolist()
                
                best_match = None
                min_diff = float("inf")
                
                for db_name, db_feat in st.session_state["face_db"].items():
                    diff = np.sum(np.abs(np.array(db_feat) - np.array(face_resized)))
                    if diff < min_diff:
                        min_diff = diff
                        best_match = db_name
                
                if best_match and min_diff < 50000:  
                    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 4)
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    st.image(image_rgb, caption="ผลการสแกนใบหน้า", use_container_width=True)
                    st.success(f"🎉 ตรวจพบใบหน้าในระบบ! บุคคลนี้คือ: **{best_match}**")
                else:
                    st.error("❌ ไม่พบข้อมูลบุคคลนี้ในระบบฐานข้อมูล")

# --- หน้าที่ 2: ฝั่งแอดมิน ---
elif choice == "📥 ฝั่งแอดมิน (เพิ่มรูปภาพใบหน้า)":
    st.subheader("📥 เพิ่มรูปภาพใบหน้าต้นแบบเข้าสู่ระบบ")
    name = st.text_input("กรอกชื่อ-นามสกุล ของบุคคลในภาพ:")
    uploaded_file = st.file_uploader("เลือกรูปภาพใบหน้า (JPG/PNG)", type=["jpg", "jpeg", "png"], key="add_face")
    
    if st.button("บันทึกข้อมูลใบหน้า") and uploaded_file and name:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            st.error("❌ ไม่พบใบหน้าในรูปภาพนี้ กรุณาใช้รูปที่เห็นใบหน้าชัดเจน")
        else:
            x, y, w, h = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_roi, (32, 32))
            
            st.session_state["face_db"][name] = face_resized.tolist()
            st.success(f"✔️ บันทึกใบหน้าของ '{name}' เข้าสู่ระบบเรียบร้อยแล้ว!")
            st.info(f"💡 ตอนนี้ในระบบมีข้อมูลใบหน้าทั้งหมด {len(st.session_state['face_db'])} คน")
