import streamlit as st
import sqlite3
import hashlib
from email_validator import validate_email, EmailNotValidError

st.set_page_config(page_title="BrainScan AI", layout="wide", page_icon="🧠")

# اسم قاعدة بيانات موحد لكل العمليات
DB_NAME = 'brain_tumor.db'

# --- الدوال الأساسية ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

init_db()

# إعداد الجلسة
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = ""

# --- الواجهة ---
if not st.session_state.logged_in:
    st.title("🧠 BrainScan AI Portal")
    tab1, tab2 = st.tabs(["🔐 تسجيل دخول", "📝 حساب جديد"])
    
    with tab1:
        e_login = st.text_input("البريد الإلكتروني", key="login_email")
        p_login = st.text_input("كلمة المرور", type="password", key="login_pass")
        if st.button("دخول"):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute('SELECT password FROM users WHERE email =?', (e_login,))
            data = c.fetchone()
            conn.close() # إغلاق الاتصال دائمًا
            
            if data and check_hashes(p_login, data[0]):
                st.session_state.logged_in = True
                st.session_state.user_email = e_login
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun() # سيقوم بإعادة التشغيل وإظهار المحتوى الجديد
            else: 
                st.error("البريد الإلكتروني أو كلمة المرور غير صحيحة")

    with tab2:
        e_reg = st.text_input("البريد الإلكتروني الجديد", key="reg_email")
        p_reg = st.text_input("كلمة مرور جديدة", type="password", key="reg_pass")
        if st.button("إنشاء حساب"):
            if e_reg and p_reg:
                try:
                    validate_email(e_reg)
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute('INSERT INTO users VALUES (?,?)', (e_reg, make_hashes(p_reg)))
                    conn.commit()
                    conn.close()
                    st.success("تم إنشاء الحساب بنجاح! انتقل لخانة تسجيل الدخول.")
                except sqlite3.IntegrityError:
                    st.error("هذا البريد مسجل بالفعل!")
                except EmailNotValidError:
                    st.error("يرجى إدخال بريد إلكتروني بصيغة صحيحة")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
            else:
                st.warning("يرجى ملء جميع الحقول")

else:
    # الترحيب بالمستخدم
    st.markdown(f"## مرحباً بك د. {st.session_state.user_email.split('@')[0].capitalize()} 👋")
    st.balloons()
    
    # صف الأزرار العلوية
    col_status, col_logout = st.columns([3, 1])
    with col_status:
        st.success(f"تم التحقق من الهوية بنجاح ✅ (المستخدم: {st.session_state.user_email})")
    with col_logout:
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.rerun()

    st.divider()

    # --- قسم الانتقال لصفحة التحليل ---
    st.markdown("### 🛠️ الأدوات المتاحة")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.info("ابدأ الآن بتحليل صور الرنين المغناطيسي وتحديد مكان الورم بدقة.")
        # زر للانتقال لصفحة التحليل (يجب أن يكون اسم الملف Tumor_Analysis.py في مجلد pages)
        if st.button("الذهاب إلى صفحة التحليل 🔍", type="primary", use_container_width=True):
            st.page_link("pages/1_Tumor_Analysis.py")
    
    st.divider()

    # --- قسم التعريف بالأمراض ---
    st.markdown("### 📚 دليل الأورام المدعومة في النظام")
    st.write("يقوم النظام بتصنيف وتحديد أربعة أنواع رئيسية بناءً على خوارزميات الذكاء الاصطناعي:")

    # استخدام Tabs لعرض المعلومات بشكل منظم
    tab1, tab2, tab3, tab4 = st.tabs(["Glioma", "Meningioma", "Pituitary", "Healthy"])

    with tab1:
        st.markdown("#### 🧬 الورم الدبقي (Glioma Tumor)")
        st.write("""
        هو نوع شائع من الأورام ينشأ في الخلايا الدبقية التي تحيط بالخلايا العصبية. 
        - **الخطورة:** قد يكون سريع النمو (عدواني).
        - **الظهور:** يظهر غالباً بشكل غير منتظم داخل أنسجة الدماغ.
        """)
        
    with tab2:
        st.markdown("#### 🧩 الورم السحائي (Meningioma Tumor)")
        st.write("""
        ينشأ من الأغشية التي تغطي الدماغ والحبل الشوكي.
        - **الخطورة:** غالباً ما يكون حميداً وبطيء النمو.
        - **الظهور:** يظهر عادةً عند أطراف الدماغ ويضغط على الأنسجة المجاورة.
        """)

    with tab3:
        st.markdown("#### ⚖️ ورم الغدة النخامية (Pituitary Tumor)")
        st.write("""
        ورم ينمو في الغدة النخامية المسؤولة عن الهرمونات.
        - **الخطورة:** قد يؤثر على الرؤية أو يسبب خللاً هرمونياً كبيراً.
        - **الظهور:** يتركز في قاعدة الجمجمة تحت الدماغ.
        """)

    with tab4:
        st.markdown("#### ✅ الدماغ السليم (No Tumor)")
        st.write("""
        يعني عدم وجود أي نمو غير طبيعي أو كتل في صور الرنين المغناطيسي، مع وضوح الأنسجة الطبيعية.
        """)

    # القائمة الجانبية
    st.sidebar.title("القائمة الرئيسية")
    st.sidebar.markdown(f"**المستخدم الحالي:** \n `{st.session_state.user_email}`")
