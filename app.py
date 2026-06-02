import streamlit as st
import cv2
import numpy as np
import requests

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Photo Finder System", layout="wide")

# --- 2. ประกาศฟังก์ชันทั้งหมดที่นี่ (ห้ามเรียกใช้ฟังก์ชันในส่วนนี้) ---
def fetch_all_file_ids_via_api():
    # ... (โค้ดฟังก์ชันเดิมของคุณ) ...
    return []

def auto_sync_gdrive():
    # ... (โค้ดฟังก์ชันเดิมของคุณ) ...
    pass

# --- 3. สร้างเมนู ---
menu = ["หน้าหลักสำหรับสแกนรูป", "ฝั่งแอดมินสำหรับผู้จัดงาน"]
choice = st.sidebar.radio("เลือกหน้าต่างที่ต้องการ:", menu)

# --- 4. ส่วนแสดงผล (เรียกใช้ฟังก์ชันในนี้) ---
if choice == "หน้าหลักสำหรับสแกนรูป":
    # เรียกใช้ที่นี่เท่านั้น
    auto_sync_gdrive() 
    
    st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่าย")
    uploaded_file = st.file_uploader("อัปโหลดรูปภาพใบหน้าของคุณ", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        # ... (โค้ดประมวลผลรูป) ...
        pass

elif choice == "ฝั่งแอดมินสำหรับผู้จัดงาน":
    # ... (โค้ดส่วน Admin) ...
