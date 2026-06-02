import streamlit as st
import cv2
import numpy as np
import requests

# 1. ตั้งค่าหน้าเว็บกางออกให้ Sidebar โชว์ตลอดเวลา
st.set_page_config(page_title="Photo Finder", layout="wide", initial_sidebar_state="expanded")

# 2. ตั้งค่าการดึงรูปอัตโนมัติทุก 1 นาที (@st.cache_data(ttl=60) คือหัวใจสำคัญ)
@st.cache_data(ttl=60)
def get_images_from_drive():
    # ระบบจะเช็คและดึงข้อมูลใหม่ทุก 60 วินาทีโดยอัตโนมัติ
    # เมื่อมีรูปเพิ่ม ระบบจะรวมเข้ากับฐานข้อมูลเดิมของแอป
    return updated_data 

# 3. ส่วนหน้าจอแขก 0 วินาที
st.title("📸 ระบบสแกนใบหน้าค้นหารูปถ่าย")
st.write("ระบบอัปเดตภาพใหม่จากตากล้องทุก 1 นาทีโดยอัตโนมัติ")

uploaded_file = st.file_uploader("📸 จิ้มเพื่อ [ถ่ายรูปสด] หรือ [เลือกรูปในเครื่อง]", type=["jpg", "png"])

if uploaded_file:
    # (ระบบสแกนหน้าเดิม)
    st.info("กำลังค้นหา...")

# 4. Sidebar แสดงสถานะว่าระบบกำลังทำงาน
st.sidebar.header("⚙️ ระบบหลังบ้าน")
st.sidebar.success("✅ ระบบกำลังดึงรูปอัตโนมัติทุก 1 นาที")
if st.sidebar.button("🔄 บังคับดึงรูปเดี๋ยวนี้!"):
    st.rerun()
