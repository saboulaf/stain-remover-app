import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="מסיר הכתמים החכם", page_icon="🧺", layout="centered")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;800&display=swap');

        html, body, .stApp {
            font-family: 'Assistant', sans-serif !important;
            background-color: #0b0f19 !important;
            color: #f1f5f9 !important;
            direction: rtl;
            text-align: right;
        }

        [data-testid="stHeader"], footer { display: none !important; }
        .block-container { padding-top: 1.5rem !important; max-width: 680px; }

        /* כותרת כהה ומודרנית */
        .top-header {
            background-color: #1e293b;
            border: 1px solid #334155;
            padding: 25px;
            text-align: center;
            border-radius: 16px;
            margin-bottom: 25px;
        }
        .top-header h1 { color: #38bdf8 !important; font-weight: 800 !important; font-size: 2.2rem !important; margin: 0 !important; }
        .top-header p { color: #94a3b8 !important; font-size: 1rem !important; margin-top: 4px !important; }

        /* כרטיסיות כהות עם מסגרת עדינה */
        .css-card {
            background-color: #1e293b;
            border-radius: 16px;
            padding: 22px;
            border: 1px solid #334155;
            margin-bottom: 20px;
        }
        .card-title { color: #38bdf8; font-weight: 700; font-size: 1.2rem; margin-bottom: 15px; }

        /* התאמת אלמנטים למצב לילה */
        input, textarea, .stSelectbox, div[data-baseweb="select"] {
            direction: rtl !important; text-align: right !important;
            background-color: #0f172a !important; color: #f8fafc !important;
            border: 1px solid #334155 !important; border-radius: 10px !important;
        }

        .stButton button[kind="primary"] {
            background-color: #0284c7 !important;
            color: #ffffff !important; font-weight: 700 !important; font-size: 1.15rem !important;
            border-radius: 10px !important; padding: 14px !important; border: none !important;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important; width: 100% !important;
        }
        .stButton button[kind="primary"]:hover { background-color: #0369a1 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="top-header">
        <h1>🧺 מסיר הכתמים החכם</h1>
        <p>מערכת AI מתקדמת לזיהוי וטיפול בכתמים</p>
    </div>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        API_KEY = st.text_input("🔑 הזן מפתח API של Gemini:", type="password")
        st.markdown('</div>', unsafe_allow_html=True)

if API_KEY:
    try:
        genai.configure(api_key=API_KEY.strip())

        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🧼 זיהוי הכתם והבד</div>', unsafe_allow_html=True)
        stain_text = st.text_input("ממה נגרם הכתם?", placeholder="לדוגמה: קפה, יין, דם...")
        fabric_type = st.selectbox("סוג הבד:", ["כותנה", "ג'ינס", "סינתטי", "משי / עדין", "צמר", "לא בטוח/ה"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📸 תמונת הכתם</div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["📁 העלאה מהגלריה", "📷 צילום במצלמה"])
        image_file = None
        with tab1:
            uploaded_file = st.file_uploader("בחרו תמונה:", type=["jpg", "jpeg", "png"])
            if uploaded_file: image_file = uploaded_file
        with tab2:
            camera_photo = st.camera_input("צלמו את הכתם:")
            if camera_photo: image_file = camera_photo

        image = None
        if image_file:
            image = Image.open(image_file).convert("RGB")
            if image_file == uploaded_file:
                st.image(image, caption="התמונה שהועלתה", use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🚀 חשב הוראות ניקוי", type="primary"):
            if not stain_text and not image:
                st.warning("אנא רשמו ממה נגרם הכתם או העלו תמונה.")
            else:
                with st.spinner("מנתח את הכתם..."):
                    prompt = f"אתה מומחה להסרת כתמים. גורם: {stain_text}, בד: {fabric_type}. ספק מדריך קצר ושלבי ניקוי בעברית."
                    inputs = [prompt]
                    if image: inputs.append(image)
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    res = model.generate_content(inputs)
                    st.markdown('<div class="css-card">', unsafe_allow_html=True)
                    st.markdown('<div class="card-title">✨ הנחיות הניקוי</div>', unsafe_allow_html=True)
                    st.markdown(f"<div style='direction: rtl;'>{res.text}</div>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"שגיאה: {e}")
