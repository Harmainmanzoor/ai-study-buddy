import io
import streamlit as st
import google.genai as genai
from google.genai import types
from gtts import gTTS
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="AI Study Buddy", page_icon="🎓", layout="wide")
st.title("🎓 AI Study Buddy for Your Syllabus")
st.write("Upload notes, snap pictures of textbooks, generate quizzes, or ask questions by voice!")

# 2. Initialize Gemini Client (pulls from your .streamlit/secrets.toml)
MODEL_NAME = "gemini-2.5-flash"
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API Connection Error. Please verify your secrets.toml file configuration.")
    st.stop()

# Helper function for AI text responses
def generate_ai_response(prompt_content):
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt_content)
        return response.text
    except Exception as err:
        return f"AI Processing Error: {err}"

# Helper function for Text-to-Speech (Read Aloud)
def generate_audio_bytes(text_to_speak, language_code='en'):
    try:
        fp = io.BytesIO()
        # Clean markdown symbols before speaking
        clean_text = text_to_speak.replace("*", "").replace("#", "").replace("-", "")
        tts = gTTS(text=clean_text[:1200], lang=language_code)
        tts.write_to_fp(fp)
        return fp.getvalue()
    except Exception as e:
        st.error(f"Audio Generation Error: {e}")
        return None

# --- APP LAYOUT: FEATURE TABS ---
tab1, tab2, tab3 = st.tabs(["📸 Snap & Simplify (OCR)", "🎤 Voice Questions", "📝 Quizzes & Flashcards"])

# ==========================================
# FEATURE 1 & 2: SNAP & READ (OCR) + SIMPLIFY
# ==========================================
with tab1:
    st.header("📸 Textbook Snap & Simplify")
    st.write("Take a picture or upload a page to extract text, simplify it, or translate it to Urdu.")
    
    uploaded_file = st.file_uploader("Upload a textbook page or lecture notes", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Page Preview", width=350)
        
        # Operational Mode Choices
        action_mode = st.radio(
            "What should Study Buddy do with this page?",
            ["Extract Exact Text (OCR)", "Simplify Text (Easy English)", "Explain in Urdu (اردو میں ترجمہ کریں)"]
        )
        
        if st.button("Process Document Page"):
            with st.spinner("Analyzing image text..."):
                if "Extract" in action_mode:
                    prompt = ["Perform high-accuracy OCR on this image. Extract and output all visible text exactly as it appears without modifications.", img]
                elif "Simplify" in action_mode:
                    prompt = ["Extract the text from this image page and rewrite it completely in very simple, easy-to-understand language. Perfect for young students or individuals struggling with difficult terms.", img]
                else:
                    prompt = ["Extract the core educational text from this image and explain its key concepts clearly in Urdu (اردو). Use easy Urdu vocabulary.", img]
                
                output_text = generate_ai_response(prompt)
                st.subheader("📝 Study Buddy's Output:")
                st.write(output_text)
                
                # FEATURE 3: READ ALOUD
                st.subheader("🔊 Read Aloud (Text-to-Speech)")
                lang = 'ur' if "Urdu" in action_mode else 'en'
                audio_data = generate_audio_bytes(output_text, language_code=lang)
                if audio_data:
                    st.audio(audio_data, format="audio/mp3")

# ==========================================
# FEATURE 4: VOICE QUESTIONS
# ==========================================
with tab2:
    st.header("🎤 Ask by Voice")
    st.write("Speak your question out loud if you can't type easily, and get a spoken explanation back!")
    
    # Audio recorder widget
    voice_input = st.audio_input("Click to record your study question")
    
    if voice_input:
        with st.spinner("Listening and analyzing your voice prompt..."):
            voice_prompt = [
                types.Part.from_bytes(data=voice_input.getvalue(), mime_type="audio/wav"),
                "Listen to this student's question carefully. Answer it in simple, direct, educational language as an encouraging tutor."
            ]
            
            voice_reply = generate_ai_response(voice_prompt)
            st.subheader("📝 Answer Summary:")
            st.write(voice_reply)
            
            # Read aloud response automatically
            st.subheader("🔊 Audio Explanation Response:")
            reply_audio = generate_audio_bytes(voice_reply, language_code='en')
            if reply_audio:
                st.audio(reply_audio, format="audio/mp3")

# ==========================================
# FEATURE 5: QUIZZES & FLASHCARDS
# ==========================================
with tab3:
    st.header("📝 Quiz & Flashcard Generator")
    st.write("Turn your syllabus topics, chapters, or copy-pasted raw notes into interactive practice materials.")
    
    notes_context = st.text_area("Paste your study topic or textbook paragraph here:")
    quiz_type = st.selectbox("Select Study Tool Type:", ["3 Multiple Choice Questions (MCQs)", "3 Quick Flashcards (Question & Answer pairs)"])
    
    if st.button("Generate Study Materials"):
        if not notes_context.strip():
            st.warning("Please paste some text topic information first!")
        else:
            with st.spinner("Drafting practice assignment questions..."):
                if "MCQs" in quiz_type:
                    prompt = f"Based on this topic content: '{notes_context}', generate a 3-question multiple-choice quiz. Provide options A, B, C, D for each question, and print the correct answers at the absolute bottom."
                else:
                    prompt = f"Based on this topic content: '{notes_context}', generate 3 clear Study Flashcards. Format each clearly as 'Flashcard Front (Question):' and 'Flashcard Back (Answer):'."
                
                quiz_output = generate_ai_response(prompt)
                st.subheader("💡 Practice Tools:")
                st.write(quiz_output)