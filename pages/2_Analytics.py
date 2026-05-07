

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px # مكتبة رائعة للرسوم التفاعلية

# 1. إعدادات الصفحة
st.set_page_config(page_title="BrainScan AI | Dashboard", layout="wide", page_icon="📊")

DB_NAME = 'brain_tumor.db'
# 2. التحقق من تسجيل الدخول
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ يرجى تسجيل الدخول أولاً للوصول إلى التقارير.")
    st.page_link("Home.py", label="العودة للرئيسية", icon="🏠")
    st.stop()

st.title("📊 سجل التقارير والإحصائيات")
current_user = st.session_state.get('username', 'Guest')
st.info(f"مرحباً دكتور {current_user}، إليك ملخص لجميع الحالات التي قمت بفحصها.")

# --- 3. دالة جلب البيانات من قاعدة البيانات ---
def fetch_user_history(username):
    try:
        conn = sqlite3.connect(DB_NAME)
        # قراءة البيانات مباشرة في DataFrame
        query = "SELECT diagnosis as 'نوع التشخيص', date as 'التاريخ', image_name as 'اسم الصورة' FROM history WHERE username = ?"
        df = pd.read_sql_query(query, conn, params=(username,))
        conn.close()
        return df
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {e}")
        return pd.DataFrame()

# جلب البيانات
df_history = fetch_user_history(current_user)

if df_history.empty:
    st.warning("📭 لا توجد سجلات محفوظة لهذا المستخدم حتى الآن.")
else:
    # --- 4. عرض الإحصائيات (الرسوم البيانية) ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📈 توزيع الحالات المشخصة")
        # حساب تكرار كل نوع تشخيص
        stats = df_history['نوع التشخيص'].value_counts().reset_index()
        stats.columns = ['نوع التشخيص', 'العدد']
        
        # رسم بياني تفاعلي باستخدام Plotly
        fig = px.bar(stats, x='نوع التشخيص', y='العدد', 
                     color='نوع التشخيص', 
                     text_auto=True,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📋 ملخص سريع")
        total_cases = len(df_history)
        normal_cases = len(df_history[df_history['نوع التشخيص'] == 'No Tumor'])
        tumor_cases = total_cases - normal_cases
        
        st.metric("إجمالي الفحوصات", total_cases)
        st.metric("حالات الإصابة المؤكدة", tumor_cases, delta_color="inverse")
        st.metric("الحالات السليمة", normal_cases)

    # --- 5. عرض الجدول التفصيلي ---
    st.divider()
    st.subheader("📑 سجل الفحوصات التفصيلي")
    
    # تحسين عرض الجدول
    st.dataframe(df_history, use_container_width=True, hide_index=True)

    # إضافة خيار لتحميل البيانات كملف Excel أو CSV
    csv = df_history.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 تحميل السجل كملف CSV",
        data=csv,
        file_name=f'history_{current_user}.csv',
        mime='text/csv',
    )

# 6. التذييل
st.divider()
st.page_link("pages/1_Tumor_Analysis.py", label="الذهاب لإجراء فحص جديد", icon="🧠")
st.page_link("Home.py", label="العودة للرئيسية", icon="🏠")
