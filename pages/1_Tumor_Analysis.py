import streamlit as st
import numpy as np
import cv2
import tensorflow as tf
import os
import gdown
import warnings

# إخفاء التحذيرات
warnings.filterwarnings("ignore")

# 1. إعدادات الصفحة
st.set_page_config(page_title="Brain Tumor AI", layout="wide", page_icon="🧠")

# 2. التحقق من تسجيل الدخول
if not st.session_state.get('logged_in', False):
    st.warning("يرجى تسجيل الدخول من الصفحة الرئيسية أولاً.")
    st.stop()

# --- 3. دالة تحميل الموديلات من Google Drive ---
@st.cache_resource
def load_all_models():
    # استبدل هذه الـ IDs بالـ IDs الحقيقية لملفاتك من جوجل درايف
    classification_id = '1atz2SVbb9-IHnzRDiLRAjjae1az3caD6'
    segmentation_id = '1CxuWXW9lFzixm_P0XosX8KF7n8ayfgly'

    # أسماء الملفات التي سيتم حفظها في السيرفر
    cls_path = "brain_tumor1.h5"
    seg_path = "segmentation_model.h5"

    # تحميل موديل التصنيف إذا لم يكن موجوداً
    if not os.path.exists(cls_path):
        with st.spinner("جاري تحميل موديل التصنيف من Google Drive..."):
            gdown.download(f'https://drive.google.com/uc?id={classification_id}', cls_path, quiet=False)

    # تحميل موديل الـ Segmentation إذا لم يكن موجوداً
    if not os.path.exists(seg_path):
        with st.spinner("جاري تحميل موديل تحديد الموقع..."):
            gdown.download(f'https://drive.google.com/uc?id={segmentation_id}', seg_path, quiet=False)

    # تحميل الموديلات في الذاكرة
    cls = tf.keras.models.load_model(cls_path)
    seg = tf.keras.models.load_model(seg_path, compile=False)
    return cls, seg

# محاولة تحميل الموديلات
try:
    cls_model, seg_model = load_all_models()
except Exception as e:
    st.error(f"خطأ في تحميل الموديلات: {e}")
    st.info("تأكد من أن روابط Google Drive عامة (Anyone with the link can view)")
    st.stop()

# --- 4. الدوال البرمجية (كما هي مع تعديل بسيط في التصنيف) ---
IMG_SIZE = (256, 256)

def classify_image(img_rgb):
    # الموديل يتوقع 150x150 بناءً على كودك السابق
    resized_img = cv2.resize(img_rgb, (150, 150))
    # تطبيع الصورة (Normalization) إذا كان الموديل تدرب على ذلك
    input_img = np.expand_dims(resized_img, axis=0) 
    preds = cls_model.predict(input_img)
    p = np.argmax(preds, axis=1)[0]
    labels = ['Glioma Tumor', 'No Tumor', 'Meningioma Tumor', 'Pituitary Tumor']
    return labels[p]

def segment_image(img_rgb):
    resized_img = cv2.resize(img_rgb, IMG_SIZE)
    gray = cv2.cvtColor(resized_img, cv2.COLOR_RGB2GRAY)
    gray = gray.astype(np.float32) / 255.0
    gray = np.expand_dims(gray, axis=-1)
    input_img = np.expand_dims(gray, axis=0)

    pred_mask = seg_model.predict(input_img)[0]
    pred_mask = (pred_mask > 0.5).astype(np.uint8)
    
    # تحجيم الماسك ليتناسب مع الصورة الأصلية المرفوعة
    mask_resized = cv2.resize(pred_mask, (img_rgb.shape[1], img_rgb.shape[0]))

    mask_colored = np.zeros_like(img_rgb)
    mask_colored[:, :, 0] = mask_resized * 255 # تلوين الورم بالأحمر
    highlighted = cv2.addWeighted(img_rgb, 0.8, mask_colored, 0.5, 0)

    return highlighted

# --- 6. واجهة المستخدم ---
st.title("🔬 نظام فحص وتشخيص أورام الدماغ")
st.write("قم برفع صورة رنين مغناطيسي (MRI) للحصول على تحليل فوري.")

uploaded_file = st.file_uploader("اختر صورة...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    with st.spinner('جاري التحليل...'):
        label_res = classify_image(img_rgb)
        seg_res = segment_image(img_rgb)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 نتيجة التصنيف")
        st.image(img_rgb, caption="الصورة الأصلية", use_container_width=True)
        
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

    st.divider()
    st.page_link("Home.py", label="🏠 العودة للرئيسية")
