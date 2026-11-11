import streamlit as st
import os

# Page Config
st.set_page_config(page_title="AI Bibliography Chatbot", layout="wide")

# Sidebar for Settings
st.sidebar.title("⚙️ Settings / সেটিংস")

# Model Selection
model_type = st.sidebar.radio("Select Model Type / মডেল ধরন", ["Local (Ollama)", "Cloud (API)"])

if model_type == "Local (Ollama)":
    # Adding the requested model from the image
    selected_model = st.sidebar.selectbox("Choose Local Model / লোকাল মডেল", ["qwen3:0.6b", "llama3.2:3b", "mistral:7b"])
else:
    selected_model = st.sidebar.selectbox("Choose Cloud Model / ক্লাউড মডেল", ["GPT-4o", "Gemini 1.5 Pro", "Claude 3.5 Sonnet"])

# Language Selection
language = st.sidebar.selectbox("Select Language / ভাষা নির্বাচন করুন", ["বাংলা (Bengali)", "English"])

st.title("📚 AI Bibliography Chatbot")

if language == "বাংলা (Bengali)":
    st.markdown(f"**বর্তমান মডেল:** `{selected_model}` ({model_type})")
    st.write("স্বাগতম! আপনার রেফারেন্স বা গ্রন্থপঞ্জি সম্পর্কিত প্রশ্ন নিচে লিখুন।")
    prompt_placeholder = "এখানে আপনার প্রশ্ন লিখুন..."
else:
    st.markdown(f"**Current Model:** `{selected_model}` ({model_type})")
    st.write("Welcome! Ask your bibliography or reference-related questions below.")
    prompt_placeholder = "Type your question here..."

# Chat UI
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input(prompt_placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Mock AI response
    with st.chat_message("assistant"):
        if language == "বাংলা (Bengali)":
            response = f"`{selected_model}` মডেল থেকে উত্তর দেওয়া হচ্ছে... (এটি একটি ডেমো উত্তর)"
        else:
            response = f"Generating response from `{selected_model}`... (This is a demo response)"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
