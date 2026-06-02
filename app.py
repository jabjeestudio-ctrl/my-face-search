import streamlit as st
import cv2
import numpy as np

# ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง
st.set_page_config(page_title="Photo Finder System", layout="wide")

st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายทั้งหมดในงาน")
st.write("👇 แขกอัปโหลดรูปตัวเอง เพื่อค้นหาภาพถ่าย 'ทั้งหมด' ของตัวเองในระบบคลังภาพได้เลยครับ")

# โหลดตัวตรวจจับใบหน้ามาตรฐานของ OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ใช้ Session State ในการจำข้อมูลใบหน้าและรูปภาพเต็ม
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []  # เก็บลิสต์ของ dict: [{"feat": feature, "img": image_rgb}]

# สร้างเมนูฝั่งซ้ายมือ (Sidebar)
st.sidebar.header("⚙️ เมนูการใช้งาน")
menu = ["🏠 หน้าหลัก (สำหรับแขกสแกนรูป)", "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)"]
choice = st.sidebar.radio("เลือกหน้าต่างที่ต้องการ:", menu)

# --- ปุ่มเคลียร์ข้อมูลด่วนฝั่ง Sidebar ---
if choice == "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)":
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ ล้างคลังรูปภาพทั้งหมดในระบบ"):
        st.session_state["face_images_db"] = []
        st.sidebar.success("ล้างข้อมูลเรียบร้อยแล้ว!")

# --- หน้าที่ 1: หน้าหลักค้นหาใบหน้า (สำหรับแขกเล่น - โชว์ทุกรูปที่หน้าเหมือน) ---
if choice == "🏠 หน้าหลัก (สำหรับแขกสแกนรูป)":
    if len(st.session_state["face_images_db"]) == 0:
        st.warning("⚠️ คลังรูปภาพยังว่างอยู่ (กรุณาให้แอดมินใส่รหัสผ่านเข้ามาอัปโหลดรูปภาพต้นแบบก่อนครับ)")
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
                
                # ลิสต์สำหรับเก็บทุกรูปที่หน้าคล้ายกันผ่านเกณฑ์
                matched_images = []
                
                # วิ่งไล่เช็ก "ทุกรูป" ในคลังภาพ
                for item in st.session_state["face_images_db"]:
                    diff = np.sum(np.abs(np.array(item["feat"]) - np.array(face_resized)))
                    
                    # ถ้าค่าความต่างน้อยกว่า 52000 (แปลว่าหน้าคล้ายกันมากพอ) ให้เก็บรูปนั้นไว้
                    if diff < 52000:  
                        matched_images.append(item["img"])
                
                # --- แสดงผลลัพธ์ ---
                if len(matched_images) > 0:
                    st.success(f"🎉 เจอรูปถ่ายของคุณในระบบทั้งหมด {len(matched_images)} รูปครับ! ดูด้านล่างได้เลย 👇")
                    
                    # จัดเรียงรูปภาพให้แสดงเป็นแถว แถวละ 2 รูปสวยๆ ไม่ยาวเป็นหางว่าวลงไปข้างล่าง
                    cols = st.columns(2)
                    for idx, match_img in enumerate(matched_images):
                        with cols[idx % 2]:
                            st.image(match_img, caption=f"รูปที่ {idx + 1}", use_container_width=True)
                else:
                    st.error("❌ ไม่พบรูปภาพที่ตรงกับใบหน้าของคุณในระบบคลังภาพ")

# --- หน้าที่ 2: ฝั่งแอดมิน (ล็อกรหัส 2401 อัปโหลดทีละเยอะๆ) ---
elif choice == "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)":
    st.subheader("🔒 กรุณาใส่รหัสผ่านแอดมินเพื่อเข้าสู่ระบบ")
    password = st.text_input("กรอกรหัสผ่านหลังบ้าน:", type="password")
    
    if password == "2401":
        st.success("🔓 รหัสผ่านถูกต้อง! ยินดีต้อนรับแอดมิน")
        st.write("---")
        
        st.subheader("📥 อัปโหลดคลังรูปภาพเข้าสู่ระบบ (ไม่ต้องพิมพ์ชื่อ)")
        st.info(f"💡 ตอนนี้มีรูปภาพในคลังทั้งหมด: {len(st.session_state['face_images_db'])} รูป")
        
        uploaded_files = st.file_uploader("เลือกรูปภาพถ่ายแขกในงาน (เลือกได้หลายรูปพร้อมกัน)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        
        if st.button("บันทึกรูปภาพทั้งหมดเข้าคลัง") and uploaded_files:
            success_count = 0
            for f in uploaded_files:
                file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, 1)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    face_roi = gray[y:y+h, x:x+w]
                    face_resized = cv2.resize(face_roi, (32, 32)).tolist()
                    
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    st.session_state["face_images_db"].append({
                        "feat": face_resized,
                        "img": image_rgb
                    })
                    success_count += 1
            
            if success_count > 0:
                st.success(f"✔️ นำเข้าและตรวจเจอใบหน้าสำเร็จทั้งหมด {success_count} รูปเรียบร้อยแล้ว!")
                st.rerun() # รีเฟรชหน้าจอหลังบ้านเพื่อให้ตัวเลขสถิติมันอัปเดตทันที
            else:
                st.error("❌ รูปภาพที่อัปโหลดไม่มีใบหน้าที่ระบบตรวจจับได้เลย")
                
    elif password != "":
        st.error("❌ รหัสผ่านไม่ถูกต้อง!")
