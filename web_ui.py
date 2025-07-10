# ✅ EcoFriend AI — Final UI Update with Avatars and Fixed Dropdown Width

import streamlit as st
from core_logic import load_model_and_index, chat_with_ecofriend
from langdetect import detect
from deep_translator import GoogleTranslator
from datetime import datetime
import os

# === Page Config ===
st.set_page_config(
    page_title="EcoFriend AI",
    page_icon="🌿",
    layout="wide"
)

# === Load model and index only once ===
@st.cache_resource
def setup():
    return load_model_and_index("app/docs")

llm, embedder, index, doc_chunks = setup()

# === Sidebar Controls ===
st.sidebar.title("⚙ EcoFriend Settings")
if st.sidebar.button("🔁 Refresh"):
    st.session_state.history = []
    st.rerun()

if "prev_level" not in st.session_state:
    st.session_state.prev_level = "beginner"

lang_list = ["auto", "en", "es", "fr", "de", "ta", "hi", "zh", "ar"]
lang_names = {
    "auto": "Auto Detect 🌐", "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "ta": "Tamil", "hi": "Hindi", "zh": "Chinese", "ar": "Arabic"
}
selected_lang = st.sidebar.selectbox("🌍 Reply Language:", lang_list, format_func=lambda x: lang_names.get(x, x))

if "show_logs" not in st.session_state:
    st.session_state.show_logs = False

if st.sidebar.button("📋 View Logs"):
    st.session_state.show_logs = not st.session_state.show_logs

if st.session_state.show_logs:
    st.sidebar.markdown("### 🔗 Chat Logs")
    if os.path.exists("eco_log.txt"):
        with open("eco_log.txt", "r", encoding="utf-8") as f:
            logs = f.readlines()
            st.sidebar.code("".join(logs[-50:]), language="text")
    else:
        st.sidebar.info("No logs available yet.")

# === Title & Info ===
st.markdown("""
<h1 style='display: flex; align-items: center; gap: 10px;'>
    <span>🌿 EcoFriend AI</span>
    <span style='font-size: 16px; opacity: 0.5; margin-left: auto;' title='Link to this section'>🔗</span>
</h1>
<p style='font-size: 16px;'>Welcome to <strong>EcoFriend Assistant</strong> 🌿 — your personal sustainability companion!</p>
<p style='font-size: 16px; margin-top: -10px;'>Ask anything about eco-friendly practices, sustainability, and green living!</p>
""", unsafe_allow_html=True)

# === Compact Dropdown Styling ===
st.markdown("""
<style>
.custom-dropdown .stSelectbox div[data-baseweb="select"] {
    width: 160px !important;
}
</style>
""", unsafe_allow_html=True)

# === Main Level Selector ===
st.markdown("""
<div style='margin-top: 20px; display: grid; align-items: center; gap: 10px;' class='custom-dropdown'>
  <label style='font-size: 14px; font-weight: 500;'>🌱 Choose your Eco Level:</label>
""", unsafe_allow_html=True)

level = st.selectbox(
    label="Choose Level",
    options=["beginner", "explorer", "eco-warrior"],
    index=["beginner", "explorer", "eco-warrior"].index(st.session_state.get("prev_level", "beginner")),
    format_func=str.title,
    key="level_selector_main",
    label_visibility="collapsed"
)

st.markdown("</div>", unsafe_allow_html=True)

if level != st.session_state.prev_level:
    st.session_state.prev_level = level
    level_msg = f"🌿 You've just leveled up to *{level.title()}*! Let's continue your green journey together! 🍃"
    st.session_state.history.append({"role": "assistant", "content": level_msg})

# === Chat History State ===
if "history" not in st.session_state:
    st.session_state.history = []

# === Text Input ===
user_input = st.chat_input("Ask EcoFriend...", key="chat_input")

# === Message Handling ===
if user_input:
    detected_lang = detect(user_input)
    reply_lang = detected_lang if selected_lang == "auto" else selected_lang

    st.session_state.history.append({"role": "user", "content": user_input})

    processed_input = GoogleTranslator(source="auto", target="en").translate(user_input) if detected_lang != "en" else user_input
    response_en = chat_with_ecofriend(processed_input, level, llm, embedder, index, doc_chunks)
    final_response = GoogleTranslator(source="en", target=reply_lang).translate(response_en) if reply_lang != "en" else response_en

    st.session_state.history.append({"role": "assistant", "content": final_response})

    with open("eco_log.txt", "a", encoding="utf-8") as log:
        log.write(f"\n\n[{datetime.now()} | Level: {level.title()} | Lang: {reply_lang}]\n")
        log.write(f"You: {user_input}\nEcoFriend: {final_response}\n")

# === Display Chat ===
for msg in st.session_state.history:
    avatar_icon = "🌿" if msg["role"] == "assistant" else None  # 🌿 for assistant, none for user
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])