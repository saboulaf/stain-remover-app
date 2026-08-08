import streamlit as st
import google.generativeai as genai
from PIL import Image

# הגדרת דף - עיצוב כללי
st.set_page_config(page_title="מסיר הכתמים החכם", page_icon="🧺", layout="centered")

# --- CSS מותאם אישית להשגת העיצוב המבוקש ---
st.markdown("""
    <style>
        /* יבוא פונט Heebo הנקי מ-Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;800&display=swap');

        /* הגדרות כלליות ורקע הדף */
        html, body, .stApp {
            font-family: 'Heebo', sans-serif !important;
            background-color: #f4f6f8 !important;
            direction: rtl;
            text-align: right;
        }

        /* הסרת סרגלי הכלים הדיפולטיביים של Streamlit */
        [data-testid="stHeader"], footer {
            display: none !important;
        }

        /* הגדרת המכולה הראשית */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 3rem !important;
            max-width: 700px;
        }

        /* --- באנר עליון ירוק (כמו בתמונה) --- */
        .top-header {
            background-color: #009661;
            color: white;
            padding: 35px 20px 25px 20px;
            text-align: center;
            border-bottom-left-radius: 20px;
            border-bottom-right-radius: 20px;
            margin-left: -1rem;
            margin-right: -1rem;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0, 150, 97, 0.2);
        }
        .top-header h1 {
            color: white !important;
            font-weight: 800 !important;
            font-size: 2.2rem !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .top-header p {
            color: #e0f2fe !important;
            font-size: 1.05rem !important;
            margin-top: 8px !important;
            margin-bottom: 0 !important;
        }

        /* --- כרטיסיה לבנה מעוצבת (Card Style) --- */
        .css-card {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            border: 1px solid #eef0f2;
            margin-bottom: 20px;
        }
        
        .card-title {
            color: #111827;
            font-weight: 700;
            font-size: 1.25rem;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* עיצוב שדות קלט ותפריטים */
        input, textarea, .stSelectbox, div[data-baseweb="select"] {
            direction: rtl !important;
            text-align: right !important;
            border-radius: 10px !important;
        }
        
        div[data-baseweb="input"] {
            border-radius: 10px !important;
        }

        /* עיצוב לשוניות (Tabs) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f8fafc;
            padding: 4px;
            border-radius: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            font-weight: 600;
        }

        /* --- כפתור ירוק בולט (כמו בתמונה) --- */
        .stButton button[kind="primary"] {
            background-color: #009661 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            font-size: 1.2rem !important;
            border-radius: 12px !important;
            padding: 14px 28px !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(0, 150, 97, 0.3) !important;
            width: 100% !important;
            transition: all 0.2s ease !important;
        }
        .stButton button[kind="primary"]:hover {
            background-color: #007d51 !important;
            transform: translateY(-1px);
        }

        /* יישור הודעות ותשובות */
        .stAlert {
            direction: rtl;
            text-align: right;
            border-radius: 12px;
        }
    </style>
""", unsafe_allow_html=True)

# --- באנר כותרת עליון ---
st.markdown("""
    <div class="top-header">
        <h1>🧺 מחשבון ומסיר הכתמים החכם</h1>
        <p>אבחון מהיר וטיפול מדויק מבוסס AI לפי סוג הכתם והבד</p>
    </div>
""", unsafe_allow_html=True)

# טעינת מפתח ה-API מתוך Secrets או מתיבת הקלט
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        API_KEY = st.text_input("🔑 הזן מפתח API של Gemini להפעלת המערכת:", type="password")
        st.markdown('</div>', unsafe_allow_html=True)

if API_KEY:
    try:
        genai.configure(api_key=API_KEY.strip())

        # --- כרטיסיה 1: פרטי הכתם ---
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🧼 זיהוי הכתם והבד</div>', unsafe_allow_html=True)
        
        stain_text = st.text_input(
            "ממה נגרם הכתם?", 
            placeholder="לדוגמה: יין אדום, קפה, שמן מנוע, רוטב עגבניות..."
        )
        
        fabric_type = st.selectbox(
            "מאיזה בד עשוי הבגד?",
            ["כותנה", "ג'ינס", "סינתטי (פוליאסטר)", "משי / עדין", "צמר", "לא בטוח/ה"]
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # --- כרטיסיה 2: צילום / העלאת תמונה ---
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📸 תמונת הכתם (אימות ויזואלי)</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📷 צילום במצלמה", "📁 העלאה מהגלריה"])
        image_file = None

        with tab1:
            camera_photo = st.camera_input("צלמו את הכתם מקרוב:")
            if camera_photo:
                image_file = camera_photo

        with tab2:
            uploaded_file = st.file_uploader("בחרו תמונה מהמכשיר:", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                image_file = uploaded_file

        image = None
        if image_file:
            image = Image.open(image_file).convert("RGB")
            if image_file == uploaded_file:
                st.image(image, caption="התמונה שהועלתה", use_column_width=True)
                
        st.markdown('</div>', unsafe_allow_html=True)

        # --- כפתור הפעלה מרכזי ---
        if st.button("🚀 חשב הוראות ניקוי", type="primary"):
            if not stain_text and not image:
                st.warning("אנא רשמו ממה נגרם הכתם או צלמו/העלו תמונה.")
            else:
                with st.spinner("מנתח את הכתם ומכין תוכנית ניקוי..."):
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
                        # --- כרטיסיית תוצאה מעוצבת ---
                        st.markdown('<div class="css-card">', unsafe_allow_html=True)
                        st.markdown('<div class="card-title" style="color: #009661;">✨ הנחיות הטיפול וההסרה</div>', unsafe_allow_html=True)
                        st.markdown(f"<div style='direction: rtl; text-align: right;'>{response.text}</div>", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"לא ניתן היה להתחבר למודלים. שגיאה אחרונה: {last_error}")

    except Exception as e:
        st.error(f"אירעה שגיאה בחיבור ל-AI: {e}")
