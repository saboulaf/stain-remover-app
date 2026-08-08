import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="מסיר הכתמים החכם", page_icon="🧺", layout="centered")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;600;700&display=swap');

        html, body, .stApp {
            font-family: 'Rubik', sans-serif !important;
            background: linear-gradient(180deg, #e0f2fe 0%, #f0f9ff 100%) !important;
            direction: rtl;
            text-align: right;
        }

        [data-testid="stHeader"], footer { display: none !important; }
        .block-container { padding-top: 1rem !important; max-width: 680px; }

        /* באנר עם גרדיאנט כחול-ים */
        .top-header {
            background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
            border-radius: 24px;
            margin-bottom: 25px;
            box-shadow: 0 10px 25px rgba(2, 132, 199, 0.25);
        }
        .top-header h1 { color: white !important; font-weight: 700 !important; font-size: 2.1rem !important; margin: 0 !important; }
        .top-header p { color: #e0f2fe !important; font-size: 1rem !important; margin-top: 6px !important; }

        /* כרטיסיות עגולות ורכות */
        .css-card {
            background-color: #ffffff;
            border-radius: 20px;
            padding: 22px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
            border: 1px solid #bae6fd;
            margin-bottom: 20px;
        }
        .card-title { color: #0369a1; font-weight: 700; font-size: 1.2rem; margin-bottom: 15px; }

        input, textarea, .stSelectbox, div[data-baseweb="select"] {
            direction: rtl !important; text-align: right !important; border-radius: 12px !important;
        }

        .stButton button[kind="primary"] {
            background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
            color: #ffffff !important; font-weight: 700 !important; font-size: 1.15rem !important;
            border-radius: 14px !important; padding: 14px !important; border: none !important;
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3) !important; width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="top-header">
        <h1>🧺 מסיר הכתמים החכם</h1>
        <p>ניקוי מושלם ורענן בלחיצת כפתור</p>
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
