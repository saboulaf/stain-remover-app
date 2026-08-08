import streamlit as st
import google.generativeai as genai
from PIL import Image

# הגדרת דף - עיצוב ברשת
st.set_page_config(page_title="מערכת הזיהוי והטיפול בכתמים", page_icon="🛡️", layout="centered")

# --- CSS מותאם אישית בסגנון GovID / מערכת ההזדהות הלאומית ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700;800&display=swap');

        /* רקע כללי ופונט */
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
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            max-width: 850px;
        }

        /* סרגל עליון מינימליסטי */
        .top-gov-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
            color: #004b87;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 8px;
            border-bottom: 1px solid #dce4ed;
        }

        /* כותרת מרכזית */
        .main-title {
            text-align: center;
            color: #0f2b48;
            font-size: 2.1rem;
            font-weight: 800;
            margin-bottom: 25px;
        }

        /* כרטיסייה לבנה ראשית */
        .govid-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 16px rgba(15, 43, 72, 0.06);
            border: 1px solid #dbe2ea;
            margin-bottom: 20px;
        }

        /* כותרות משנה בתוך הכרטיסייה */
        .sub-title {
            color: #0f2b48;
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
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

        /* כפתור ראשי בכחול-נייבי רשמי */
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

        /* כרטיסיית מידע צדדית (Outline) */
        .info-side-box {
            border-left: 1px solid #e2e8f0;
            padding-left: 20px;
            height: 100%;
        }
        
        .outline-btn {
            border: 2px solid #004b87;
            color: #004b87;
            background-color: transparent;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 700;
            text-align: center;
            margin-top: 15px;
            display: block;
            text-decoration: none;
        }

        /* עיצוב הלשוניות ככפתורי בחירה מרובעים בחלק התחתון */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #f8fafc;
            border: 1px solid #c5d3e2;
            border-radius: 8px;
            padding: 10px 16px;
            color: #004b87;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #e8f1f9 !important;
            border-color: #004b87 !important;
            color: #004b87 !important;
        }

        /* יישור הודעות */
        .stAlert {
            direction: rtl;
            text-align: right;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# --- סרגל עליון בסגנון ממשלתי ---
st.markdown("""
    <div class="top-gov-bar">
        <div>🔒 אבחון מוסמך ומהיר לשירות הציבור</div>
        <div>מערכת הזיהוי והטיפול בכתמים</div>
    </div>
    <div class="main-title">אבחון וזיהוי כתמים ממוחשב</div>
""", unsafe_allow_html=True)

# טעינת מפתח API
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    st.markdown('<div class="govid-card">', unsafe_allow_html=True)
    API_KEY = st.text_input("🔑 הזן מפתח API של Gemini להזדהות במערכת:", type="password")
    st.markdown('</div>', unsafe_allow_html=True)

if API_KEY:
    try:
        genai.configure(api_key=API_KEY.strip())

        # --- הכרטיסייה הראשית (בחלוקה דו-עמודתית) ---
        st.markdown('<div class="govid-card">', unsafe_allow_html=True)
        
        col_right, col_left = st.columns([2, 1], gap="large")

        # עמודה ימנית: טופס הזנת נתונים
        with col_right:
            st.markdown('<div class="sub-title">🔒 הזנת פרטי הכתם והבד</div>', unsafe_allow_html=True)
            
            stain_text = st.text_input(
                "גורם הכתם (תיאור מילולי)", 
                placeholder="לדוגמה: יין אדום, קפה, שמן, דם..."
            )
            
            fabric_type = st.selectbox(
                "סוג הבד המטופל",
                ["כותנה", "ג'ינס", "סינתטי (פוליאסטר)", "משי / עדין", "צמר", "לא בטוח/ה"]
            )

            st.markdown('<div class="sub-title" style="font-size: 1.05rem; margin-top: 15px;">📸 אמצעי אימות ויזואלי</div>', unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["📁 העלאת קובץ", "📷 צילום במצלמה"])
            image_file = None

            with tab1:
                uploaded_file = st.file_uploader("בחירת תמונה מהמחשב/נייד:", type=["jpg", "jpeg", "png"])
                if uploaded_file:
                    image_file = uploaded_file

            with tab2:
                camera_photo = st.camera_input("צילום ישיר של הכתם:")
                if camera_photo:
                    image_file = camera_photo

            image = None
            if image_file:
                image = Image.open(image_file).convert("RGB")
                if image_file == uploaded_file:
                    st.image(image, caption="התמונה שנקלטה במערכת", use_column_width=True)

        # עמודה שמאלית: כרטיסיית הסבר ומידע
        with col_left:
            st.markdown("""
                <div class="info-side-box">
                    <div style="font-weight: 700; font-size: 1.1rem; color: #0f2b48; margin-bottom: 8px;">אין לך מושג ממה הכתם?</div>
                    <div style="font-size: 0.9rem; color: #475569; line-height: 1.5;">
                        העלו תמונה ברורה של הכתם, ומנגנון ה-AI יבצע ניתוח ראייה ממוחשבת כדי לזהות את הרכב הכתם והטיפול המומלץ.
                    </div>
                    <div class="outline-btn">אבחון אוטומטי בטוח</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # כפתור הפעלה מרכזי
        if st.button("כניסה לאבחון והפקת הוראות ניקוי 🛡️", type="primary"):
            if not stain_text and not image:
                st.warning("יש להזין תיאור מילולי של הכתם או לצרף תמונה לאימות.")
            else:
                with st.spinner("מבצע ניתוח נתונים ממוחשב..."):
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
                        # כרטיסיית תוצאה מעוצבת
                        st.markdown('<div class="govid-card">', unsafe_allow_html=True)
                        st.markdown('<div class="sub-title" style="color: #004b87;">📋 תוכנית טיפול והנחיות ניקוי מאושרות</div>', unsafe_allow_html=True)
                        st.markdown(f"<div style='direction: rtl; text-align: right; font-size: 1rem; line-height: 1.6;'>{response.text}</div>", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"לא ניתן היה להתחבר למודלים. שגיאה: {last_error}")

    except Exception as e:
        st.error(f"אירעה שגיאה בחיבור ל-AI: {e}")
