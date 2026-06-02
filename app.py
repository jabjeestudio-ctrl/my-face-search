import streamlit as st
import cv2
import numpy as np
import requests

# 1. ตั้งค่าหน้าเว็บ: กาง Sidebar ออกทันที (แก้ปัญหาเมนูหาย)
st.set_page_config(page_title="Photo Finder System", layout="wide", initial_sidebar_state="expanded")

# 🎯 ระบบดีดทะลวง LINE
st.markdown("""
    <script>
    if (navigator.userAgent.indexOf('Line') > -1) {
        window.location.href = window.location.href + '?openExternalBrowser=1';
    }
    </script>
    """, unsafe_allow_html=True)

st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่าย (เวอร์ชันออโต้ 1 นาที)")

# 🛠️ เชื่อมต่อ Google Drive
GDRIVE_FOLDER_ID = "1PKox87btEZQDHSJ_0nZXm9aR1x3T74w0"
GOOGLE_API_KEY = "AIzaSyCuqZK1l-Vte0TN5KhatUSOm3xHwHIC6Ig"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# เก็บข้อมูลใน Memory
if "face_images_db" not in st.session_state:
    st.session_state["face_images_db"] = []
    st.session_state["scanned_file_ids"] = set()

# ฟังก์ชันดึงรูปอัตโนมัติ (Cached)
@st.cache_data(ttl=60)
def sync_drive():
    url = f"https://www.googleapis.com/drive/v3/files?q='{GDRIVE_FOLDER_ID}'+in+parents&key={GOOGLE_API_KEY}&pageSize=100"
    files = requests.get(url).json().get('files', [])
    for f in files:
        if f['id'] not in st.session_state["scanned_file_ids"]:
            # ดึงรูปมาประมวลผล...
            st.session_state["scanned_file_ids"].add(f['id'])
    return "Synced"

sync_drive()

# --- หน้าหลักสำหรับแขก ---
uploaded_file = st.file_uploader("📸 จิ้มเพื่อ [ถ่ายรูปสด] หรือ [เลือกรูปในเครื่อง]", type=["jpg", "png"], key="search")

if uploaded_file:
    # โค้ดสแกนใบหน้า...
    st.success("กำลังค้นหา...")

# --- เมนูหลังบ้าน (Sidebar) ---
st.sidebar.header("⚙️ เมนูควบคุมระบบ")
st.sidebar.write("ระบบดึงรูปจาก Drive อัตโนมัติทุก 1 นาที")
if st.sidebar.button("🗑️ ล้างคลังรูปภาพทั้งหมด"):
    st.session_state["face_images_db"] = []
    st.session_state["scanned_file_ids"] = set()
    st.rerun()
