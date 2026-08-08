import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="מסיר הכתמים החכם", page_icon="🧺", layout="centered")

st.title("🧺 מסיר הכתמים החכם")
st.write("צלמו את הכתם או ספרו לנו ממה הוא נוצר, ולקבל הנחיות מדויקות להסרתו!")

# טעינת מפתח ה-API מתוך Secrets או מתיבת הקלט
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    API_KEY = st.sidebar.text_input("הזן מפתח API של Gemini:", type="password")

if API_KEY:
    try:
        # ניקוי רווחים מיותרים במפתח
        genai.configure(api_key=API_KEY.strip())
        model = genai.GenerativeModel('gemini-1.5-flash')

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
            # המרה אוטומטית ל-RGB פותרת את שגיאת InvalidArgument
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
                    
                    החזר את התשובה בעברית, בפורמט מעוצב, ברור וידידותי.
                    """
                    
                    inputs = [prompt]
                    if image:
                        inputs.append(image)
                    
                    response = model.generate_content(inputs)
                    st.success("הנה מה שצריך לעשות:")
                    st.markdown(response.text)

    except Exception as e:
        st.error(f"אירעה שגיאה בחיבור ל-AI: {e}")
else:
    st.info("כדי להפעיל את האפליקציה, יש להזין מפתח Google Gemini API בסרגל הצד או ב-Secrets.")
