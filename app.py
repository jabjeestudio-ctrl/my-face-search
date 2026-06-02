import streamlit as st
import cv2
import numpy as np
import requests
import face_recognition
import sqlite3
import io

# 1. เชื่อมต่อ Database (เก็บข้อมูลไว้ในไฟล์ database.db ข้อมูลจะไม่หายถ้าเว็บรีโหลด)
def init_db():
    conn = sqlite3.connect('faces.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS face_db 
                 (id INTEGER PRIMARY KEY, file_id TEXT, encoding BLOB, image_bytes BLOB)''')
    conn.commit()
    conn.close()

# 2. ฟังก์ชันแปลงรูปเป็น Encoding (หัวใจสำคัญของความเร็ว)
def get_encoding(image_bgr):
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, boxes)
    return encodings[0].tobytes() if encodings else None

# 3. ฟังก์ชันบันทึกลง DB
def save_to_db(file_id, encoding, image_bytes):
    conn = sqlite3.connect('faces.db')
    c = conn.cursor()
    c.execute("INSERT INTO face_db (file_id, encoding, image_bytes) VALUES (?, ?, ?)", 
              (file_id, encoding, image_bytes))
    conn.commit()
    conn.close()

# --- ในฟังก์ชัน auto_sync_gdrive ของคุณ ให้เปลี่ยนส่วนการเก็บข้อมูลเป็น: ---
# encoding = get_encoding(image)
# if encoding:
#     save_to_db(file_id, encoding, raw_bytes)

# --- ในหน้าค้นหา (ส่วนที่ผู้ใช้อัปโหลดรูป) ---
if uploaded_file:
    # 1. แปลงรูปที่อัปโหลดเป็น Encoding
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    query_enc = face_recognition.face_encodings(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    if query_enc:
        query_enc = query_enc[0]
        # 2. ดึง Encoding จาก Database มาเทียบ (เร็วมาก)
        conn = sqlite3.connect('faces.db')
        c = conn.cursor()
        c.execute("SELECT encoding, image_bytes FROM face_db")
        rows = c.fetchall()
        
        matches = []
        for row in rows:
            db_enc = np.frombuffer(row[0], dtype=np.float64)
            # เปรียบเทียบความคล้าย
            if face_recognition.compare_faces([db_enc], query_enc, tolerance=0.5)[0]:
                matches.append(row[1])
        conn.close()
        
        # 3. แสดงรูปที่เจอ
        for m in matches:
            st.image(m)
