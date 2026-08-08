import streamlit as st
import google.generativeai as genai
from PIL import Image

# הגדרת עיצוב הדף
st.set_page_config(page_title="מסיר הכתמים החכם", page_icon="🧺", layout="centered")

# --- הגדרת תמיכה מלאה ב-RTL (מימין לשמאל) ---
st.markdown("""
    <style>
        /* כיוון כללי של האפליקציה ויישור טקסט */
        .stApp, .main, .block-container {
            direction: rtl;
            text-align: right;
        }
        
        /* יישור לימין של כותרות ופסקאות */
        h1, h2, h3, h4, h5, h6, p, div {
            text-align: right;
        }

        /* כיוון סרגל הצד (Sidebar) */
        section[data-testid="stSidebar"] {
            direction: rtl;
            text-align: right;
        }

        /* יישור שדות קלט ותפריטים נפתחים */
        input, textarea, .stSelectbox, div[data-baseweb="select"], div[data-baseweb="base-input"] {
            direction: rtl !important;
            text-align: right !important;
        }

        /* יישור הודעות מערכת */
        .stAlert, div[data-baseweb="notification"] {
            direction: rtl;
            text-align: right;
        }

        /* עיצוב כפתור ההפעלה */
        .stButton button {
            width: 100%;
        }

        /* יישור תוכן ה-Markdown */
        .stMarkdown, .stMarkdown p, .stMarkdown ul, .stMarkdown li {
            text-align: right !important;
            direction: rtl !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🧺 מסיר הכתמים החכם")
st.write("צלמו את הכתם או ספרו לנו ממה הוא נוצר, וקבלו הנחיות מדויקות להסרתו!")

# טעינת מפתח ה-API מתוך Secrets או מתיבת הקלט
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    API_KEY = st.sidebar.text_input("הזן מפתח API של Gemini:", type="password")

if API_KEY:
    try:
        # ניקוי רווחים והגדרת ה-API
        genai.configure(api_key=API_KEY.strip())

        st.subheader("1. פרטי הכתם")
        stain_text = st.text_input("ממה נגרם הכתם? (לדוגמה: יין אדום, קפה, שמן):")
        fabric_type = st.selectbox(
            "מאיזה בד עשוי הבגד?",
            ["כותנה", "ג'ינס", "סינתטי (פוליאסטר)", "משי / עדין", "צמר", "לא בטוח/ה"]
        )

        st.subheader("2. תמונת הכתם (אופציונלי אך מומלץ)")
        uploaded_file = st.file_uploader("העלו תמונה של הכתם לאימות:", type=["jpg", "jpeg", "png"])
        
        image = None
        if uploaded_file:
            # המרה ל-RGB כדי למנוע שגיאות שקיפות
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="התמונה שהועלתה", use_column_width=True)

        if st.button("🚀 איך מנקים את זה?", type="primary"):
            if not stain_text and not image:
                st.warning("אנא רשמו ממה נגרם הכתם או העלו תמונה.")
            else:
                with st.spinner("מנתח את הכתם ומכין הוראות ניקוי..."):
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
                    
                    # רשימת מודלים עדכניים לפי סדר עדיפויות
                    candidate_models = [
                        'gemini-2.0-flash',
                        'gemini-1.5-flash-latest',
                        'gemini-1.5-pro-latest',
                        'gemini-1.5-flash',
                        'gemini-1.5-pro'
                    ]
                    
                    # הוספת מודלים נתמכים נוספים מתוך החשבון
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

                    # ניסיון שליחה בפועל לכל מודל - אם מודל מוחזר כ-Deprecated, הלולאה תמשיך לסיבוב הבא
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
                        st.success("הנה מה שצריך לעשות:")
                        st.markdown(f"<div style='direction: rtl; text-align: right;'>{response.text}</div>", unsafe_allow_html=True)
                    else:
                        st.error(f"לא ניתן היה להתחבר למודלים. שגיאה אחרונה: {last_error}")

    except Exception as e:
        st.error(f"אירעה שגיאה בחיבור ל-AI: {e}")
else:
    st.info("כדי להפעיל את האפליקציה, יש להזין מפתח Google Gemini API בסרגל הצד (או להגדיר ב-Secrets).")
