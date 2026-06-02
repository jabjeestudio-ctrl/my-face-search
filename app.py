import streamlit as str
import cv2
import chromadb
import numpy as np
from chromadb.config import Settings

st.set_page_config(page_title="Face Search System", layout="wide")

st.title("👤 ระบบสแกนและค้นหาใบหน้า (Local Version)")
st.write("ระบบนี้ทำงานบนคลาวด์ได้ 100% ไม่ต้องใช้ Google Drive หรือดึงตัวดั้งเดิมที่ติดตั้งยาก")

# โหลดตัวตรวจจับใบหน้ามาตรฐานของ OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# เชื่อมต่อฐานข้อมูล ChromaDB ในเครื่องเซิร์ฟเวอร์
try:
    chroma_client = chromadb.Client()
    collection = chroma_client.get_or_create_collection(name="face_signatures")
except Exception as e:
    st.error(f"ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {e}")

menu = ["🏠 หน้าหลัก (ค้นหาใบหน้า)", "📥 ฝั่งแอดมิน (เพิ่มรูปภาพใบหน้า)"]
choice = st.sidebar.selectbox("เมนูการใช้งาน", menu)

# --- ฝั่งแอดมิน ---
if choice == "📥 ฝั่งแอดมิน (เพิ่มรูปภาพใบหน้า)":
    st.subheader("📥 เพิ่มรูปภาพใบหน้าต้นแบบเข้าสู่ระบบ")
    name = st.text_input("กรอกชื่อ-นามสกุล ของบุคคลในภาพ:")
    uploaded_file = st.file_uploader("เลือกรูปภาพใบหน้า (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    if st.button("บันทึกข้อมูลใบหน้า") and uploaded_file and name:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # ตรวจหาใบหน้าในรูป
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            st.error("❌ ไม่พบใบหน้าในรูปภาพนี้ กรุณาใช้รูปที่เห็นใบหน้าชัดเจน")
        else:
            # คำนวณค่าฟีเจอร์แบบง่ายจากขนาดและพิกเซล (เพื่อใช้แทนโมเดลเดิมที่ลงไม่ได้)
            x, y, w, h = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_roi, (32, 32))
            flattened_features = face_resized.flatten().tolist()
            
            # บันทึกลงฐานข้อมูล ChromaDB
            collection.add(
                embeddings=[flattened_features],
                documents=[name],
                ids=[f"id_{name}_{np.random.randint(1000,9999)}"]
            )
            st.success(f"✔️ บันทึกใบหน้าของ '{name}' เข้าสู่ระบบเรียบร้อยแล้ว!")

# --- หน้าหลักค้นหาใบหน้า ---
elif choice == "🏠 หน้าหลัก (ค้นหาใบหน้า)":
    st.subheader("🔍 อัปโหลดรูปภาพเพื่อค้นหาบุคคล")
    uploaded_file = st.file_uploader("อัปโหลดรูปภาพที่ต้องการสแกนหาตัวตน", type=["jpg", "jpeg", "png"])
    
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
            face_resized = cv2.resize(face_roi, (32, 32))
            flattened_features = face_resized.flatten().tolist()
            
            # ตรวจสอบว่าในฐานข้อมูลมีข้อมูลไหม
            if collection.count() == 0:
                st.warning("⚠️ ยังไม่มีข้อมูลใบหน้าในระบบ (กรุณาให้แอดมินเพิ่มข้อมูลก่อน)")
            else:
                # ค้นหาในฐานข้อมูล ChromaDB
                results = collection.query(
                    query_embeddings=[flattened_features],
                    n_results=1
                )
                
                if results and results['documents'] and len(results['documents'][0]) > 0:
                    matched_name = results['documents'][0][0]
                    
                    # วาดกรอบสี่เหลี่ยมรอบใบหน้า
                    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 4)
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    st.image(image_rgb, caption="ผลการสแกนใบหน้า", use_container_width=True)
                    st.success(f"🎉 ตรวจพบใบหน้าในระบบ! บุคคลนี้คือ: **{matched_name}**")
                else:
                    st.error("❌ ไม่พบข้อมูลบุคคลนี้ในระบบฐานข้อมูล")
