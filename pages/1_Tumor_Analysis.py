import streamlit as st
import numpy as np
import cv2
import tensorflow as tf
import matplotlib.pyplot as plt
import warnings

# إخفاء التحذيرات لضمان واجهة نظيفة
warnings.filterwarnings("ignore")

# 1. إعدادات الصفحة
st.set_page_config(page_title="Brain Tumor AI", layout="wide", page_icon="🧠")

# 2. التحقق من تسجيل الدخول (اختياري حسب نظامك)
if not st.session_state.get('logged_in', False):
    st.warning("يرجى تسجيل الدخول من الصفحة الرئيسية أولاً.")
    st.stop()

# 3. تحميل الموديلات مع التخزين المؤقت لسرعة الأداء
@st.cache_resource
def load_all_models():
    # تأكد من صحة المسارات على جهازك
    cls = tf.keras.models.load_model(r"C:\Users\DELL\Downloads\brain_tumor1.h5")
    seg = tf.keras.models.load_model(r"C:\Users\DELL\Downloads\segmentation_model (1).h5", compile=False)
    return cls, seg

try:
    cls_model, seg_model = load_all_models()
except Exception as e:
    st.error(f"خطأ في تحميل الموديلات: {e}")
    st.stop()

# 4. دالة التصنيف (Classification)
IMG_SIZE = (256, 256)

# ==== دالة التصنيف ====
def classify_image(img_rgb):
    resized_img = cv2.resize(img_rgb, (150, 150))
    input_img = resized_img.reshape(1, 150, 150, 3)
    preds = cls_model.predict(input_img)
    p = np.argmax(preds, axis=1)[0]
    labels = ['Glioma Tumor', 'No Tumor', 'Meningioma Tumor', 'Pituitary Tumor']
    return labels[p]

# ==== دالة الـ segmentation ====
def segment_image(img_rgb):
    resized_img = cv2.resize(img_rgb, IMG_SIZE)
    gray = cv2.cvtColor(resized_img, cv2.COLOR_RGB2GRAY)
    gray = gray.astype(np.float32) / 255.0
    gray = np.expand_dims(gray, axis=-1)
    input_img = np.expand_dims(gray, axis=0)

    pred_mask = seg_model.predict(input_img)[0]
    pred_mask = (pred_mask > 0.5).astype(np.uint8)
    mask_resized = cv2.resize(pred_mask, (img_rgb.shape[1], img_rgb.shape[0]))

    mask_colored = np.zeros_like(img_rgb)
    mask_colored[:, :, 0] = mask_resized * 255
    highlighted = cv2.addWeighted(img_rgb, 0.8, mask_colored, 0.5, 0)

    return highlighted

# 6. واجهة المستخدم (Streamlit UI)
st.title("🔬 نظام فحص وتشخيص أورام الدماغ")
st.write("قم برفع صورة رنين مغناطيسي (MRI) للحصول على تحليل فوري.")

uploaded_file = st.file_uploader("اختر صورة...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # قراءة الصورة وتحويلها
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # تنفيذ المهام
    with st.spinner('جاري التحليل...'):
        label_res = classify_image(img_rgb)
        seg_res = segment_image(img_rgb)

    # عرض النتائج
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 نتيجة التصنيف")
        st.image(img_rgb, caption="الصورة الأصلية", use_container_width=True)
        
        # معلومات توضيحية
        info = {
            "Glioma Tumor": "ورم دبقي (عدواني)",
            "Meningioma Tumor": "ورم سحائي (غالباً حميد)",
            "Pituitary Tumor": "ورم غدة نخامية",
            "No Tumor": "لا يوجد ورم - الحالة سليمة"
        }
        st.success(f"التشخيص: {label_res}")
        st.info(f"الوصف: {info.get(label_res, '')}")

    with col2:
        st.subheader("📍 موقع الإصابة")
        st.image(seg_res, caption="تحديد الورم باللون الأحمر", use_container_width=True)

    # زر العودة
    st.divider()
    st.page_link("Home.py", label="🏠 العودة للرئيسية")