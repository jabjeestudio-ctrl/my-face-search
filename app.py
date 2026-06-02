import streamlit as st
import cv2
import numpy as np

# ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง
st.set_page_config(page_title="Photo Finder System", layout="wide")

st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายทั้งหมดในงาน (เวอร์ชันรูปคู่/รูปกลุ่ม)")
st.write("👇 แขกอัปโหลดรูปตัวเอง เพื่อค้นหาภาพถ่ายทั้งหมดที่มีใบหน้าของคุณ (รวมถึงรูปคู่และรูปกลุ่ม) แบบชัดเต็มขั้น")

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

# --- หน้าที่ 1: หน้าหลักค้นหาใบหน้า (สำหรับแขกเล่น - รองรับรูปกลุ่ม ชัดเต็มสตรีม) ---
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
                
                # ลิสต์สำหรับเก็บทุกรูปที่หน้าตรงปกผ่านเกณฑ์ (ใช้ set เพื่อไม่ให้รูปซ้ำกรณีเจอหน้าตัวเองซ้ำในระบบ)
                matched_images = []
                seen_images = set()
                
                # วิ่งไล่เช็กกับคลังภาพ
                for item in st.session_state["face_images_db"]:
                    diff = np.sum(np.abs(np.array(item["feat"]) - np.array(face_resized)))
                    
                    # เกณฑ์ความแม่นยำตรงปก (38000)
                    if diff < 38000:  
                        # เช็กไอดีรูปภาพเพื่อป้องกันไม่ให้แสดงรูปซ้ำซ้อนบนหน้าจอ
                        if item["img_id"] not in seen_images:
                            matched_images.append(item["img"])
                            seen_images.add(item["img_id"])
                
                # --- แสดงผลลัพธ์ ---
                if len(matched_images) > 0:
                    st.success(f"🎉 เจอรูปถ่ายของคุณในระบบทั้งหมด {len(matched_images)} รูปครับ! (รวมรูปคู่/รูปกลุ่มของคุณ) 👇")
                    
                    # จัดเรียงรูปภาพแถวละ 2 รูปสวยๆ ขนาดคมชัดเต็มพิกเซล
                    cols = st.columns(2)
                    for idx, match_img in enumerate(matched_images):
                        with cols[idx % 2]:
                            st.image(match_img, caption=f"รูปที่ {idx + 1} (ขนาดต้นฉบับ)", use_container_width=True)
                else:
                    st.error("❌ ไม่พบรูปภาพที่ตรงกับใบหน้าของคุณในคลังภาพ")

# --- หน้าที่ 2: ฝั่งแอดมิน (ล็อกรหัส 2401 อัปโหลดคลังภาพกลุ่ม/เดี่ยว พร้อมกัน) ---
elif choice == "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)":
    st.subheader("🔒 กรุณาใส่รหัสผ่านแอดมินเพื่อเข้าสู่ระบบ")
    password = st.text_input("กรอกรหัสผ่านหลังบ้าน:", type="password")
    
    if password == "2401":
        st.success("🔓 รหัสผ่านถูกต้อง! ยินดีต้อนรับแอดมิน")
        st.write("---")
        
        st.subheader("📥 อัปโหลดคลังรูปภาพเข้าสู่ระบบ (รองรับรูปภาพคู่และรูปกลุ่ม)")
        
        # นับจำนวนรูปภาพที่ไม่ซ้ำกันในคลังปัจจุบัน
        unique_photos = len(set(item["img_id"] for item in st.session_state["ai_face_db"])) if "ai_face_db" in st.session_state and len(st.session_state["ai_face_db"]) > 0 else len(set(item["img_id"] for item in st.session_state["face_images_db"]))
        st.info(f"💡 ตอนนี้มีไฟล์รูปภาพในคลังทั้งหมด: {unique_photos} รูป")
        
        uploaded_files = st.file_uploader("เลือกรูปภาพถ่ายในงาน (อัปโหลดพร้อมกันได้หลายไฟล์ ทั้งรูปเดี่ยว รูปคู่ รูปกลุ่ม)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        
        if st.button("บันทึกรูปภาพทั้งหมดเข้าคลัง") and uploaded_files:
            success_img_count = 0
            
            for f_idx, f in enumerate(uploaded_files):
                file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, 1)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # สแกนหาใบหน้าทั้งหมดในภาพ (ถ้ารูปกลุ่ม มี 5 หน้า มันจะเจอครบเลยครับ)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    # สร้างไอดีเฉพาะให้รูปภาพใบนี้ เพื่อให้ระบบรู้ว่าเป็นรูปเดียวกันแม้เจอหลายใบหน้า
                    img_id = f"{f.name}_{f_idx}_{len(st.session_state['face_images_db'])}"
                    
                    # แตกหน้าทุกคนที่เจอในภาพนี้ออกมาบันทึกรหัสแยกกัน
                    for (x, y, w, h) in faces:
                        face_roi = gray[y:y+h, x:x+w]
                        face_resized = cv2.resize(face_roi, (32, 32)).tolist()
                        
                        # บันทึกรหัสของหน้านั้นคู่กับภาพต้นฉบับใบใหญ่เต็มๆ
                        st.session_state["face_images_db"].append({
                            "feat": face_resized,
                            "img": image_rgb,    # ตัวนี้คือรูปขนาดเต็มดั้งเดิม ไม่โดนบีบย่อยครับ
                            "img_id": img_id
                        })
                    success_img_count += 1
            
            if success_img_count > 0:
                st.success(f"✔️ นำเข้ารูปภาพสำเร็จ {success_img_count} รูป! (ระบบทำการสแกนเก็บใบหน้าทุกคนในภาพเรียบร้อยแล้ว)")
                st.rerun() 
            else:
                st.error("❌ รูปภาพที่อัปโหลดไม่มีใบหน้าที่ระบบตรวจจับได้เลย")
                
    elif password != "":
        st.error("❌ รหัสผ่านไม่ถูกต้อง!")
