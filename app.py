import streamlit as st
import cv2
import numpy as np
import requests
import mediapipe as mp

# 1. ตั้งค่า
st.set_page_config(page_title="AI Photo Finder", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #f0f2f6; }
    [data-testid="stFileUploader"] { background: white; border: 2px dashed #4a90e2; border-radius: 15px; }
    div.stButton > button { background-color: #4a90e2; color: white; border-radius: 10px; }
</style>""", unsafe_allow_html=True)

# 2. AI Setup
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"

if "db" not in st.session_state: st.session_state.db = []
if "scanned_ids" not in st.session_state: st.session_state.scanned_ids = set()

# 3. ฟังก์ชัน AI สแกน
def process_images():
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents&key={GOOGLE_API_KEY}"
    files = requests.get(url).json().get('files', [])
    for f in files:
        if f['id'] not in st.session_state.scanned_ids:
            img_data = requests.get(f"https://www.googleapis.com/drive/v3/files/{f['id']}?alt=media&key={GOOGLE_API_KEY}").content
            img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            res = face_detection.process(rgb)
            if res.detections:
                st.session_state.db.append({"feat": res.detections[0].location_data.relative_keypoints, "img": rgb, "raw": img_data})
            st.session_state.scanned_ids.add(f['id'])

# 4. หน้าจอ
menu = st.sidebar.radio("เลือก:", ["ค้นหา", "แอดมิน"])
if menu == "แอดมิน":
    if st.button("ดึงรูปใหม่"): process_images()
    st.write(f"สแกนแล้ว: {len(st.session_state.scanned_ids)} รูป")
else:
    up = st.file_uploader("อัปโหลดรูปหน้าของคุณ")
    if up:
        user_img = cv2.imdecode(np.frombuffer(up.read(), np.uint8), cv2.IMREAD_COLOR)
        user_res = face_detection.process(cv2.cvtColor(user_img, cv2.COLOR_BGR2RGB))
        if user_res.detections:
            u_feat = user_res.detections[0].location_data.relative_keypoints
            found = False
            for item in st.session_state.db:
                # คำนวณระยะห่างจุดใบหน้า
                diff = sum([abs(item["feat"][i].x - u_feat[i].x) + abs(item["feat"][i].y - u_feat[i].y) for i in range(len(u_feat))])
                if diff < 0.3: # ค่าความแม่นยำ
                    st.image(item["img"], caption="เจอรูปนี้ในงาน!")
                    st.download_button("ดาวน์โหลด", item["raw"], "result.jpg")
                    found = True
            if not found: st.warning("ไม่พบรูปที่ตรงกัน")
        else: st.error("ไม่พบหน้าในรูปที่อัปโหลด")
