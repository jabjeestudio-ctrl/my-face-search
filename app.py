import streamlit as st
import cv2
import numpy as np
import requests

# 1. ตั้งค่าแสดง Sidebar ตลอดเวลา
st.set_page_config(page_title="Photo Finder", layout="wide", initial_sidebar_state="expanded")

# --- โค้ดดึงรูปและสแกนหน้าแบบ Fast Index ---
# น้าเอาฟังก์ชันเดิมที่ใช้อยู่มาใส่ที่นี่ และเพิ่มระบบ Indexing ให้มันจำใบหน้าไว้ล่วงหน้า
# โค้ดส่วนนี้จะทำให้การค้นหาแทบไม่ต้องรอเวลาประมวลผลเพิ่มครับ
