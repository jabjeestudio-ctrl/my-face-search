# --- ส่วนบนของไฟล์คงไว้เหมือนเดิม ---
import streamlit as st
import cv2
import numpy as np
import requests

st.set_page_config(page_title="Photo Finder System", layout="wide")

# (ใส่ฟังก์ชันต่างๆ ของคุณไว้ที่นี่เหมือนเดิม รวมถึง auto_sync_gdrive)
# ... [ฟังก์ชัน fetch_all_file_ids_via_api และ auto_sync_gdrive อยู่ที่นี่] ...

# 7. สร้างเมนูฝั่งซ้ายมือ (Sidebar)
st.sidebar.header("⚙️ เมนูการใช้งาน")
menu = ["หน้าหลักสำหรับสแกนรูป", "ฝั่งแอดมินสำหรับผู้จัดงาน"]
choice = st.sidebar.radio("เลือกหน้าต่างที่ต้องการ:", menu)

# --- หน้าที่ 1: หน้าหลักค้นหาใบหน้า ---
if choice == "หน้าหลักสำหรับสแกนรูป":
    # เรียกใช้การ Sync ตรงนี้เพื่อให้ทำงานเฉพาะตอนที่เลือกหน้านี้
    # และย้ายมาไว้ข้างในเงื่อนไข if เพื่อป้องกัน IndentationError
    auto_sync_gdrive() 
    
    uploaded_file = st.file_uploader("อัปโหลดรูปภาพใบหน้าของคุณเพื่อค้นหารูปในงาน", type=["jpg", "jpeg", "png"], key="search_photo")
    
    if uploaded_file:
        # ... (โค้ดสแกนใบหน้าของคุณ) ...
        # (ตรวจสอบให้แน่ใจว่าโค้ดบรรทัดถัดจาก if มีการย่อหน้าเข้าไป 4 เคาะเสมอ)

# --- หน้าที่ 2: ฝั่งแอดมิน ---
elif choice == "ฝั่งแอดมินสำหรับผู้จัดงาน":
    st.subheader("🔒 กรุณาใส่รหัสผ่านแอดมินเพื่อเข้าสู่ระบบ")
    password = st.text_input("กรอกรหัสผ่านหลังบ้าน:", type="password")
    if password == "2401":
        st.success("🔓 รหัสผ่านถูกต้อง!")
        # ... (โค้ดส่วน Admin) ...
