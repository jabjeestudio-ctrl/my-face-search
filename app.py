import streamlit as st
from supabase import create_client

# 1. ใส่กุญแจ (URL และ KEY)
SUPABASE_URL = "https://nwhevupzbbrstqejqzfd.supabase.co"
SUPABASE_KEY = "sb_publishable_z4Iziju2EIVToTU5MJzr3g_er6_Q6Lr"

# 2. เชื่อมต่อ
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("📸 ระบบสแกนใบหน้า")

# 3. ลองทดสอบการเชื่อมต่อ
if st.button("กดเช็คข้อมูล"):
    try:
        data = sb.table("faces_db").select("*").execute()
        st.write("เชื่อมต่อสำเร็จ! ตอนนี้มีข้อมูลในตาราง:", len(data.data), "รายการ")
    except Exception as e:
        st.error(f"เชื่อมต่อไม่ได้: {e}")
