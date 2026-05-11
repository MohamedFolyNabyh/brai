import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("يرجى تسجيل الدخول")
    st.stop()


# تحديد مسار المجلد الرئيسي للمشروع
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if "pages" in BASE_DIR:
    BASE_DIR = os.path.dirname(BASE_DIR)

# تحديث اسم قاعدة البيانات ليكون بمسار كامل
DB_NAME = os.path.join(BASE_DIR, 'brain_tumor.db')


st.set_page_config(page_title="لوحة البيانات", layout="wide")

st.title("📊 سجل التقارير والإحصائيات")


def load_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM history WHERE username=?", 
                           conn, params=(st.session_state.user_email,))
    conn.close()
    return df

df = load_data()

if df.empty:
    st.warning("لا توجد بيانات مسجلة لك بعد.")
else:
    # بطاقات سريعة
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الفحوصات", len(df))
    c2.metric("حالات الأورام", len(df[df['diagnosis'] != 'No Tumor']))
    c3.metric("الحالات السليمة", len(df[df['diagnosis'] == 'No Tumor']))

    # رسوم بيانية
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(df, names='diagnosis', title="نسب توزيع الحالات")
        st.plotly_chart(fig1)
    with col2:
        # ترتيب زمني بسيط
        df['date'] = pd.to_datetime(df['date'])
        fig2 = px.line(df.sort_values('date'), x='date', y='diagnosis', title="تطور الحالات زمنياً")
        st.plotly_chart(fig2)

    st.subheader("📑 الجدول التفصيلي")
    st.dataframe(df, use_container_width=True)

st.divider()

col1, col2=st.columns(2)
with col1:
    st.page_link("pages/1_Tumor_Analysis.py",label="اجراء فحص جديد",icon="🔍",use_container_width=True)
    

with col2:
    st.page_link("Home.py", label="العودة للرئيسية", icon="🏠", use_container_width=True)
    
