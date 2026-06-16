import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

from rag import load_and_index, search_document
from search import web_search

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

genai.configure(api_key = GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

SYSTEM_PROMPT = """
You are ChefGenie, an expert cooking assistant.
You help users with:
- Recipes and cooking techniques
- Ingredient substitutions
- Meal planning
- Nutrition advice related to food
- Cooking tips and tricks

Always respond in a warm, friendly and encouraging tone.
If the context is provided, use it to answer accurately.
If the question is not related to cooking or food, politely
say you can only help with cooking related topics.
"""

st.set_page_config(
    page_title="👨‍🍳 ChefGenie",
    page_icon="👨‍🍳",
    layout="centered",

)

st.markdown("""
<style>

/* ========================================
   MAIN APP BACKGROUND
======================================== */
.stApp {
    background: linear-gradient(
        135deg,
        #0B1120 0%,
        #111827 50%,
        #1F2937 100%
    );
    color: #F8FAFC;
}

/* ========================================
   SIDEBAR
======================================== */
section[data-testid="stSidebar"] {
    background: rgba(17, 24, 39, 0.85);
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Sidebar Text */
section[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
}

/* ========================================
   HEADINGS
======================================== */
h1 {
    color: #10B981 !important;
    font-weight: 800 !important;
    text-align: center;
}

h2, h3 {
    color: #F59E0B !important;
}

/* ========================================
   GENERAL TEXT
======================================== */
.stMarkdown,
p,
span,
label,
div {
    color: #F8FAFC;
}

/* ========================================
   CHAT MESSAGES (GLASS EFFECT)
======================================== */
.stChatMessage {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(12px);

    border: 1px solid rgba(255,255,255,0.08);

    border-radius: 18px;
    padding: 14px;
    margin-bottom: 12px;

    box-shadow:
        0 8px 32px rgba(0,0,0,0.25);
}

/* ========================================
   CHAT INPUT
======================================== */
.stChatInputContainer {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);

    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* ========================================
   FILE UPLOADER
======================================== */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.05);

    border: 2px dashed #10B981;

    border-radius: 16px;

    padding: 15px;

    backdrop-filter: blur(10px);
}

/* ========================================
   BUTTONS
======================================== */
.stButton > button {

    background: linear-gradient(
        90deg,
        #10B981,
        #059669
    );

    color: white !important;

    border: none;

    border-radius: 12px;

    font-weight: 600;

    transition: all 0.3s ease;
}

.stButton > button:hover {

    transform: translateY(-2px);

    box-shadow:
        0 0 20px rgba(16,185,129,0.4);
}

/* ========================================
   TEXT INPUTS
======================================== */
.stTextInput input {

    background: rgba(255,255,255,0.05);

    color: white;

    border: 1px solid rgba(255,255,255,0.1);

    border-radius: 12px;
}

/* ========================================
   SCROLLBAR
======================================== */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #111827;
}

::-webkit-scrollbar-thumb {
    background: #10B981;
    border-radius: 10px;
}

/* ========================================
   HERO CARD
======================================== */
.hero-card {

    background: rgba(255,255,255,0.05);

    backdrop-filter: blur(15px);

    border: 1px solid rgba(255,255,255,0.08);

    border-radius: 24px;

    padding: 30px;

    text-align: center;

    margin-bottom: 20px;

    box-shadow:
        0 8px 32px rgba(0,0,0,0.25);
}

</style>
""", unsafe_allow_html=True)

st.markdown("""


# 👨‍🍳 ChefGenie

### Your AI Cooking Assistant

Upload recipes, discover new dishes,
get ingredient substitutions, meal plans,
and instant cooking help.


""")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.button("🍝 Dinner Ideas")

with col2:
    st.button("🥗 Healthy Recipes")

with col3:
    st.button("🍰 Desserts")

with col4:
    st.button("🍛 Indian Dishes")

st.caption("Your Wish is My Dish! — Upload recipes or just ask!")


with st.sidebar:
    st.header("📂 Upload Your Recipe File")
    st.caption("Supported formats: .txt & .pdf")

    uploaded_file = st.file_uploader(
        "Upload a recipe book or cooking notes",
        type=["txt", "pdf"]
    )

    if uploaded_file:
        with st.spinner("Reading and indexing your file..."):
            try:
                st.session_state.vector_store = load_and_index(uploaded_file, GEMINI_API_KEY)
                st.success(f"✅ '{uploaded_file.name}' indexed successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.divider()
    st.markdown("**How it works:**")
    st.markdown("1. 📄 Searches your uploaded file first")
    st.markdown("2. 🤖 Tries Gemini AI if doc has no answer")
    st.markdown("3. 🌐 Falls back to Web Search if needed")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

for messages in st.session_state.messages:
    with st.chat_message(messages["role"]):
            st.markdown(messages["content"])

user_input = st.chat_input("Ask me anything about cooking... 🍽️")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    source_used = ""
    context = ""

    history = ""
    for message in st.session_state.messages[:-1]:
        role = "User" if message["role"] == "user" else "Assistant"
        history += f"{role}: {message['content']}\n"

    if st.session_state.vector_store:
        doc_content, is_relevent = search_document(
            st.session_state.vector_store, user_input
        )
        if is_relevent:
            context = doc_content
            source_used = "📄 Answered from your uploaded file"
    if not context:
        llm_response = model.generate_content(user_input)
        llm_text = llm_response.text
        check = model.generate_content(f"""
Question: '{user_input}'
Response: '{llm_text}'
Classify the response as Relevant or Not Relevant.
We want concrete answers to be classified as Relevant only.
Reply with only one word: Relevant or Not Relevant
""")
        classification = check.text.strip()

        if "Relevant" in classification:
            context = llm_text
            source_used = "🤖 Answered by Gemini AI"
        else:
            web_result = web_search(user_input, SERP_API_KEY)
            context = web_result
            source_used = "🌐 Answered by Web Search"
    
    final_prompt = f"""
{SYSTEM_PROMPT}

Chat History:
{history}

Context:
{context}

User Question: {user_input}

Answer as ChefGenie using the context above.
"""

    final_response = model.generate_content(final_prompt)
    answer = final_response.text
    with st.chat_message("assistant"):
        st.markdown(answer)
        st.caption(source_used)

    st.session_state.messages.append({"role": "assistant", "content": answer})