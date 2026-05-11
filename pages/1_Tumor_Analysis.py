import streamlit as st
import numpy as np
import cv2
import tensorflow as tf
import sqlite3
from datetime import datetime
from io import BytesIO
import warnings
import SimpleITK as sitk
from radiomics import featureextractor
import os
import gdown

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table

warnings.filterwarnings("ignore")

# =========================
# Base Directory + DB
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if "pages" in BASE_DIR:
    BASE_DIR = os.path.dirname(BASE_DIR)

DB_NAME = os.path.join(BASE_DIR, 'brain_tumor.db')

# =========================
# Session Check
# =========================
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ يرجى تسجيل الدخول أولاً.")
    st.stop()

st.set_page_config(page_title="Brain MRI Analysis", layout="wide")

# =========================
# Unsupported Classes
# =========================
UNSUPPORTED_CLASSES = ["Not supported image", "Unsupported Image / Low Confidence"]

# =========================
# Load Models
# =========================
@st.cache_resource
def load_all_models():
    classification_id = '1atz2SVbb9-IHnzRDiLRAjjae1az3caD6'
    segmentation_id = '1CxuWXW9lFzixm_P0XosX8KF7n8ayfgly'

    cls_path = "brain_tumor1.h5"
    seg_path = "segmentation_model.h5"

    if not os.path.exists(cls_path):
        gdown.download(f'https://drive.google.com/uc?id={classification_id}', cls_path, quiet=False)

    if not os.path.exists(seg_path):
        gdown.download(f'https://drive.google.com/uc?id={segmentation_id}', seg_path, quiet=False)

    cls = tf.keras.models.load_model(cls_path)
    seg = tf.keras.models.load_model(seg_path, compile=False)

    return cls, seg

# =========================
# DB Save
# =========================
def save_to_db(diagnosis, img_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS history 
        (username TEXT, diagnosis TEXT, date TEXT, image_name TEXT)
    ''')

    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute('''
        INSERT INTO history VALUES (?,?,?,?)
    ''', (st.session_state.user_email, diagnosis, date_now, img_name))

    conn.commit()
    conn.close()

# =========================
# Classification
# =========================
def classify_image(img_rgb, model):
    resized = cv2.resize(img_rgb, (150, 150))
    input_img = resized.reshape(1, 150, 150, 3)

    preds = model.predict(input_img)
    confidence = np.max(preds)

    labels = ['Glioma Tumor', 'No Tumor', 'Meningioma Tumor', 'Pituitary Tumor']

    if confidence < 0.90:
        return "Not supported image"

    return labels[np.argmax(preds)]

# =========================
# Segmentation
# =========================
def segment_image(img_rgb, model):
    resized = cv2.resize(img_rgb, (256, 256))
    gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    input_tensor = np.expand_dims(np.expand_dims(gray, axis=-1), axis=0)

    pred_mask = model.predict(input_tensor)[0]
    mask = (pred_mask > 0.5).astype(np.uint8)

    mask_full = cv2.resize(mask, (img_rgb.shape[1], img_rgb.shape[0]))

    mask_colored = np.zeros_like(img_rgb)
    mask_colored[:, :, 0] = mask_full * 255

    highlighted = cv2.addWeighted(img_rgb, 0.8, mask_colored, 0.5, 0)

    return highlighted, mask_full

# =========================
# Radiomics
# =========================
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

        return {
            k: float(v)
            for k, v in features.items()
            if 'diagnostics' not in k
        }

    except:
        return {"Error": "Radiomics failed"}

# =========================
# PDF Report
# =========================
def create_pdf_report(img_orig, img_seg, diagnosis, radiomics, user_email):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("BrainScan AI Report", styles['Heading1']))
    elements.append(Paragraph(f"User: {user_email}", styles['Normal']))
    elements.append(Paragraph(f"Diagnosis: {diagnosis}", styles['Heading2']))
    elements.append(Spacer(1, 10))

    def to_img(arr):
        _, enc = cv2.imencode(".png", cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
        return BytesIO(enc.tobytes())

    elements.append(Table([
        [Image(to_img(img_orig), 200, 180),
         Image(to_img(img_seg), 200, 180)]
    ]))

    data = [["Feature", "Value"]]
    for i, (k, v) in enumerate(radiomics.items()):
        if i > 15:
            break
        data.append([k, str(v)])

    elements.append(Table(data))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# =========================
# UI
# =========================
st.title("🧠 Brain MRI Analysis")

cls_model, seg_model = load_all_models()

uploaded_file = st.file_uploader("Upload MRI Image", type=["jpg", "png", "jpeg"])

if uploaded_file:

    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    with st.spinner("Analyzing..."):

        diagnosis = classify_image(img_rgb, cls_model)

        is_supported = diagnosis not in UNSUPPORTED_CLASSES

        # =========================
        # ❌ UNSUPPORTED CASE
        # =========================
        if not is_supported:
            st.error("❌ الصورة غير مدعومة أو الثقة ضعيفة")
            st.warning("لن يتم تنفيذ Segmentation أو Radiomics أو PDF")
            st.stop()

        # =========================
        # ✅ VALID CASE
        # =========================
        viz_img, mask_raw = segment_image(img_rgb, seg_model)

        save_to_db(diagnosis, uploaded_file.name)

    st.success(f"Result: {diagnosis}")

    col1, col2 = st.columns(2)

    with col1:
        st.image(img_rgb)

    with col2:
        st.image(viz_img)

    # =========================
    # Radiomics + PDF ONLY
    # =========================
    if np.any(mask_raw):

        st.divider()

        feats = get_radiomics_features(img_rgb, mask_raw)

        st.subheader("Radiomics Features")
        st.table(list(feats.items())[:10])

        pdf = create_pdf_report(
            img_rgb,
            viz_img,
            diagnosis,
            feats,
            st.session_state.user_email
        )

        st.download_button(
            "Download Report",
            pdf,
            "report.pdf",
            "application/pdf"
        )

# =========================
# Navigation
# =========================
st.divider()

c1, c2 = st.columns(2)

with c1:
    st.page_link("pages/2_Analytics.py", label="Analytics")

with c2:
    st.page_link("Home.py", label="Home")
