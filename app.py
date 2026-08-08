import streamlit as st
import google.generativeai as genai
from PIL import Image

# הגדרת דף
st.set_page_config(page_title="זיהוי וטיפול בכתמים", page_icon="🛡️", layout="centered")

# --- CSS מעוצב בסגנון GovID נקי ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700;800&display=swap');

        /* רקע ופונט */
        html, body, .stApp {
            font-family: 'Assistant', sans-serif !important;
            background-color: #eef3f8 !important;
            color: #0f2b48 !important;
            direction: rtl;
            text-align: right;
        }

        /* הסרת סרגלי הכלים של Streamlit */
        [data-testid="stHeader"], footer {
            display: none !important;
        }

        /* מכולה ראשית */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
            max-width: 650px;
        }

        /* כותרת ראשית */
        .main-title {
            text-align: center;
            color: #0f2b48;
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 20px;
        }

        /* כרטיסיה לבנה מרכזית */
        .govid-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 28px;
            box-shadow: 0 4px 16px rgba(15, 43, 72, 0.06);
            border: 1px solid #dbe2ea;
            margin-bottom: 20px;
        }

        /* כותרות משנה בתוך הכרטיסיה */
        .sub-title {
            color: #0f2b48;
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 12px;
        }

        /* עיצוב שדות קלט בסגנון כחלחל-בהיר */
        div[data-baseweb="input"], div[data-baseweb="select"] {
            background-color: #f0f4f9 !important;
            border: 1px solid #c5d3e2 !important;
            border-radius: 8px !important;
        }
        
        input {
            color: #0f2b48 !important;
            font-weight: 600 !important;
        }

        /* כפתור ראשי בכחול-נייבי */
        .stButton button[kind="primary"] {
            background-color: #004b87 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            border: none !important;
            width: 100% !important;
            box-shadow: 0 2px 6px rgba(0, 75, 135, 0.2) !important;
            transition: all 0.2s ease !important;
        }
        .stButton button[kind="primary"]:hover {
            background-color: #003662 !important;
        }

        /* עיצוב הלשוניות (Tabs) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #f8fafc;
            border: 1px solid #c5d3e2;
            border-radius: 8px;
            padding: 8px 16px;
            color: #004b87;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #e8f1f9 !important;
            border-color: #004b87 !important;
            color: #004b87 !important;
        }

        .stAlert {
            direction: rtl;
            text-align: right;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# כותרת העמוד
st.markdown('<div class="main-title">זיהוי וטיפול בכתמים</div>', unsafe_allow_html=True)

# טעינת מפתח API
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    st.markdown('<div class="govid-card">', unsafe_allow_html=True)
    API_KEY = st.text_input("🔑 הזן מפתח API של Gemini:", type="password")
    st.markdown('</div>', unsafe_allow_html=True)

if API_KEY:
    try:
        genai.configure(api_key=API_KEY.strip())

        # כרטיסיית הזנת הנתונים
        st.markdown('<div class="govid-card">', unsafe_allow_html=True)
        
        st.markdown('<div class="sub-title">פרטי הכתם והבד</div>', unsafe_allow_html=True)
        
        stain_text = st.text_input(
            "גורם הכתם:", 
            placeholder="לדוגמה: יין אדום, קפה, שמן, דם..."
        )
        
        fabric_type = st.selectbox(
            "סוג הבד:",
            ["כותנה", "ג'ינס", "סינתטי (פוליאסטר)", "משי / עדין", "צמר", "לא בטוח/ה"]
        )

        st.markdown('<div class="sub-title" style="margin-top: 15px;">תמונת הכתם</div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["📁 העלאה מהגלריה", "📷 צילום במצלמה"])
        image_file = None

        with tab1:
            uploaded_file = st.file_uploader("בחירת תמונה:", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                image_file = uploaded_file

        with tab2:
            camera_photo = st.camera_input("צילום הכתם:")
            if camera_photo:
                image_file = camera_photo

        image = None
        if image_file:
            image = Image.open(image_file).convert("RGB")
            if image_file == uploaded_file:
                st.image(image, caption="התמונה שנבחרה", use_column_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # כפתור הפעלה
        if st.button("חשב הוראות ניקוי", type="primary"):
            if not stain_text and not image:
                st.warning("יש לרשום ממה נגרם הכתם או לצרף תמונה.")
            else:
                with st.spinner("מנתח נתונים..."):
                    prompt = f"""
                    אתה מומחה להסרת כתמים וכביסה.
                    המשתמש מבקש עזרה בהסרת כתם.
                    
                    מידע מפי המשתמש:
                    - גורם הכתם (טקסט): {stain_text if stain_text else 'לא צוין, יש לזהות מהתמונה'}
                    - סוג הבד: {fabric_type}
                    
                    משימותיך:
                    1. אם צורפה תמונה, נתח אותה וודא אם הכתם נראה מתאים לגורם שתואר.
                    2. ספק מדריך ברור, קצר ושלב-אחר-שלב להסרת הכתם.
                    3. פרט אילו חומרים נדרשים.
                    4. ציין ממה חובה להימנע כדי לא להרוס את הבד.
                    
                    החזר את התשובה בעברית תקנית, בפורמט מעוצב, ברור וידידותי.
                    """
                    
                    inputs = [prompt]
                    if image:
                        inputs.append(image)
                    
                    candidate_models = [
                        'gemini-2.0-flash',
                        'gemini-1.5-flash-latest',
                        'gemini-1.5-pro-latest',
                        'gemini-1.5-flash',
                        'gemini-1.5-pro'
                    ]
                    
                    try:
                        for m in genai.list_models():
                            if 'generateContent' in m.supported_generation_methods:
                                clean_name = m.name.replace('models/', '')
                                if clean_name not in candidate_models:
                                    candidate_models.append(clean_name)
                    except Exception:
                        pass

                    response = None
                    last_error = None

                    for model_name in candidate_models:
                        try:
                            model = genai.GenerativeModel(model_name)
                            res = model.generate_content(inputs)
                            if res and res.text:
                                response = res
                                break
                        except Exception as err:
                            last_error = err
                            continue

                    if response:
                        st.markdown('<div class="govid-card">', unsafe_allow_html=True)
                        st.markdown('<div class="sub-title" style="color: #004b87;">הנחיות לניקוי הכתם</div>', unsafe_allow_html=True)
                        st.markdown(f"<div style='direction: rtl; text-align: right; line-height: 1.6;'>{response.text}</div>", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"אירעה שגיאה בחיבור: {last_error}")

    except Exception as e:
        st.error(f"שגיאה: {e}")
