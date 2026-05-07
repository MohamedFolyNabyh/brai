import streamlit as st

st.title("🛠 أدوات طبية مساعدة")

st.info("هذا القسم مخصص للموارد الطبية السريعة.")

with st.expander("📚 معلومات عن أنواع الأورام"):
    st.write("- **Glioma:** يبدأ في الخلايا الدبقية.")
    st.write("- **Meningioma:** ينشأ من الأغشية المحيطة بالدماغ.")
    st.write("- **Pituitary:** يصيب الغدة النخامية.")
    

st.text_area("ملاحظات الطبيب (للحفظ المؤقت):", placeholder="اكتب ملاحظاتك هنا...")