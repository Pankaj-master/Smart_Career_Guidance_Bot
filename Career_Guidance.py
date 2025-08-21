import os
import streamlit as st
import requests
import json
from dotenv import load_dotenv

# ========== LOAD GEMINI API KEY SECURELY ==========
GEMINI_API_KEY = ""  # Default placeholder

# First try to get from Streamlit secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# If not found, try from .env
if not GEMINI_API_KEY:
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Error if still not found
if not GEMINI_API_KEY:
    st.error("❌ API Key not found. Please add it to .env or Streamlit secrets.")
    st.stop()

# ========== API URL ==========
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# ========== CAREER GUIDANCE FUNCTION ==========
def get_career_guidance(user_input: str) -> str:
    headers = {
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are a professional career guidance expert.
    Analyze the user's profile below and suggest 3 suitable, future-proof career options. Be supportive, insightful, and motivational.

    Each suggestion must include:
    - A bold career title
    - A 2–3 line description of why it's a good fit
    - A clickable and trusted resource link using [text](URL) format

    Add a closing line: "🌟 You've got this! Explore what excites you and build a future you love."

    User Profile:
    {user_input}

    Response format:
    1. **Career Title**  
       Description  
       🔗 [Link Text](URL)

    2. ...
    3. ...
    """

    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ========== STREAMLIT UI ==========
st.set_page_config(page_title="Career Guidance Chatbot", page_icon="🎯")

with st.sidebar:
    st.title("🧭 About This App")
    st.info("This AI-powered chatbot helps you explore personalized career paths based on your skills, interests, and education.")
    st.markdown("🔗 Powered by [Gemini API](https://aistudio.google.com/)")

st.title("🎯 Career Guidance Chatbot")
st.markdown("Describe your **skills**, **interests**, and **education background**. Get personalized and practical career suggestions.")

# Session history
if "history" not in st.session_state:
    st.session_state.history = []

# User input
user_input = st.text_area("🧑‍🎓 Your Background", height=150, placeholder="E.g., I love tech and solving problems, have a B.Sc. in Computer Science, and enjoy designing websites...")

if st.button("Get Career Advice"):
    if user_input.strip():
        with st.spinner("🤖 Thinking..."):
            result = get_career_guidance(user_input)
            st.session_state.history.append((user_input, result))
    else:
        st.warning("⚠️ Please enter your background info to get advice.")

# Display chat history
if st.session_state.history:
    st.markdown("### 📌 Suggested Careers")
    for i, (q, a) in enumerate(reversed(st.session_state.history), 1):
        st.markdown(f"**🧑‍🎓 You:** {q}")
        st.markdown(f"**🤖 Chatbot:**\n{a}", unsafe_allow_html=True)
        st.markdown("---")

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.caption("💡 Tip: Ask again with different skills or interests to explore more career paths.")
