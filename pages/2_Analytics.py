import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# =========================
# 🔐 Check login
# =========================
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("يرجى تسجيل الدخول")
    st.stop()

# =========================
# 📁 DB Path
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if "pages" in BASE_DIR:
    BASE_DIR = os.path.dirname(BASE_DIR)

DB_NAME = os.path.join(BASE_DIR, 'brain_tumor.db')

# =========================
# 📊 Page Config
# =========================
st.set_page_config(page_title="لوحة البيانات", layout="wide")
st.title("📊 سجل التقارير والإحصائيات")

# =========================
# 📥 Load Data
# =========================
def load_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT * FROM history WHERE username=?",
        conn,
        params=(st.session_state.user_email,)
    )
    conn.close()
    return df

df = load_data()

# =========================
# 🚫 Handle Empty Data
# =========================
if df.empty:
    st.warning("لا توجد بيانات مسجلة لك بعد.")
    st.stop()

# =========================
# 🚫 Filter Low Confidence
# =========================
df_valid = df[df['diagnosis'] != "Unsupported Image / Low Confidence"].copy()
df_unsupported = df[df['diagnosis'] == "Unsupported Image / Low Confidence"].copy()

# =========================
# 📅 Fix date column
# =========================
df_valid['date'] = pd.to_datetime(df_valid['date'], errors='coerce')

# =========================
# 📊 Metrics
# =========================
c1, c2, c3 = st.columns(3)

c1.metric("إجمالي الفحوصات", len(df_valid))
c2.metric("حالات الأورام", len(df_valid[df_valid['diagnosis'] != 'No Tumor']))
c3.metric("الحالات السليمة", len(df_valid[df_valid['diagnosis'] == 'No Tumor']))

st.divider()

# =========================
# 📈 Charts
# =========================
col1, col2 = st.columns(2)

with col1:
    fig1 = px.pie(
        df_valid,
        names='diagnosis',
        title="نسب توزيع الحالات"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.line(
        df_valid.sort_values('date'),
        x='date',
        y='diagnosis',
        title="تطور الحالات زمنياً"
    )
    st.plotly_chart(fig2, use_container_width=True)

# =========================
# 📑 Table
# =========================
st.subheader("📑 الجدول التفصيلي")
st.dataframe(df_valid, use_container_width=True)

# =========================
# 🚫 Unsupported cases (optional view)
# =========================
if not df_unsupported.empty:
    st.warning("⚠️ تم استبعاد صور غير مدعومة من التحليل")
    st.subheader("🚫 Low Confidence Cases")
    st.dataframe(df_unsupported, use_container_width=True)

# =========================
# 🔗 Navigation
# =========================
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.page_link(
        "pages/1_Tumor_Analysis.py",
        label="اجراء فحص جديد",
        icon="🔍",
        use_container_width=True
    )

with col2:
    st.page_link(
        "Home.py",
        label="العودة للرئيسية",
        icon="🏠",
        use_container_width=True
    )
