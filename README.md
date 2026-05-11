# 🧠 نظام تشخيص وتحديد أورام الدماغ باستخدام الذكاء الاصطناعي
### Brain Tumor Classification & Segmentation System

هذا المشروع هو تطبيق ويب تفاعلي يعتمد على **التعلم العميق (Deep Learning)** لمساعدة الأطباء في تحليل صور الرنين المغناطيسي (MRI). يقوم النظام بمهمتين أساسيتين:
1. **التصنيف (Classification):** تحديد نوع الورم (Glioma, Meningioma, Pituitary) أو التأكد من سلامة الدماغ.
2. **التقطيع (Segmentation):** تحديد مكان الورم بدقة ورسم قناع (Mask) ملون فوق منطقة الإصابة.

---

## 🚀 المميزات (Features)
*   **دقة عالية:** استخدام نماذج CNN متطورة مدربة على آلاف الصور الطبية.
*   **واجهة تفاعلية:** مبنية باستخدام Streamlit لتسهيل الاستخدام.
*   **تحليل فوري:** الحصول على النتائج في ثوانٍ معدودة.
*   **نظام أمان:** صفحة تسجيل دخول مخصصة للأطباء المصرح لهم.

---

## 🛠️ التقنيات المستخدمة (Tech Stack)
*   **Python:** اللغة الأساسية للمشروع.
*   **TensorFlow/Keras:** لبناء وتشغيل نماذج الذكاء الاصطناعي (.h5).
*   **OpenCV:** لمعالجة الصور وتحويلها (Grayscale, RGB, Resizing).
*   **Streamlit:** لبناء واجهة المستخدم الويب.
*   **Matplotlib & NumPy:** للتعامل مع المصفوفات الحسابية وعرض الصور.

---

## 📂 هيكلة المشروع (Project Structure)
```text
brai/
├── Home.py              # الصفحة الرئيسية ونظام تسجيل الدخول
├── requirements.txt     # ملف المكتبات المطلوبة للتشغيل
├── brain_tumor1.h5      # موديل التصنيف (Classification)
├── segment_model.h5     # موديل تحديد المكان (Segmentation)
└── pages/               # المجلد الفرعي لصفحات التطبيق
    └── Tumor_Analysis.py # صفحة تحليل ورفع الصور
Brain Tumor AI System
Classification • Segmentation • Radiomics




🚀 Live Demo
👉 Try the App Here:

(ضع هنا رابط Streamlit Cloud أو Render بعد النشر)
https://your-app-link.streamlit.app


🧠 Overview
This project is an AI-powered medical decision support system for brain tumor analysis using MRI images.
It integrates:


🧬 Deep Learning (CNN & U-Net)

📊 Radiomics Feature Extraction

🖼️ Medical Image Processing

📈 Clinical Reporting Dashboard
The system helps doctors:


Detect tumors

Classify tumor types

Segment tumor regions

Extract quantitative radiomic features
✨ Features

⚡ Fast MRI analysis (seconds)

🎯 High accuracy deep learning models

🧠 Multi-stage pipeline (Classification + Segmentation + Radiomics)

📊 Interactive analytics dashboard

🔐 Secure login system

📑 Patient history tracking

🧬 Advanced radiomics feature extraction
🖥️ Screenshots
🏠 Home Page
🔬 MRI Analysis Page
📊 Analytics Dashboard
🧬 Segmentation Result
🛠️ Tech Stack
Python
TensorFlow / Keras
Streamlit
OpenCV
NumPy / Pandas
Matplotlib / Plotly
PyRadiomics
Scikit-learn
🧬 Radiomics Module
Radiomics converts medical images into quantitative data features.

Extracted Features:

Shape-based features

Texture analysis (GLCM, GLRLM)

Intensity statistics

Histogram features
Why it matters:

Improves diagnostic accuracy

Adds explainability to AI decisions

Bridges AI with clinical medicine
📂 Project Structure
brain_tumor_app/
│
├── Home.py                  # Login + Main Interface
├── requirements.txt        # Dependencies
├── brain_tumor1.h5        # Classification model
├── segment_model.h5       # Segmentation model
│
└── pages/
    ├── 1_Tumor_Analysis.py
    ├── 2_Analytics.py

⚙️ Installation
1. Clone repository

git clone https://github.com/your-username/brain-tumor-ai.git
cd brain-tumor-ai

2. Install dependencies

pip install -r requirements.txt


3. Run app

streamlit run Home.py


📊 Supported Classes

Glioma Tumor

Meningioma Tumor

Pituitary Tumor

No Tumor (Healthy)
🧠 System Pipeline
MRI Image
   ↓
Preprocessing (OpenCV)
   ↓
Classification Model (CNN)
   ↓
Segmentation Model (U-Net)
   ↓
Radiomics Feature Extraction
   ↓
Final Clinical Report

📈 Future Improvements

3D MRI support

Explainable AI (Grad-CAM visualization)

Cloud deployment (AWS / GCP)

Multi-disease extension

Real hospital integration
👨‍⚕️ Medical Disclaimer
This system is a decision support tool only and should not replace professional medical diagnosis.
📜 License
This project is licensed under the MIT License اعملي ده علي هيئة ملف readme
