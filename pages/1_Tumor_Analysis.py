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
import os
import gdown

# مكتبات ReportLab للتقارير
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle
)

# إخفاء التحذيرات
warnings.filterwarnings("ignore")

# =========================================================
# Paths
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if "pages" in BASE_DIR:
    BASE_DIR = os.path.dirname(BASE_DIR)

DB_NAME = os.path.join(BASE_DIR, 'brain_tumor.db')

# =========================================================
# Check Login
# =========================================================

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ يرجى تسجيل الدخول أولاً.")
    st.stop()

st.set_page_config(
    page_title="التحليل الشامل | BrainScan AI",
    layout="wide"
)

# =========================================================
# Load Models
# =========================================================

@st.cache_resource
def load_all_models():

    classification_id = '1atz2SVbb9-IHnzRDiLRAjjae1az3caD6'
    segmentation_id = '1CxuWXW9lFzixm_P0XosX8KF7n8ayfgly'

    cls_path = "brain_tumor1.h5"
    seg_path = "segmentation_model.h5"

    if not os.path.exists(cls_path):
        with st.spinner("جاري تحميل موديل التصنيف من Drive..."):
            gdown.download(
                f'https://drive.google.com/uc?id={classification_id}',
                cls_path,
                quiet=False
            )

    if not os.path.exists(seg_path):
        with st.spinner("جاري تحميل موديل تحديد الموقع..."):
            gdown.download(
                f'https://drive.google.com/uc?id={segmentation_id}',
                seg_path,
                quiet=False
            )

    cls = tf.keras.models.load_model(cls_path)

    seg = tf.keras.models.load_model(
        seg_path,
        compile=False
    )

    return cls, seg

# =========================================================
# Save To DB
# =========================================================

def save_to_db(diagnosis, img_name):

    try:

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS history
            (
                username TEXT,
                diagnosis TEXT,
                date TEXT,
                image_name TEXT
            )
        ''')

        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute(
            '''
            INSERT INTO history
            (username, diagnosis, date, image_name)
            VALUES (?, ?, ?, ?)
            ''',
            (
                st.session_state.user_email,
                diagnosis,
                date_now,
                img_name
            )
        )

        conn.commit()
        conn.close()

    except Exception as e:
        st.error(f"⚠️ خطأ أثناء محاولة حفظ البيانات: {e}")

# =========================================================
# Classification
# =========================================================

def classify_image(img_rgb, model):

    resized = cv2.resize(img_rgb, (150, 150))

    input_img = resized.reshape(1, 150, 150, 3)

    preds = model.predict(input_img)

    confidence = np.max(preds)

    if confidence < 0.8:
        return "not valid image"

    if confidence < 0.90:
        return "Not supported image"

    labels = [
        'Glioma Tumor',
        'No Tumor',
        'Meningioma Tumor',
        'Pituitary Tumor'
    ]

    return labels[np.argmax(preds)]

# =========================================================
# Segmentation
# =========================================================

def segment_image(img_rgb, model):

    resized = cv2.resize(img_rgb, (256, 256))

    gray = cv2.cvtColor(
        resized,
        cv2.COLOR_RGB2GRAY
    ).astype(np.float32) / 255.0

    input_tensor = np.expand_dims(
        np.expand_dims(gray, axis=-1),
        axis=0
    )

    pred_mask = model.predict(input_tensor)[0]

    mask = (pred_mask > 0.5).astype(np.uint8)

    mask_full = cv2.resize(
        mask,
        (img_rgb.shape[1], img_rgb.shape[0])
    )

    mask_colored = np.zeros_like(img_rgb)

    mask_colored[:, :, 0] = mask_full * 255

    highlighted = cv2.addWeighted(
        img_rgb,
        0.8,
        mask_colored,
        0.5,
        0
    )

    return highlighted, mask_full

# =========================================================
# Radiomics
# =========================================================

def get_radiomics_features(image_rgb, mask):

    try:

        gray_img = cv2.cvtColor(
            image_rgb,
            cv2.COLOR_RGB2GRAY
        )

        sitk_img = sitk.GetImageFromArray(
            gray_img.astype(np.float32)
        )

        sitk_mask = sitk.GetImageFromArray(
            mask.astype(np.uint8)
        )

        extractor = featureextractor.RadiomicsFeatureExtractor()

        extractor.disableAllFeatures()

        extractor.enableFeatureClassByName('firstorder')

        extractor.enableFeatureClassByName('shape2D')

        features = extractor.execute(
            sitk_img,
            sitk_mask
        )

        clean_features = {
            k: float(v)
            if isinstance(v, (np.ndarray, np.generic))
            else v
            for k, v in features.items()
            if 'diagnostics' not in k
        }

        return clean_features

    except:
        return {
            "Error": "منطقة الورم صغيرة جداً لاستخراج الخصائص."
        }

# =========================================================
# PDF Report
# =========================================================

def create_pdf_report(
    img_orig,
    img_seg,
    diagnosis,
    radiomics,
    user_email
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter
    )

    elements = []

    styles = getSampleStyleSheet()

    elements.append(
        Paragraph(
            "BrainScan AI - Medical Report",
            styles['Heading1']
        )
    )

    elements.append(
        Paragraph(
            f"<b>Practitioner:</b> {user_email}",
            styles['Normal']
        )
    )

    elements.append(
        Paragraph(
            f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles['Normal']
        )
    )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            f"<b>Diagnosis Result:</b> {diagnosis}",
            styles['Heading2']
        )
    )

    elements.append(Spacer(1, 20))

    def get_img_buf(arr):

        _, img_encoded = cv2.imencode(
            ".png",
            cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        )

        return BytesIO(img_encoded.tobytes())

    img1 = Image(
        get_img_buf(img_orig),
        width=200,
        height=180
    )

    img2 = Image(
        get_img_buf(img_seg),
        width=200,
        height=180
    )

    elements.append(
        Table(
            [[img1, img2]],
            colWidths=[220, 220]
        )
    )

    elements.append(Spacer(1, 20))

    data = [["Radiomics Feature", "Value"]]

    for i, (k, v) in enumerate(radiomics.items()):

        if i > 15:
            break

        name = k.replace(
            'original_firstorder_',
            ''
        ).replace(
            'original_shape2D_',
            ''
        )

        val = f"{v:.4f}" if isinstance(v, float) else str(v)

        data.append([name, val])

    t = Table(
        data,
        colWidths=[300, 100]
    )

    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 10)
    ]))

    elements.append(t)

    doc.build(elements)

    buffer.seek(0)

    return buffer

# =========================================================
# UI
# =========================================================

st.title("🧠 التحليل المتقدم للرنين المغناطيسي")

cls_model, seg_model = load_all_models()

uploaded_file = st.file_uploader(
    "قم برفع صورة الـ MRI (JPG/PNG)",
    type=["jpg", "png", "jpeg"]
)

if uploaded_file:

    file_bytes = np.asarray(
        bytearray(uploaded_file.read()),
        dtype=np.uint8
    )

    img = cv2.imdecode(file_bytes, 1)

    img_rgb = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2RGB
    )

    with st.spinner('جاري إجراء التحليل العميق...'):

        # Classification
        diagnosis = classify_image(
            img_rgb,
            cls_model
        )

        # الحالات المسموح لها بالتحليل الكامل
        VALID_RESULTS = [
            'Glioma Tumor',
            'Meningioma Tumor',
            'Pituitary Tumor'
        ]

        # قيم افتراضية
        viz_img = img_rgb
        mask_raw = None

        # Segmentation فقط لو يوجد ورم
        if diagnosis in VALID_RESULTS:

            viz_img, mask_raw = segment_image(
                img_rgb,
                seg_model
            )

        # حفظ النتيجة
        save_to_db(
            diagnosis,
            uploaded_file.name
        )

    # =====================================================
    # Results
    # =====================================================

    st.success(f"النتيجة: {diagnosis}")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🖼️ الصورة الأصلية")

        st.image(
            img_rgb,
            use_container_width=True
        )

    with col2:

        if diagnosis in VALID_RESULTS:

            st.subheader("🎯 منطقة الورم المكتشفة")

            st.image(
                viz_img,
                use_container_width=True
            )

        else:

            st.subheader("ℹ️ نتيجة التحليل")

            st.info("لا توجد منطقة ورم لعرضها.")

    # =====================================================
    # Radiomics + PDF
    # =====================================================

    if (
        diagnosis in VALID_RESULTS
        and mask_raw is not None
        and np.any(mask_raw)
    ):

        st.divider()

        c1, c2 = st.columns([2, 1])

        # Radiomics
        with c1:

            st.subheader("📊 الخصائص الإشعاعية (Radiomics)")

            feats = get_radiomics_features(
                img_rgb,
                mask_raw
            )

            st.table(list(feats.items())[:10])

        # PDF
        with c2:

            st.subheader("📄 التقرير الطبي")

            st.info(
                "يمكنك تحميل تقرير مفصل بصيغة PDF يحتوي على الصور والتحليلات."
            )

            pdf_data = create_pdf_report(
                img_rgb,
                viz_img,
                diagnosis,
                feats,
                st.session_state.user_email
            )

            st.download_button(
                label="📥 تحميل التقرير (PDF)",
                data=pdf_data,
                file_name=f"Report_{uploaded_file.name}.pdf",
                mime="application/pdf"
            )

# =========================================================
# Navigation
# =========================================================

st.divider()

b1, b2 = st.columns(2)

with b1:

    st.page_link(
        "pages/2_Analytics.py",
        label="الذهاب الي لوحة الاحصائيات",
        icon="📊",
        use_container_width=True
    )

with b2:

    st.page_link(
        "Home.py",
        label="العودة للرئيسية",
        icon="🏠",
        use_container_width=True
    )
