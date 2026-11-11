import streamlit as st
import json
import os
import uuid
from dotenv import load_dotenv
import ollama

# Load environment variables
load_dotenv()
ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "admin123")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.1")

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="AI Biography Bot", page_icon="👤", layout="wide")

# --- Custom CSS for UI/UX Improvement ---
st.markdown("""
<style>
    /* Global styling */
    .main {background-color: #F8F9FA;}
    
    /* Custom Headers */
    .main-title {
        font-size: 3rem;
        color: #1E3A8A;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Cards for Dashboard */
    .profile-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-left: 5px solid #1E3A8A;
    }
    
    /* Login Box */
    .login-box {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        max-width: 500px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)


class JSONDatabaseManager:
    def __init__(self, db_path="database.json"):
        self.db_path = db_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.db_path):
            self.save_data([])

    def get_all_records(self):
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def save_data(self, data):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add_record(self, data_dict):
        records = self.get_all_records()
        new_record = {"id": str(uuid.uuid4())[:8], **data_dict}
        records.append(new_record)
        self.save_data(records)
        return new_record

db_manager = JSONDatabaseManager()

# --- Sidebar Navigation ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.markdown("### Navigation")
    page = st.radio("Go to", ["🤖 AI Chat Assistant", "🛡️ Admin Dashboard"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"**Engine:** Ollama Local\n**Model:** `{MODEL_NAME}`")
    st.markdown("💡 *Object-Oriented Architecture (Week 3)*")

# --- Page 1: AI Chat Assistant ---
if page == "🤖 AI Chat Assistant":
    st.markdown('<div class="main-title">👤 AI Biography Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Ask anything about the profiles in the database</div>', unsafe_allow_html=True)

    # Load context from NoSQL JSON
    records = db_manager.get_all_records()
    context_str = "Biography Database:\n"
    for r in records:
        context_str += f"""
        - Name: {r.get('full_name')}
          Father: {r.get('father_name')}, Grandfather: {r.get('grandfather_name')}
          Children: {r.get('children_names')}
          Birthplace: {r.get('thana')}, {r.get('district')}, {r.get('country')}
          Life Story: {r.get('life_story')}
        -------------------
"""

    # Chat UI container
    chat_container = st.container()
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": "Hello! I am ready to answer questions about the biographies in my database. Who would you like to know about?"}]

    with chat_container:
        for msg in st.session_state.chat_history:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    if prompt := st.chat_input("E.g., Where was this person born? What are the names of their children?"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Searching biography database..."):
                system_prompt = f"You are a helpful biography assistant. Use the following profiles to answer the user's questions. Answer nicely and politely. If the answer isn't in the database, say so.\n\n{context_str}"
                
                try:
                    response = ollama.chat(model=MODEL_NAME, messages=[
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': prompt}
                    ])
                    reply = response['message']['content']
                    st.markdown(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error connecting to Ollama: {e}")
                    st.info("Make sure you run `ollama serve` in your terminal.")

# --- Page 2: Admin Dashboard ---
elif page == "🛡️ Admin Dashboard":
    st.markdown('<div class="main-title">🛡️ Admin Control Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Manage Biographies & Life Histories</div>', unsafe_allow_html=True)
    
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False

    if not st.session_state.is_authenticated:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("### 🔒 Secure Login")
        username = st.text_input("Admin Username")
        password = st.text_input("Password", type="password")
        if st.button("Access Dashboard", use_container_width=True, type="primary"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.is_authenticated = True
                st.rerun()
            else:
                st.error("Invalid Credentials!")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        col_a, col_b = st.columns([8, 2])
        col_a.success("✅ Authenticated as Administrator")
        if col_b.button("Logout 🚪", use_container_width=True):
            st.session_state.is_authenticated = False
            st.rerun()
            
        st.markdown("---")
        
        # Dashboard Metrics
        records = db_manager.get_all_records()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Profiles", len(records))
        col2.metric("Database Status", "Active")
        col3.metric("Storage Type", "NoSQL (JSON)")
        
        st.markdown("### ➕ Add New Biography")
        with st.form("add_bio_form", clear_on_submit=True):
            st.markdown("**Personal Details**")
            c1, c2, c3 = st.columns(3)
            full_name = c1.text_input("Full Name *")
            father_name = c2.text_input("Father's Name")
            grandfather_name = c3.text_input("Grandfather's Name")
            
            st.markdown("**Family & Location**")
            c4, c5 = st.columns(2)
            children_names = c4.text_input("Children's Names (Comma separated)")
            country = c5.text_input("Country of Birth")
            
            c6, c7 = st.columns(2)
            district = c6.text_input("District")
            thana = c7.text_input("Thana / Upazila")
            
            st.markdown("**Detailed Life Story**")
            life_story = st.text_area("Write the complete biography, achievements, and other important information here...", height=150)
            
            submitted = st.form_submit_button("💾 Save Profile to Database", type="primary")
            if submitted:
                if full_name:
                    data_dict = {
                        "full_name": full_name,
                        "father_name": father_name,
                        "grandfather_name": grandfather_name,
                        "children_names": children_names,
                        "country": country,
                        "district": district,
                        "thana": thana,
                        "life_story": life_story
                    }
                    db_manager.add_record(data_dict)
                    st.success(f"Profile for '{full_name}' successfully added!")
                else:
                    st.error("Full Name is a required field.")
                    
        st.markdown("---")
        st.markdown("### 🗂️ Current Database Records")
        for rec in records:
            with st.expander(f"👤 {rec.get('full_name')} ({rec.get('district')}, {rec.get('country')})"):
                st.json(rec)
