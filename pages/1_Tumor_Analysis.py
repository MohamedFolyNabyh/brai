import streamlit as st
import numpy as np
import cv2
import tensorflow as tf
import os
import gdown
import sqlite3
import warnings
from datetime import datetime

# إخفاء التحذيرات لضمان واجهة نظيفة
warnings.filterwarnings("ignore")

# 1. إعدادات الصفحة
st.set_page_config(page_title="BrainScan AI | Diagnosis", layout="wide", page_icon="🧠")

# 2. التحقق من تسجيل الدخول
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ يرجى تسجيل الدخول من الصفحة الرئيسية أولاً.")
    st.page_link("Home.py", label="العودة لتسجيل الدخول", icon="🏠")
    st.stop()

# --- 3. دالة حفظ النتائج في قاعدة البيانات ---
def save_patient_history(username, diagnosis, image_name):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        # إنشاء جدول السجل إذا لم يكن موجوداً
        cursor.execute('''CREATE TABLE IF NOT EXISTS history 
                          (username TEXT, diagnosis TEXT, image_name TEXT, date TEXT)''')
        
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO history (username, diagnosis, image_name, date) VALUES (?, ?, ?, ?)", 
                       (username, diagnosis, image_name, current_date))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"خطأ في حفظ البيانات: {e}")
        return False

# --- 4. دالة تحميل الموديلات من Google Drive ---
@st.cache_resource
def load_all_models():
    # IDs ملفات جوجل درايف (تأكد أنها العامة Anyone with the link)
    classification_id = '1atz2SVbb9-IHnzRDiLRAjjae1az3caD6'
    segmentation_id = '1CxuWXW9lFzixm_P0XosX8KF7n8ayfgly'

    cls_path = "brain_tumor1.h5"
    seg_path = "segmentation_model.h5"

    if not os.path.exists(cls_path):
        with st.spinner("جاري تحميل موديل التصنيف من Drive..."):
            gdown.download(f'https://drive.google.com/uc?id={classification_id}', cls_path, quiet=False)

    if not os.path.exists(seg_path):
        with st.spinner("جاري تحميل موديل تحديد الموقع..."):
            gdown.download(f'https://drive.google.com/uc?id={segmentation_id}', seg_path, quiet=False)

    cls = tf.keras.models.load_model(cls_path)
    seg = tf.keras.models.load_model(seg_path, compile=False)
    return cls, seg

try:
    cls_model, seg_model = load_all_models()
except Exception as e:
    st.error(f"خطأ في تحميل الموديلات: {e}")
    st.stop()

# --- 5. الدوال البرمجية للمعالجة ---
IMG_SIZE = (256, 256)

def classify_image(img_rgb):
    resized_img = cv2.resize(img_rgb, (150, 150))
    input_img = np.expand_dims(resized_img, axis=0) 
    preds = cls_model.predict(input_img)
    
    confidence = np.max(preds) # أعلى نسبة يقين
    p = np.argmax(preds, axis=1)[0]
    
    # إذا كانت نسبة اليقين ضعيفة جداً (الموديل شاكك)
    if confidence < 0.80: 
        return "Invalid Image"
    
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
    
    mask_resized = cv2.resize(pred_mask, (img_rgb.shape[1], img_rgb.shape[0]))
    mask_colored = np.zeros_like(img_rgb)
    mask_colored[:, :, 0] = mask_resized * 255 
    highlighted = cv2.addWeighted(img_rgb, 0.8, mask_colored, 0.5, 0)
    return highlighted

# --- 6. واجهة المستخدم ---
st.title("🔬 نظام فحص وتشخيص أورام الدماغ")
st.info(f"المستخدم الحالي: {st.session_state.get('username', 'Guest')}")

uploaded_file = st.file_uploader("اختر صورة رنين مغناطيسي...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    with st.spinner('جاري التحليل واستخراج النتائج...'):
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

        # --- إضافة زر حفظ الحالة ---
        if st.button("💾 حفظ النتيجة في السجل الطبي"):
            user_name = st.session_state.get('username', 'Guest')
            if save_patient_history(user_name, label_res, uploaded_file.name):
                st.toast(f"تم حفظ حالة المريض بنجاح يا {user_name}!", icon="✅")

    with col2:
        st.subheader("📍 تحديد موقع الإصابة")
        st.image(seg_res, caption="تحديد منطقة الورم (بالأحمر)", use_container_width=True)

    st.divider()
    st.page_link("Home.py", label="🏠 العودة للرئيسية", icon="⬅️")
