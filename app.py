


import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import json
import re

# ---------------------------
# Gemini API Config
# ---------------------------

API_KEY=st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("🤖 AI Study Buddy")

page = st.sidebar.radio(
    "Go to:",
    ["💬 Chat", "🧾 Summarize Notes", "🎯 Quiz Me"]
)

# ---------------------------
# Helper Functions
# ---------------------------

def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())


def extract_json(text):
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    return None


def ask_ai(prompt):
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

def read_pdf(file):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""
    return text



# ---------------------------
# Chat Page
# ---------------------------
if page == "💬 Chat":
    st.title("💬 Chat with Your Study Buddy")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask your questions...")

    if user_input:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ask_ai(
                    f"Answer clearly for students:\n{user_input}"
                )
                st.markdown(response)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )

    if st.button("🗑 Clear Chat"):
        st.session_state.chat_history = []


# ---------------------------
# Summarize Page
# ---------------------------
elif page == "🧾 Summarize Notes":
    st.title("🧾 Summarize Notes")

    uploaded_file = st.file_uploader(
        "Upload notes (PDF or TXT)",
        type=["pdf", "txt"]
    )

    notes = ""

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            notes = read_pdf(uploaded_file)
        else:
            notes = uploaded_file.read().decode("utf-8")

        st.text_area("Extracted Text", notes, height=200)

    manual_notes = st.text_area("Or paste notes manually:", height=200)

    final_notes = manual_notes if manual_notes.strip() else notes

    if st.button("Generate Summary"):
        if final_notes.strip():
            with st.spinner("Summarizing..."):
                summary = ask_ai(
                    f"Summarize clearly with bullet points:\n{final_notes}"
                )
                st.markdown(summary)
        else:
            st.warning("Upload or paste notes first.")



# ---------------------------
# Quiz Page
# ---------------------------
elif page == "🎯 Quiz Me":
    st.title("🎯 Quiz Generator")

    topic = st.text_input("Enter topic for quiz")

    if st.button("Generate Quiz"):
        if topic:
            prompt = f"""
Create 5 multiple choice questions about {topic}.
Return JSON format:
[
  {{
    "question": "Question text",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "answer": "A"
  }}
]
"""

            with st.spinner("Generating quiz..."):
                response = ask_ai(prompt)
                quiz_data = extract_json(response)

                if quiz_data:
                    st.session_state.quiz = quiz_data
                    st.session_state.answers = [""] * len(quiz_data)
                else:
                    st.error("Quiz generation failed.")

    if "quiz" in st.session_state:
        st.subheader("Answer Questions")

        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            
            ans = st.radio(
                "Choose:",
                q["options"],
                index=None,   # no default selection
                key=i
        )

            st.session_state.answers[i] = ans[0] if ans else ""

        if st.button("Submit Quiz"):
            correct = [q["answer"] for q in st.session_state.quiz]

            score = sum(
                a == c
                for a, c in zip(st.session_state.answers, correct)
            )

            st.success(f"Score: {score}/{len(correct)}")

            for i, (a, c) in enumerate(zip(st.session_state.answers, correct)):
                if a == c:
                    st.write(f"Q{i+1}: ✅ Correct")
                else:
                    st.write(f"Q{i+1}: ❌ Correct answer: {c}")



