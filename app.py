import streamlit as st
import io
import sys
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate
)

# Custom CSS styling
st.markdown("""
<style>
    .main { background-color: #ffffff; color: #000000; }
    .sidebar .sidebar-content { background-color: #f5f5f5; }
    .stTextInput textarea { color: #333333 !important; }
</style>
""", unsafe_allow_html=True)

st.title("DeepSeek Code Assistant and Executor")
st.caption("🚀 Your AI Pair Programmer with Executing Superpowers")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")
    mode = st.radio("Select Mode", ["Code Assistant", "Execute Python Code"])
    selected_model = st.selectbox("Choose Model", ["deepseek-r1:1.5b", "Use Your Own Model"], index=0)
    st.divider()
    st.markdown("### Model Capabilities")
    st.markdown("""
    - 🐍 Python Expert
    - ⚡ Code Executor
    """)

# Initialize AI engine
llm_engine = ChatOllama(
    model=selected_model, base_url="http://localhost:11434", temperature=0.3
)

# System Prompt
system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an expert AI coding assistant. Provide concise, correct solutions."
)

# Manage session state
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hi! I'm DeepSeek. How can I help you code today? 💻"}]

# 🧠 **Code Assistant Mode**
if mode == "Code Assistant":
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.message_log:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    user_query = st.chat_input("Type your coding question here...")
    
    if user_query:
        st.session_state.message_log.append({"role": "user", "content": user_query})

        with st.spinner("🧠 Processing..."):
            # Build chat history
            prompt_messages = [system_prompt]
            for msg in st.session_state.message_log:
                if msg["role"] == "user":
                    prompt_messages.append(HumanMessagePromptTemplate.from_template(msg["content"]))
                elif msg["role"] == "ai":
                    prompt_messages.append(AIMessagePromptTemplate.from_template(msg["content"]))

            # Create chat prompt
            prompt_chain = ChatPromptTemplate.from_messages(prompt_messages)

            try:
                # 🔥 Fix: Ensure `ai_response` is always defined
                ai_response = None  

                # Generate response
                ai_response = (prompt_chain | llm_engine | StrOutputParser()).invoke({})
                
            except KeyError as e:
                # 🛠 Fix: Handle missing variables safely
                st.error(f"⚠️ Error: Missing input variable '{{e}}'. Please check your prompt formatting.")
                ai_response = "⚠️ An error occurred while processing your request."

            # Append AI response and refresh UI
            if ai_response:
                st.session_state.message_log.append({"role": "ai", "content": ai_response})
                st.rerun()

# ⚡ **Execute Python Code Mode**
elif mode == "Execute Python Code":
    st.subheader("⚡ Python Code Executor")
    user_code = st.text_area("Enter your Python code:")

    def execute_code(code):
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        try:
            exec(code, {})
            result = output_buffer.getvalue()
        except Exception as e:
            result = f"⚠️ Error: {str(e)}"
        sys.stdout = sys.__stdout__
        return result
    
    if st.button("Run Code"):
        with st.spinner("🚀 Executing..."):
            execution_output = execute_code(user_code)
        st.code(execution_output, language="python")
