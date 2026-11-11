import streamlit as st
import json
import os
import glob
import requests
from dotenv import load_dotenv

load_dotenv()
ADMIN_USER = os.getenv("ADMIN_USERNAME", "shafiul")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "admin123")

st.set_page_config(page_title="AI Biography Chatbot", page_icon="🤖", layout="wide")

st.markdown('''
<style>
    .main-header { font-size: 2.5rem; color: #1E3A8A; text-align: center; font-weight: 800; margin-bottom: 0px; }
    .sub-header { font-size: 1.1rem; color: #6B7280; text-align: center; margin-bottom: 30px; }
    .profile-card { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #3B82F6; margin-bottom: 10px; }
    .admin-header { color: #B91C1C; font-weight: bold; }
</style>
''', unsafe_allow_html=True)

DATA_DIR = "data"
USER_ADDED_FILE = os.path.join(DATA_DIR, "user_added.json")

@st.cache_data
def load_all_data():
    all_data = []
    for filepath in glob.glob(os.path.join(DATA_DIR, "*.json")):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    all_data.extend(file_data)
            except Exception as e:
                pass
    return all_data

db_data = load_all_data()

def get_context_for_llm(query, all_data):
    # Always include primary user profile so the AI knows who "I" or "my" is
    context = []
    for p in all_data:
        if p.get("Name") == "Mohammad Shafiul Azam":
            context.append(p)
            break
    
    # Simple search for other names in the massive database if mentioned in query
    query_lower = query.lower()
    for p in all_data:
        if p.get("Name") != "Mohammad Shafiul Azam":
            if str(p.get("Name", "")).lower() in query_lower or str(p.get("Bengali_Name", "")).lower() in query_lower:
                context.append(p)
                if len(context) >= 3: # Keep context window small for local models
                    break
    return context

def ask_ollama(model_name, prompt, context, lang):
    lang_inst = "in Bengali (বাংলা)" if lang == "বাংলা (Bengali)" else "in English"
    system_instruction = (
        f"You are a highly intelligent Personal Assistant. Answer the user's question {lang_inst}. "
        f"Base your answers STRICTLY on the following JSON database. "
        f"IMPORTANT: If the user asks about 'my name', 'my district', 'my children', or uses 'I', 'me', 'my', "
        f"they are referring to the primary person in this database: Mohammad Shafiul Azam. "
        f"Act confidently based on this data: {json.dumps(context, ensure_ascii=False)}"
    )
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    try:
        res = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
        res.raise_for_status()
        return res.json()["message"]["content"]
    except requests.exceptions.ConnectionError:
        return "❌ Error: Could not connect to local Ollama. Please make sure Ollama is running (`ollama run qwen3:0.6b`)."
    except Exception as e:
        return f"❌ Error: {e}"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
st.sidebar.title("📌 মেনু / Menu")
app_mode = st.sidebar.radio("Go to", ["💬 Chatbot", "🔐 Admin Panel"])
st.sidebar.markdown("---")

if app_mode == "💬 Chatbot":
    st.sidebar.title("⚙️ সেটিংস / Settings")
    language = st.sidebar.radio("🌐 Language / ভাষা", ["বাংলা (Bengali)", "English"])
    model_env = st.sidebar.radio("☁️ এনভায়রনমেন্ট / Environment", ["Local (Ollama)", "Cloud (API)"])
    
    if model_env == "Local (Ollama)":
        selected_model = st.sidebar.selectbox("🧠 মডেল / Model", ["qwen3:0.6b", "llama3.2:3b", "mistral:7b"])
    else:
        selected_model = st.sidebar.selectbox("🧠 মডেল / Model", ["Gemini 1.5 Pro", "GPT-4o"])

    if language == "বাংলা (Bengali)":
        st.markdown('<div class="main-header">🤖 এআই বায়োগ্রাফি চ্যাটবট (Live)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub-header">নলেজ বেস ডেটা: {len(db_data):,} টি প্রোফাইল সংযুক্ত</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="main-header">🤖 AI Biography Chatbot (Live)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub-header">Knowledge Base: {len(db_data):,} Profiles connected</div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("আপনার প্রশ্ন লিখুন... / Type your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("মডেল উত্তর তৈরি করছে... (Model is thinking...)"):
                if model_env == "Local (Ollama)":
                    rel_context = get_context_for_llm(prompt, db_data)
                    response = ask_ollama(selected_model, prompt, rel_context, language)
                else:
                    response = "Cloud API is not configured yet. Please use Local (Ollama) for testing."
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

elif app_mode == "🔐 Admin Panel":
    st.markdown('<div class="main-header admin-header">🔐 এডমিন প্যানেল</div>', unsafe_allow_html=True)

    if not st.session_state.admin_logged_in:
        st.warning("Please log in. (Default: shafiul / admin123)")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login") and username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.admin_logged_in = True
                st.rerun()
    else:
        st.success(f"Logged in as: {ADMIN_USER}")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()
