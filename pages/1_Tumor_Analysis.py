# import streamlit as st
# import numpy as np
# import cv2
# import tensorflow as tf
# import os
# import gdown
# import sqlite3
# import warnings
# from datetime import datetime

# # إخفاء التحذيرات لضمان واجهة نظيفة
# warnings.filterwarnings("ignore")



# # تحديد مسار المجلد الرئيسي للمشروع
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# if "pages" in BASE_DIR:
#     BASE_DIR = os.path.dirname(BASE_DIR)

# # تحديث اسم قاعدة البيانات ليكون بمسار كامل
# DB_NAME = os.path.join(BASE_DIR, 'brain_tumor.db')

# # 1. إعدادات الصفحة
# st.set_page_config(page_title="BrainScan AI | Diagnosis", layout="wide", page_icon="🧠")

# # 2. التحقق من تسجيل الدخول
# if not st.session_state.get('logged_in', False):
#     st.warning("⚠️ يرجى تسجيل الدخول من الصفحة الرئيسية أولاً.")
#     st.page_link("Home.py", label="العودة لتسجيل الدخول", icon="🏠")
#     st.stop()

# # --- 3. دالة حفظ النتائج في قاعدة البيانات ---
# def save_patient_history(username, diagnosis, image_name):
#     try:
#         conn = sqlite3.connect(DB_NAME)
#         cursor = conn.cursor()
#         # إنشاء جدول السجل إذا لم يكن موجوداً
#         cursor.execute('''CREATE TABLE IF NOT EXISTS history 
#                           (username TEXT, diagnosis TEXT, image_name TEXT, date TEXT)''')
        
#         current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         cursor.execute("INSERT INTO history (username, diagnosis, image_name, date) VALUES (?, ?, ?, ?)", 
#                        (username, diagnosis, image_name, current_date))
#         conn.commit()
#         conn.close()
#         return True
#     except Exception as e:
#         st.error(f"خطأ في حفظ البيانات: {e}")
#         return False

# # --- 4. دالة تحميل الموديلات من Google Drive ---
# @st.cache_resource
# def load_all_models():
#     # IDs ملفات جوجل درايف (تأكد أنها العامة Anyone with the link)
#     classification_id = '1atz2SVbb9-IHnzRDiLRAjjae1az3caD6'
#     segmentation_id = '1CxuWXW9lFzixm_P0XosX8KF7n8ayfgly'

#     cls_path = "brain_tumor1.h5"
#     seg_path = "segmentation_model.h5"

#     if not os.path.exists(cls_path):
#         with st.spinner("جاري تحميل موديل التصنيف من Drive..."):
#             gdown.download(f'https://drive.google.com/uc?id={classification_id}', cls_path, quiet=False)

#     if not os.path.exists(seg_path):
#         with st.spinner("جاري تحميل موديل تحديد الموقع..."):
#             gdown.download(f'https://drive.google.com/uc?id={segmentation_id}', seg_path, quiet=False)

#     cls = tf.keras.models.load_model(cls_path)
#     seg = tf.keras.models.load_model(seg_path, compile=False)
#     return cls, seg

# try:
#     cls_model, seg_model = load_all_models()
# except Exception as e:
#     st.error(f"خطأ في تحميل الموديلات: {e}")
#     st.stop()

# # --- 5. الدوال البرمجية للمعالجة ---
# IMG_SIZE = (256, 256)

# def classify_image(img_rgb):
#     resized_img = cv2.resize(img_rgb, (150, 150))
#     input_img = np.expand_dims(resized_img, axis=0) 
#     preds = cls_model.predict(input_img)
    
#     confidence = np.max(preds) # أعلى نسبة يقين
#     p = np.argmax(preds, axis=1)[0]
    
#     # إذا كانت نسبة اليقين ضعيفة جداً (الموديل شاكك)
#     if confidence < 0.80: 
#         return "Invalid Image"
    
#     labels = ['Glioma Tumor', 'No Tumor', 'Meningioma Tumor', 'Pituitary Tumor']
#     return labels[p]

# def segment_image(img_rgb):
#     resized_img = cv2.resize(img_rgb, IMG_SIZE)
#     gray = cv2.cvtColor(resized_img, cv2.COLOR_RGB2GRAY)
#     gray = gray.astype(np.float32) / 255.0
#     gray = np.expand_dims(gray, axis=-1)
#     input_img = np.expand_dims(gray, axis=0)

#     pred_mask = seg_model.predict(input_img)[0]
#     pred_mask = (pred_mask > 0.5).astype(np.uint8)
    
#     mask_resized = cv2.resize(pred_mask, (img_rgb.shape[1], img_rgb.shape[0]))
#     mask_colored = np.zeros_like(img_rgb)
#     mask_colored[:, :, 0] = mask_resized * 255 
#     highlighted = cv2.addWeighted(img_rgb, 0.8, mask_colored, 0.5, 0)
#     return highlighted

# # --- 6. واجهة المستخدم ---
# st.title("🔬 نظام فحص وتشخيص أورام الدماغ")
# st.info(f"المستخدم الحالي: {st.session_state.get('user_email', 'Guest')}")

# uploaded_file = st.file_uploader("اختر صورة رنين مغناطيسي...", type=["jpg", "png", "jpeg"])

# if uploaded_file is not None:
#     file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
#     img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
#     img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#     with st.spinner('جاري التحليل واستخراج النتائج...'):
#         label_res = classify_image(img_rgb)
#         seg_res = segment_image(img_rgb)

#     col1, col2 = st.columns(2)

#     with col1:
#         st.subheader("📊 نتيجة التصنيف")
#         st.image(img_rgb, caption="الصورة الأصلية", use_container_width=True)
        
#         info = {
#             "Glioma Tumor": "ورم دبقي (عدواني)",
#             "Meningioma Tumor": "ورم سحائي (غالباً حميد)",
#             "Pituitary Tumor": "ورم غدة نخامية",
#             "No Tumor": "لا يوجد ورم - الحالة سليمة"
#         }
#         st.success(f"التشخيص: {label_res}")
#         st.info(f"الوصف: {info.get(label_res, '')}")

#         # --- إضافة زر حفظ الحالة ---
#         if st.button("💾 حفظ النتيجة في السجل الطبي"):
#             user_name = st.session_state.get('user_email', 'Guest')
#             if save_patient_history(user_name, label_res, uploaded_file.name):
#                 st.toast(f"تم حفظ حالة المريض بنجاح يا {user_name}!", icon="✅")

#     with col2:
#         st.subheader("📍 تحديد موقع الإصابة")
#         st.image(seg_res, caption="تحديد منطقة الورم (بالأحمر)", use_container_width=True)

# st.divider()
# # --- الانتقالات (تظهر دائماً في أسفل الصفحة) ---
# st.markdown("---") # خط فاصل
# nav_c1, nav_c2 = st.columns(2)

# with nav_c1:
#     # العودة للرئيسية (تأكد أن الملف اسمه Home.py في المجلد الرئيسي)
#     st.page_link("Home.py", label="العودة للرئيسية", icon="🏠", use_container_width=True)

# with nav_c2:
#     # الرابط لصفحة التقارير (تأكد من المسار الفعلي للملف داخل مجلد pages)
#     # ملاحظة: إذا كان الملف داخل مجلد pages، المسار يكون "pages/your_file.py"
#     try:
#         st.page_link("pages/2_Analytics.py", label="عرض التقارير", icon="📈", use_container_width=True)
#     except:
#         st.page_link("Home.py", label="صفحة التقارير غير متوفرة", icon="🚫")
    


# import streamlit as st
import numpy as np
import cv2
import tensorflow as tf
import sqlite3
from datetime import datetime
from io import BytesIO
import warnings
import SimpleITK as sitk
from radiomics import featureextractor
import streamlit as st
# مكتبات ReportLab للتقارير
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle

# إخفاء التحذيرات
warnings.filterwarnings("ignore")




# تحديد مسار المجلد الرئيسي للمشروع
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if "pages" in BASE_DIR:
    BASE_DIR = os.path.dirname(BASE_DIR)

# تحديث اسم قاعدة البيانات ليكون بمسار كامل
DB_NAME = os.path.join(BASE_DIR, 'brain_tumor.db')


# التحقق من تسجيل الدخول
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ يرجى تسجيل الدخول أولاً.")
    st.stop()

st.set_page_config(page_title="التحليل الشامل | BrainScan AI", layout="wide")

# --- الدوال التقنية ---

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


def save_to_db(diagnosis, img_name):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # 1. التأكد من إنشاء الجدول أولاً لتجنب خطأ no such table
        c.execute('''CREATE TABLE IF NOT EXISTS history 
                     (username TEXT, diagnosis TEXT, date TEXT, image_name TEXT)''')
        
        # 2. إدخال البيانات
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('INSERT INTO history (username, diagnosis, date, image_name) VALUES (?,?,?,?)', 
                  (st.session_state.user_email, diagnosis, date_now, img_name))
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"⚠️ خطأ أثناء محاولة حفظ البيانات: {e}")
def classify_image(img_rgb, model):
    resized = cv2.resize(img_rgb, (150, 150))
    input_img = resized.reshape(1, 150, 150, 3)
    preds = model.predict(input_img)
    labels = ['Glioma Tumor', 'No Tumor', 'Meningioma Tumor', 'Pituitary Tumor']
    return labels[np.argmax(preds)]

def segment_image(img_rgb, model):
    resized = cv2.resize(img_rgb, (256, 256))
    gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    input_tensor = np.expand_dims(np.expand_dims(gray, axis=-1), axis=0)
    pred_mask = model.predict(input_tensor)[0]
    mask = (pred_mask > 0.5).astype(np.uint8)
    mask_full = cv2.resize(mask, (img_rgb.shape[1], img_rgb.shape[0]))
    
    # تلوين منطقة الورم
    mask_colored = np.zeros_like(img_rgb)
    mask_colored[:, :, 0] = mask_full * 255 # اللون الأحمر
    highlighted = cv2.addWeighted(img_rgb, 0.8, mask_colored, 0.5, 0)
    return highlighted, mask_full

def get_radiomics_features(image_rgb, mask):
    try:
        gray_img = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        sitk_img = sitk.GetImageFromArray(gray_img.astype(np.float32))
        sitk_mask = sitk.GetImageFromArray(mask.astype(np.uint8))
        
        extractor = featureextractor.RadiomicsFeatureExtractor()
        extractor.disableAllFeatures()
        extractor.enableFeatureClassByName('firstorder')
        extractor.enableFeatureClassByName('shape2D')
        
        features = extractor.execute(sitk_img, sitk_mask)
        # تنظيف النتائج وتحويلها لأرقام
        clean_features = {k: float(v) if isinstance(v, (np.ndarray, np.generic)) else v 
                          for k, v in features.items() if 'diagnostics' not in k}
        return clean_features
    except:
        return {"Error": "منطقة الورم صغيرة جداً لاستخراج الخصائص."}

def create_pdf_report(img_orig, img_seg, diagnosis, radiomics, user_email):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("BrainScan AI - Medical Report", styles['Heading1']))
    elements.append(Paragraph(f"<b>Practitioner:</b> {user_email}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Diagnosis Result:</b> {diagnosis}", styles['Heading2']))
    elements.append(Spacer(1, 20))

    # دالة مساعدة لتحويل الصورة لـ Buffer لـ ReportLab
    def get_img_buf(arr):
        _, img_encoded = cv2.imencode(".png", cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
        return BytesIO(img_encoded.tobytes())

    img1 = Image(get_img_buf(img_orig), width=200, height=180)
    img2 = Image(get_img_buf(img_seg), width=200, height=180)
    elements.append(Table([[img1, img2]], colWidths=[220, 220]))
    elements.append(Spacer(1, 20))

    # جدول الخصائص
    data = [["Radiomics Feature", "Value"]]
    for i, (k, v) in enumerate(radiomics.items()):
        if i > 15: break # نكتفي بـ 15 خاصية في التقرير
        name = k.replace('original_firstorder_', '').replace('original_shape2D_', '')
        val = f"{v:.4f}" if isinstance(v, float) else str(v)
        data.append([name, val])
    
    t = Table(data, colWidths=[300, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('GRID',(0,0),(-1,-1),0.5,colors.grey),
        ('FONTSIZE', (0,0), (-1, -1), 10)
    ]))
    elements.append(t)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- واجهة المستخدم الرئيسية ---

st.title("🧠 التحليل المتقدم للرنين المغناطيسي")
cls_model, seg_model = load_all_models()

uploaded_file = st.file_uploader("قم برفع صورة الـ MRI (JPG/PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    with st.spinner('جاري إجراء التحليل العميق...'):
        # 1. التصنيف
        diagnosis = classify_image(img_rgb, cls_model)
        # 2. التقطيع (Segmentation)
        viz_img, mask_raw = segment_image(img_rgb, seg_model)
        # 3. الحفظ في قاعدة البيانات
        save_to_db(diagnosis, uploaded_file.name)

    # عرض النتائج المرئية
    st.success(f"النتيجة: {diagnosis}")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🖼️ الصورة الأصلية")
        st.image(img_rgb, use_container_width=True)
    with col2:
        st.subheader("🎯 منطقة الورم المكتشفة")
        st.image(viz_img, use_container_width=True)

    # استخراج الخصائص والتقرير في حالة وجود ورم
    if diagnosis != "No Tumor" and np.any(mask_raw):
        st.divider()
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("📊 الخصائص الإشعاعية (Radiomics)")
            feats = get_radiomics_features(img_rgb, mask_raw)
            # عرض أول 10 خصائص في جدول
            st.table(list(feats.items())[:10])
        
        with c2:
            st.subheader("📄 التقرير الطبي")
            st.info("يمكنك تحميل تقرير مفصل بصيغة PDF يحتوي على الصور والتحليلات.")
            pdf_data = create_pdf_report(img_rgb, viz_img, diagnosis, feats, st.session_state.user_email)
            st.download_button(
                label="📥 تحميل التقرير (PDF)",
                data=pdf_data,
                file_name=f"Report_{uploaded_file.name}.pdf",
                mime="application/pdf"
            )

# أزرار التنقل
st.divider()
b1, b2 = st.columns(2)
with b1:
    st.page_link("pages/2_Analytics.py",label="الذهاب الي لوحة الاحصائيات",icon="📊",use_container_width=True)
with b2:
    st.page_link("Home.py",label="العودة للرئيسية",icon="🏠",use_container_width=True)
