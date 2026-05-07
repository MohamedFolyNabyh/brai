import streamlit as st
import pandas as pd

st.title("📊 التقارير والإحصائيات")

if not st.session_state.get('logged_in', False):
    st.warning("يرجى تسجيل الدخول.")
    st.stop()

st.write("هنا يمكنك عرض ملخص للحالات التي تم فحصها.")
# يمكنك إضافة رسوم بيانية هنا باستخدام Plotly أو Matplotlib
data = pd.DataFrame({
    'نوع الورم': ['Glioma', 'Meningioma', 'Pituitary', 'Normal'],
    'العدد': [12, 7, 5, 20]
})
st.bar_chart(data.set_index('نوع الورم'))