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

# দাদা, আপনার Week 3 OOP লার্নিং এর সাথে মিল রেখে আমি ডাটাবেস হ্যান্ডলিং এর জন্য একটি Class তৈরি করেছি!
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

    def add_record(self, title, author, year, summary):
        records = self.get_all_records()
        new_record = {
            "id": str(uuid.uuid4())[:8],
            "title": title,
            "author": author,
            "year": year,
            "summary": summary
        }
        records.append(new_record)
        self.save_data(records)
        return new_record

db_manager = JSONDatabaseManager()

# --- Streamlit UI Setup ---
st.set_page_config(page_title="AI Bibliography Bot", page_icon="📚", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🤖 Chatbot Interface", "⚙️ Admin Dashboard"])

if page == "🤖 Chatbot Interface":
    st.title("📚 AI Bibliography Chatbot")
    st.markdown(f"**Running locally on Ollama (Model: `{MODEL_NAME}`)**")

    # Load context from NoSQL JSON
    records = db_manager.get_all_records()
    context_str = "Bibliography Database:\n"
    for r in records:
        context_str += f"- Title: {r['title']}, Author: {r['author']} ({r['year']}). Summary: {r['summary']}\n"

    # Chat UI
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a question about the bibliography..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                system_prompt = f"You are a helpful academic AI assistant. Use the following bibliography database to answer the user's questions. If the answer isn't in the database, say so politely.\n\n{context_str}"
                
                try:
                    response = ollama.chat(model=MODEL_NAME, messages=[
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': prompt}
                    ])
                    reply = response['message']['content']
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error connecting to Ollama: {e}")
                    st.info("Make sure Ollama is running in your terminal/PowerShell using `ollama serve`.")

elif page == "⚙️ Admin Dashboard":
    st.title("⚙️ Admin Dashboard")
    
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False

    if not st.session_state.is_authenticated:
        st.subheader("Login to Access Dashboard")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.is_authenticated = True
                st.rerun()
            else:
                st.error("Invalid Username or Password!")
    else:
        st.success("Logged in successfully!")
        if st.button("Logout"):
            st.session_state.is_authenticated = False
            st.rerun()
            
        st.divider()
        st.subheader("Add New Bibliography Entry")
        
        with st.form("add_bib_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Book/Paper Title")
                author = st.text_input("Author Name")
            with col2:
                year = st.text_input("Publication Year")
            summary = st.text_area("Summary / Notes")
            
            submitted = st.form_submit_button("Save to JSON Database")
            if submitted:
                if title and author:
                    db_manager.add_record(title, author, year, summary)
                    st.success(f"'{title}' added to database!")
                else:
                    st.warning("Title and Author are required fields.")
                    
        st.divider()
        st.subheader("Current Bibliography Backup (NoSQL JSON)")
        st.json(db_manager.get_all_records())
