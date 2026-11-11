import streamlit as st
import json
import os
import glob
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ADMIN_USER = os.getenv("ADMIN_USERNAME", "shafiul")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "admin123")

# Page Config
st.set_page_config(page_title="AI Biography Chatbot", page_icon="🤖", layout="wide")

st.markdown('''
<style>
    .main-header { font-size: 2.5rem; color: #1E3A8A; text-align: center; font-weight: 800; margin-bottom: 0px; }
    .sub-header { font-size: 1.1rem; color: #6B7280; text-align: center; margin-bottom: 30px; }
    .profile-card { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #3B82F6; margin-bottom: 10px; }
    .admin-header { color: #B91C1C; font-weight: bold; }
</style>
''', unsafe_allow_html=True)

# Load Database from 'data' folder
DATA_DIR = "data"
USER_ADDED_FILE = os.path.join(DATA_DIR, "user_added.json")

@st.cache_data
def load_all_data():
    all_data = []
    # Read all json files in data folder
    for filepath in glob.glob(os.path.join(DATA_DIR, "*.json")):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    all_data.extend(file_data)
            except Exception as e:
                st.error(f"Error loading {filepath}: {e}")
    return all_data

def save_new_entry(new_entry):
    # Always append to user_added.json to keep original data safe
    if os.path.exists(USER_ADDED_FILE):
        with open(USER_ADDED_FILE, "r", encoding="utf-8") as f:
            current_data = json.load(f)
    else:
        current_data = []
        
    current_data.append(new_entry)
    
    with open(USER_ADDED_FILE, "w", encoding="utf-8") as f:
        json.dump(current_data, f, ensure_ascii=False, indent=4)
    
    st.cache_data.clear() # Clear cache so new data is loaded

db_data = load_all_data()

# Session State for Admin Login
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# Sidebar Navigation
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
        selected_model = st.sidebar.selectbox("🧠 মডেল / Model", ["Gemini 1.5 Pro", "GPT-4o", "Claude 3.5 Sonnet"])

    if language == "বাংলা (Bengali)":
        st.markdown('<div class="main-header">🤖 এআই বায়োগ্রাফি চ্যাটবট</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub-header">নলেজ বেস ডেটা: {len(db_data):,} টি প্রোফাইল</div>', unsafe_allow_html=True)
        st.info(f"**বর্তমান মডেল:** `{selected_model}` ({model_env})")
        prompt_placeholder = "আপনার প্রশ্ন লিখুন..."
    else:
        st.markdown('<div class="main-header">🤖 AI Biography Chatbot</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub-header">Knowledge Base: {len(db_data):,} Profiles</div>', unsafe_allow_html=True)
        st.info(f"**Current Model:** `{selected_model}` ({model_env})")
        prompt_placeholder = "Type your question..."

    # Performance tweak: only show first 50 records in UI to prevent browser crash
    with st.expander(f"📂 ডাটাবেস প্রোফাইল দেখুন (Showing top 50 of {len(db_data):,})"):
        for person in db_data[:50]:
            st.markdown(f'''
            <div class="profile-card">
                <h4>{person.get('Name')} ({person.get('Bengali_Name', '')})</h4>
                <p><b>Profession:</b> {person.get('Profession')}<br>
                <b>Home:</b> {person.get('Village', '')}, {person.get('Home_District', '')}</p>
            </div>
            ''', unsafe_allow_html=True)

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
                response = f"**`{selected_model}`** মডেল {len(db_data):,} টি ডেটা থেকে আপনার প্রশ্নের উত্তর খুঁজছে... (এটি একটি ডেমো রেসপন্স)"
            else:
                response = f"**`{selected_model}`** is searching through {len(db_data):,} records for the answer... (Demo response)"
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

elif app_mode == "🔐 Admin Panel":
    st.markdown('<div class="main-header admin-header">🔐 এডমিন প্যানেল / Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Total Knowledge Base Items: <b>{len(db_data):,}</b></div>', unsafe_allow_html=True)

    if not st.session_state.admin_logged_in:
        st.warning("Please log in. (Default: shafiul / admin123)")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username == ADMIN_USER and password == ADMIN_PASS:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid Username or Password!")
    else:
        st.success(f"Logged in as: {ADMIN_USER}")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()
        
        st.markdown("### ➕ Train AI / Add New Biography")
        with st.form("add_data_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full Name (English)")
                new_district = st.text_input("Home District")
                new_prof = st.text_input("Profession")
            with col2:
                new_bengali_name = st.text_input("Bengali Name (বাংলা নাম)")
                new_village = st.text_input("Village/Area")
                new_school = st.text_input("School/College")
            
            add_submit = st.form_submit_button("Save to Knowledge Base")
            
            if add_submit:
                if new_name:
                    new_entry = {
                        "Name": new_name,
                        "Bengali_Name": new_bengali_name,
                        "Home_District": new_district,
                        "Village": new_village,
                        "Profession": new_prof,
                        "Education": {"School": new_school}
                    }
                    save_new_entry(new_entry)
                    st.success(f"Successfully trained AI with new profile: {new_name}")
                else:
                    st.error("Name is required!")
