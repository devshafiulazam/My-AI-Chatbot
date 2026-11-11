import streamlit as st
import json
import os

# Page Config
st.set_page_config(page_title="AI Biography Chatbot", page_icon="🤖", layout="wide")

# Custom CSS for Eye-Catching UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 30px;
    }
    .profile-card {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Load Database
@st.cache_data
def load_db():
    if os.path.exists("database.json"):
        with open("database.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

db_data = load_db()

# Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
st.sidebar.title("⚙️ সেটিংস / Settings")

# Language Selection
language = st.sidebar.radio("🌐 Language / ভাষা", ["বাংলা (Bengali)", "English"])

st.sidebar.markdown("---")

# Model Selection
model_env = st.sidebar.radio("☁️ এনভায়রনমেন্ট / Environment", ["Local (Ollama)", "Cloud (API)"])

if model_env == "Local (Ollama)":
    # Added qwen3:0.6b as requested
    selected_model = st.sidebar.selectbox("🧠 মডেল / Model", ["qwen3:0.6b", "llama3.2:3b", "mistral:7b"])
else:
    selected_model = st.sidebar.selectbox("🧠 মডেল / Model", ["Gemini 1.5 Pro", "GPT-4o", "Claude 3.5 Sonnet"])

# Main UI
if language == "বাংলা (Bengali)":
    st.markdown('<div class="main-header">🤖 এআই বায়োগ্রাফি চ্যাটবট</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">আপনার ব্যক্তিগত তথ্য এবং প্রোফাইল ভিত্তিক ইন্টারেক্টিভ চ্যাট সিস্টেম</div>', unsafe_allow_html=True)
    st.info(f"**বর্তমান মডেল:** `{selected_model}` ({model_env})")
    prompt_placeholder = "আপনার প্রশ্ন লিখুন (যেমন: শফিউল আজমের শিক্ষাগত যোগ্যতা কী?)..."
else:
    st.markdown('<div class="main-header">🤖 AI Biography Chatbot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Interactive chat system based on personal profiles and data</div>', unsafe_allow_html=True)
    st.info(f"**Current Model:** `{selected_model}` ({model_env})")
    prompt_placeholder = "Type your question (e.g., What is the profession of Shafiul Azam?)..."

# Show DB Data in UI (Collapsible)
with st.expander("📂 ডাটাবেস প্রোফাইল দেখুন / View Database Profiles"):
    for person in db_data:
        st.markdown(f"""
        <div class="profile-card">
            <h4>{person.get('Name')} ({person.get('Bengali_Name')})</h4>
            <p><b>Profession:</b> {person.get('Profession')}<br>
            <b>Home:</b> {person.get('Village')}, {person.get('Home_District')}</p>
        </div>
        """, unsafe_allow_html=True)

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input(prompt_placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        if language == "বাংলা (Bengali)":
            response = f"**`{selected_model}`** মডেল থেকে বিশ্লেষণ করা হচ্ছে...

ডাটাবেস অনুযায়ী, আমি আপনার প্রশ্নের উত্তর খুঁজছি। (এটি একটি ডেমো রেসপন্স)"
        else:
            response = f"Analyzing using **`{selected_model}`**...

Based on the database, I am retrieving the answer. (This is a demo response)"
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
