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
# 🚫 Empty Check
# =========================
if df.empty:
    st.warning("لا توجد بيانات مسجلة لك بعد.")
    st.stop()

# =========================
# 🚫 Unsupported filter
# =========================
UNSUPPORTED = ["Not supported image", "Unsupported Image / Low Confidence"]

df_valid = df[~df['diagnosis'].isin(UNSUPPORTED)].copy()
df_unsupported = df[df['diagnosis'].isin(UNSUPPORTED)].copy()

# =========================
# 📅 Safe date conversion
# =========================
if 'date' in df_valid.columns:
    df_valid['date'] = pd.to_datetime(df_valid['date'], errors='coerce')
    df_valid = df_valid.dropna(subset=['date'])

# =========================
# 📊 Metrics
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("إجمالي الفحوصات", len(df))
c2.metric("حالات الأورام", len(df_valid[df_valid['diagnosis'] != 'No Tumor']))
c3.metric("الحالات السليمة", len(df_valid[df_valid['diagnosis'] == 'No Tumor']))
c4.metric("صور غير مدعومة", len(df_unsupported))

st.divider()

# =========================
# 📈 Charts
# =========================
col1, col2 = st.columns(2)

with col1:
    if not df_valid.empty:
        fig1 = px.pie(
            df_valid,
            names='diagnosis',
            title="نسب توزيع الحالات"
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("لا توجد بيانات صالحة للرسم")

with col2:
    if not df_valid.empty and 'date' in df_valid.columns:
        fig2 = px.line(
            df_valid.sort_values('date'),
            x='date',
            y='diagnosis',
            title="تطور الحالات زمنياً"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("لا توجد بيانات زمنية كافية")

# =========================
# 📑 Table (valid only)
# =========================
st.subheader("📑 البيانات الصالحة للتحليل")
st.dataframe(df_valid, use_container_width=True)

# =========================
# 🚫 Unsupported cases
# =========================
if not df_unsupported.empty:
    st.divider()
    st.warning("⚠️ صور غير مدعومة تم استبعادها من التحليل")

    st.subheader("🚫 الحالات غير المدعومة")
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
