import streamlit as st
import ollama
from openai import OpenAI

# ----------------- পেজ কনফিগারেশন -----------------
st.set_page_config(
    page_title="Personal AI Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- কাস্টম প্রিমিয়াম CSS স্টাইলিং -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #1e1b4b 100%);
        color: #f8fafc;
    }

    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.88);
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    .chat-bubble-user {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: #ffffff;
        padding: 14px 18px;
        border-radius: 18px 18px 4px 18px;
        margin-bottom: 14px;
        max-width: 78%;
        margin-left: auto;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
        line-height: 1.6;
        word-wrap: break-word;
    }

    .chat-bubble-ai {
        background: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #f1f5f9;
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        margin-bottom: 14px;
        max-width: 82%;
        margin-right: auto;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        line-height: 1.6;
        word-wrap: break-word;
    }

    .stChatInputContainer {
        border-radius: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        background-color: rgba(15, 23, 42, 0.95) !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- সাইডবার সেটিংস -----------------
with st.sidebar:
    st.markdown("## ⚙️ Engine Settings")
    st.markdown("আপনার পছন্দমতো মডেল এবং হোস্ট নির্বাচন করুন।")

    engine_mode = st.radio(
        "Mode Selection",
        ["🏠 Local (Ollama)", "☁️ Cloud (OpenAI / Groq)"],
        index=0
    )

    if "Local" in engine_mode:
        st.info("লোকাল ব্যাকএন্ড: কম্পিউটারে `ollama serve` চালু রাখুন।")
        model_name = st.selectbox(
            "Select Local Model",
            ["qwen3:0.6b", "llama3.2:latest", "mistral:latest", "qwen2.5:latest", "custom"],
            index=0
        )
        if model_name == "custom":
            model_name = st.text_input("Custom Model Name", value="qwen3:0.6b")
        ollama_host = st.text_input("Ollama Host URL", value="http://localhost:11434")

    else:
        st.info("ক্লাউড ব্যাকএন্ড: আপনার API Key দিন।")
        api_key = st.text_input("Cloud API Key", type="password")
        base_url = st.text_input("Base URL (Groq/OpenAI)", value="https://api.groq.com/openai/v1")
        model_name = st.selectbox(
            "Select Cloud Model",
            ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gpt-4o-mini"],
            index=0
        )

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ----------------- সেশন স্টেট হ্যান্ডলিং -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- মেইন চ্যাট ইন্টারফেস -----------------
st.markdown("## ⚡ Personal AI Workspace")
st.caption(f"Active Mode: **{'Local Ollama' if 'Local' in engine_mode else 'Cloud API'}** | Model: **`{model_name}`**")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)

if user_prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    st.markdown(f'<div class="chat-bubble-user">{user_prompt}</div>', unsafe_allow_html=True)

    with st.spinner("AI ভাবছে..."):
        full_response = ""
        try:
            if "Local" in engine_mode:
                client = ollama.Client(host=ollama_host)
                response = client.chat(
                    model=model_name,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                )
                full_response = response['message']['content']

            else:
                if not api_key:
                    full_response = "⚠️ অনুগ্রহ করে সাইডবারে আপনার Cloud API Key প্রদান করুন।"
                else:
                    client = OpenAI(api_key=api_key, base_url=base_url)
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    )
                    full_response = response.choices[0].message.content

            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.markdown(f'<div class="chat-bubble-ai">{full_response}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {str(e)}")
