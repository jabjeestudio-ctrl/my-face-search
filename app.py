import streamlit as st
import cv2
import numpy as np

# ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง
st.set_page_config(page_title="Photo Finder System", layout="wide")

st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่ายในงาน (เวอร์ชันดาวน์โหลด & ส่งไลน์)")
st.write("👇 แขกอัปโหลดรูปตัวเอง เพื่อค้นหารูปทั้งหมดในงาน สามารถกดดาวน์โหลดหรือแชร์เข้า LINE ได้ทันที")

# โหลดตัวตรวจจับใบหน้ามาตรฐานของ OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ใช้ Session State ในการจำข้อมูลใบหน้าและรูปภาพเต็ม
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []  # [{"feat": feature, "img": image_rgb, "img_id": id, "raw_bytes": bytes}]

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

# --- หน้าที่ 1: หน้าหลักค้นหาใบหน้า (ระบบซ่อมแซมปุ่มแชร์ LINE) ---
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
                
                # ลิสต์สำหรับเก็บรูปที่ตรงปกผ่านเกณฑ์
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
                    
                    # จัดเรียงรูปภาพแถวละ 2 รูปสวยๆ
                    cols = st.columns(2)
                    for idx, item in enumerate(matched_items):
                        with cols[idx % 2]:
                            # 1. แสดงรูปขนาดเต็มต้นฉบับ
                            st.image(item["img"], caption=f"รูปที่ {idx + 1} (ชัดเต็มพิกเซล)", use_container_width=True)
                            
                            # 2. ทำปุ่มดาวน์โหลดรูปภาพ
                            st.download_button(
                                label=f"📥 ดาวน์โหลดรูปที่ {idx + 1}",
                                data=item["raw_bytes"],
                                file_name=f"event_photo_{idx+1}.jpg",
                                mime="image/jpeg",
                                key=f"dl_{idx}"
                            )
                            
                            # 3. ปุ่มส่งต่อเข้า LINE แบบเรียบง่ายแต่นิ่งสนิท ไม่พังชัวร์ครับน้า
                            # พอแขกกดปุ่มนี้ หน้าจอแชร์ลิงก์ของ LINE จะเด้งขึ้นมาให้แขกกดส่งต่อให้ตัวเองหรือเพื่อนได้ทันที
                            line_share_url = "https://social-plugins.line.me/lineit/share?url=" + "https://yiday4hy.streamlit.app"
                            st.markdown(f'<a href="{line_share_url}" target="_blank"><button style="background-color:#06C755; color:white; border:none; padding:8px 16px; border-radius:4px; cursor:pointer; width:100%; font-weight:bold;">🟢 ส่งต่อ / แชร์เว็บเข้า LINE</button></a>', unsafe_allow_html=True)
                            st.write("") # เว้นวรรคช่องไฟ
                else:
                    st.error("❌ ไม่พบรูปภาพที่ตรงกับใบหน้าของคุณในคลังภาพ")

# --- หน้าที่ 2: ฝั่งแอดมิน (ล็อกรหัส 2401 อัปโหลดคลังภาพ) ---
elif choice == "🔒 ฝั่งแอดมิน (เฉพาะผู้จัดงาน)":
    st.subheader("🔒 กรุณาใส่รหัสผ่านแอดมินเพื่อเข้าสู่ระบบ")
    password = st.text_input("กรอกรหัสผ่านหลังบ้าน:", type="password")
    
    if password == "2401":
        st.success("🔓 รหัสผ่านถูกต้อง! ยินดีต้อนรับแอดมิน")
        st.write("---")
        
        st.subheader("📥 อัปโหลดคลังรูปภาพเข้าสู่ระบบ (รองรับรูปเดี่ยว/คู่/กลุ่ม)")
        unique_photos = len(set(item["img_id"] for item in st.session_state["face_images_db"]))
        st.info(f"💡 ตอนนี้มีไฟล์รูปภาพในคลังทั้งหมด: {unique_photos} รูป")
        
        uploaded_files = st.file_uploader("เลือกรูปภาพถ่ายในงาน (อัปโหลดพร้อมกันได้หลายไฟล์)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        
        if st.button("บันทึกรูปภาพทั้งหมดเข้าคลัง") and uploaded_files:
            success_img_count = 0
            
            for f_idx, f in enumerate(uploaded_files):
                # อ่านไฟล์ดิบเก็บไวก่อนทำปุ่มดาวน์โหลดต้นฉบับ
                raw_bytes = f.read()
                
                file_bytes = np.asarray(bytearray(raw_bytes), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, 1)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    img_id = f"{f.name}_{f_idx}_{len(st.session_state['face_images_db'])}"
                    
                    # วนลูปบันทึกรหัสทุกคนที่เจอในรูปนั้น
                    for (x, y, w, h) in faces:
                        face_roi = gray[y:y+h, x:x+w]
                        face_resized = cv2.resize(face_roi, (32, 32)).tolist()
                        
                        st.session_state["face_images_db"].append({
                            "feat": face_resized,
                            "img": image_rgb,
                            "img_id": img_id,
                            "raw_bytes": raw_bytes # ผูกไฟล์ดิบขนาดเต็มไว้สำหรับให้กดโหลด
                        })
                    success_img_count += 1
            
            if success_img_count > 0:
                st.success(f"✔️ นำเข้ารูปภาพสำเร็จ {success_img_count} รูปเรียบร้อย!")
                st.rerun()
            else:
                st.error("❌ รูปภาพที่อัปโหลดไม่มีใบหน้าที่ระบบตรวจจับได้เลย")
                
    elif password != "":
        st.error("❌ รหัสผ่านไม่ถูกต้อง!")
