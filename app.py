import streamlit as st
import google.generativeai as genai
from PIL import Image

# הגדרת דף
st.set_page_config(page_title="זיהוי וטיפול בכתמים", page_icon="🧺", layout="centered")

# --- CSS מותאם אישית: RTL ויישור ימינה קשיח לכל הרכיבים ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700;800&display=swap');

        /* הגדרת כיווניות RTL ויישור לימין גורף */
        html, body, .stApp, .main, .block-container {
            font-family: 'Assistant', sans-serif !important;
            direction: rtl !important;
            text-align: right !important;
            background-color: #ffffff !important;
            color: #1e293b !important;
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

        /* כותרת הטופס */
        .form-header {
            font-family: 'Assistant', sans-serif !important;
            font-size: 2rem;
            font-weight: 800;
            color: #1e293b;
            margin-bottom: 25px;
            text-align: center !important;
            direction: rtl !important;
        }

        /* תווית שדה עם כוכבית אדומה */
        .req-label {
            font-weight: 600;
            font-size: 0.95rem;
            color: #334155;
            margin-bottom: 6px;
            text-align: right !important;
            direction: rtl !important;
            display: block !important;
        }
        .req-asterisk {
            color: #e11d48;
            font-weight: bold;
        }

        /* שדות קלט עם קו תחתון - יישור ימינה מלא */
        div[data-baseweb="input"] input, div[data-baseweb="base-input"] input {
            border: none !important;
            border-bottom: 1.5px solid #64748b !important;
            border-radius: 0px !important;
            background-color: transparent !important;
            padding-right: 0px !important;
            box-shadow: none !important;
            direction: rtl !important;
            text-align: right !important;
        }

        div[data-baseweb="select"] {
            border: none !important;
            border-bottom: 1.5px solid #64748b !important;
            border-radius: 0px !important;
            background-color: transparent !important;
            box-shadow: none !important;
            direction: rtl !important;
            text-align: right !important;
        }

        /* יישור תפריטים נפתחים (Select Box Options) */
        ul[role="listbox"] {
            direction: rtl !important;
            text-align: right !important;
        }

        /* יישור רכיב העלאת הקבצים והמצלמה לימין */
        [data-testid="stFileUploader"], [data-testid="stCameraInput"] {
            direction: rtl !important;
            text-align: right !important;
        }

        [data-testid="stFileUploaderDropzone"] {
            direction: rtl !important;
            text-align: right !important;
            justify-content: flex-start !important;
            flex-direction: row-reverse !important;
        }

        /* שומר על הכפתור הפנימי מלהתנגש בטקסט שנוצר עקב ה-RTL */
        [data-testid="stFileUploaderDropzone"] button {
            direction: ltr !important;
            margin-left: 10px !important;
        }

        /* עיצוב הלשוניות (Tabs) - מיושרות מימין לשמאל */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
            margin-bottom: 15px;
            direction: rtl !important;
            justify-content: flex-start !important;
            flex-direction: row !important;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            padding: 8px 20px;
            color: #334155;
            font-weight: 600;
            font-size: 0.95rem;
            direction: rtl !important;
            text-align: right !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #f39a1e !important;
            border-color: #f39a1e !important;
            color: #ffffff !important;
            box-shadow: 0 2px 6px rgba(243, 154, 30, 0.3) !important;
        }

        /* כפתור ראשי בכתום בולט */
        .stButton button[kind="primary"] {
            background-color: #f39a1e !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            border: none !important;
            width: 100% !important;
            box-shadow: 0 3px 8px rgba(243, 154, 30, 0.3) !important;
            transition: all 0.2s ease !important;
            margin-top: 15px;
            direction: rtl !important;
            text-align: center !important;
        }
        .stButton button[kind="primary"]:hover {
            background-color: #e08b12 !important;
        }

        /* תיבת תוצאה בסגנון תיבת ההוראות */
        .instruction-box {
            background-color: #f1f5f9;
            border: 1px solid #94a3b8;
            border-radius: 4px;
            padding: 16px;
            font-size: 0.95rem;
            line-height: 1.6;
            color: #0f172a;
            max-height: 350px;
            overflow-y: auto;
            margin-top: 20px;
            direction: rtl !important;
            text-align: right !important;
            white-space: pre-wrap;
        }

        .stAlert {
            direction: rtl !important;
            text-align: right !important;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# כותרת הטופס
st.markdown('<div class="form-header">אפליקציה חכמה להסרת כתמים מבגדים</div>', unsafe_allow_html=True)

# טעינת מפתח API
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    API_KEY = st.text_input("🔑 מפתח API (חובה) *", type="password")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY.strip())

        # שדה 1: ממה נגרם הכתם
        st.markdown('<div class="req-label"><span class="req-asterisk">*</span> ממה נגרם הכתם</div>', unsafe_allow_html=True)
        stain_text = st.text_input("", placeholder="לדוגמה: יין אדום, קפה, שמן, דם...", label_visibility="collapsed")

        # שדה 2: סוג הבד
        st.markdown('<div class="req-label" style="margin-top: 15px;"><span class="req-asterisk">*</span> סוג הבד</div>', unsafe_allow_html=True)
        fabric_type = st.selectbox(
            "",
            ["כותנה", "ג'ינס", "סינתטי (פוליאסטר)", "משי / עדין", "צמר", "לא בטוח/ה"],
            label_visibility="collapsed"
        )

        # שדה 3: אמצעי קלט תמונה
        st.markdown('<div class="req-label" style="margin-top: 20px;"><span class="req-asterisk">*</span> בחירת אמצעי קלט תמונה</div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["באמצעות העלאת קובץ", "באמצעות מצלמה"])
        image_file = None

        with tab1:
            uploaded_file = st.file_uploader("בחירת תמונה:", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
            if uploaded_file:
                image_file = uploaded_file

        with tab2:
            camera_photo = st.camera_input("צילום הכתם:", label_visibility="collapsed")
            if camera_photo:
                image_file = camera_photo

        image = None
        if image_file:
            image = Image.open(image_file).convert("RGB")
            st.image(image, caption="התמונה שנבחרה", use_container_width=True)

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
                        st.markdown(f'<div class="instruction-box"><b>הוראות ניקוי:</b><br><br>{response.text}</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"אירעה שגיאה בחיבור: {last_error}")

    except Exception as e:
        st.error(f"שגיאה: {e}")
