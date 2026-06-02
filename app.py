# --- ปรับแต่งหน้าตาให้สวยงาม (Custom CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; }
    .css-1r6slb0 { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stSuccess, .stError { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ปรับ Layout ให้น่ารักขึ้น
st.markdown("## 📸 Photo Finder : ค้นหาความทรงจำของคุณ")
st.markdown("---")

# --- ส่วนของการค้นหา (หน้าหลัก) ---
if choice == "หน้าหลักสำหรับสแกนรูป":
    # กล่องอัปโหลดแบบดีไซน์ใหม่
    col1, col2 = st.columns([1, 2])
    with col1:
        uploaded_file = st.file_uploader("อัปโหลดรูปใบหน้าของคุณ", type=["jpg", "jpeg", "png"], key="search_photo")
        st.info("💡 เคล็ดลับ: ใช้รูปที่เห็นใบหน้าชัดเจน เพื่อการค้นหาที่แม่นยำที่สุดครับ")
    
    with col2:
        if uploaded_file:
            # (ส่วนประมวลผล Logic ของคุณเหมือนเดิม)
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
            
            if len(faces) == 0:
                st.error("❌ ไม่พบใบหน้า กรุณาอัปโหลดรูปที่เห็นหน้าชัดๆ")
            else:
                # ... (Logic ค้นหาของคุณเหมือนเดิม) ...
                if len(matched_items) > 0:
                    st.balloons() # เพิ่มเอฟเฟกต์พลุ
                    st.success(f"🎉 เจอรูปของคุณทั้งหมด {len(matched_items)} รูป!")
                    
                    # แสดงรูปในรูปแบบ Grid สวยงาม
                    grid = st.columns(3)
                    for idx, item in enumerate(matched_items):
                        with grid[idx % 3]:
                            st.image(item["img"], use_container_width=True)
                            st.download_button(label="📥 ดาวน์โหลด", data=item["raw_bytes"], file_name=f"photo_{idx}.jpg", use_container_width=True)
                else:
                    st.warning("⚠️ ไม่พบรูปที่ตรงกัน ลองใช้รูปอื่นดูนะครับ")

# --- ส่วนของหลังบ้าน ---
elif choice == "ฝั่งแอดมินสำหรับผู้จัดงาน":
    st.markdown("### 🔒 แผงควบคุมระบบ (Admin)")
    password = st.text_input("กรอกรหัสผ่านเพื่อเข้าสู่ระบบ:", type="password")
    if password == "2401":
        st.success("🔓 ระบบพร้อมใช้งาน")
        st.metric("จำนวนรูปในคลัง", len(st.session_state["face_images_db"]))
        st.write("---")
        if st.button("🗑️ ล้างคลังรูปภาพ (Reset)", type="primary"):
            st.session_state["face_images_db"] = []
            st.session_state["scanned_file_ids"] = set()
            st.rerun()
