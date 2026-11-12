import streamlit as st
import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

# PAGE CONFIGURATION
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="wide"
)

# --------------------------------------------------
# MINT GREEN THEME - BLACK TEXT EVERYWHERE
# --------------------------------------------------

st.markdown("""
<style>

/* Main application background and default text */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #E8F5E9 !important;
    color: #111111 !important;
}

/* Force all normal text to black */
.stApp,
.stApp p,
.stApp span,
.stApp label,
.stApp div,
.stApp li,
.stApp strong,
.stApp b,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp h5,
.stApp h6,
.stMarkdown,
[data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"],
[data-testid="stCaptionContainer"] {
    color: #111111 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #C8E6C9 !important;
    border-right: 1px solid #81C784 !important;
}

[data-testid="stSidebar"] * {
    color: #111111 !important;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    color: #111111 !important;
    font-weight: 700 !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    background: #81C784 !important;
    color: #111111 !important;
    border: 1px solid #66BB6A !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}

.stButton > button *,
.stFormSubmitButton > button * {
    color: #111111 !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #66BB6A !important;
    color: #111111 !important;
    border: 1px solid #388E3C !important;
}

/* Text input fields */
.stTextInput input,
.stTextArea textarea,
input,
textarea {
    background: #F7FFF7 !important;
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    border: 1px solid #81C784 !important;
    border-radius: 10px !important;
    caret-color: #111111 !important;
}

/* Input placeholders */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
input::placeholder,
textarea::placeholder {
    color: #555555 !important;
    -webkit-text-fill-color: #555555 !important;
    opacity: 1 !important;
}

/* Select boxes and dropdowns */
[data-baseweb="select"],
[data-baseweb="select"] *,
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="menu"] * {
    background-color: #F7FFF7 !important;
    color: #111111 !important;
}

/* Slider */
[data-testid="stSlider"] * {
    color: #111111 !important;
}

/* Radio buttons and quiz options */
.stRadio,
.stRadio *,
[data-testid="stRadio"],
[data-testid="stRadio"] *,
[role="radiogroup"],
[role="radiogroup"] *,
[role="radio"] {
    color: #111111 !important;
}

/* Radio button accent */
.stRadio input,
[data-testid="stRadio"] input {
    accent-color: #388E3C !important;
}

/* Checkboxes */
.stCheckbox,
.stCheckbox *,
[data-testid="stCheckbox"],
[data-testid="stCheckbox"] * {
    color: #111111 !important;
}

/* PDF uploader - mint green */
[data-testid="stFileUploader"] {
    background: #D5F5D8 !important;
    border: 2px dashed #66BB6A !important;
    border-radius: 15px !important;
    padding: 20px !important;
}

[data-testid="stFileUploader"] * {
    color: #111111 !important;
}

/* Welcome box */
.welcome-box {
    background: linear-gradient(135deg, #B9EBC0, #A5D6A7, #81C784) !important;
    padding: 55px 30px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 25px;
    border: 1px solid #81C784;
}

.welcome-box h1 {
    color: #111111 !important;
    font-size: 40px;
}

.welcome-box p {
    color: #111111 !important;
    font-size: 18px;
}

/* Feature cards */
.feature-card {
    background: #C8E6C9 !important;
    padding: 25px;
    border-radius: 16px;
    border: 1px solid #81C784;
    min-height: 145px;
    margin-bottom: 12px;
}

.feature-card h3,
.feature-card p {
    color: #111111 !important;
}

/* Expanders */
[data-testid="stExpander"] {
    background: #D5F5D8 !important;
    border: 1px solid #81C784 !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] * {
    color: #111111 !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #C8E6C9 !important;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #81C784;
}

[data-testid="stMetric"] * {
    color: #111111 !important;
}

/* Forms */
[data-testid="stForm"] {
    background: #E8F5E9 !important;
    border: 1px solid #A5D6A7 !important;
    border-radius: 14px !important;
    padding: 15px !important;
}

/* Tabs */
[data-testid="stTabs"] * {
    color: #111111 !important;
}

/* Alerts and messages */
[data-testid="stAlert"] * {
    color: #111111 !important;
}

/* Progress bar */
[data-testid="stProgress"] > div {
    background: #C8E6C9 !important;
}

[data-testid="stProgress"] [role="progressbar"] {
    background: #66BB6A !important;
}

/* Page spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Footer */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# GROQ API CONFIGURATION
# --------------------------------------------------

load_dotenv()

# Works locally with .env and on Streamlit Cloud with Secrets
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        api_key = None

if not api_key:
    st.error("GROQ_API_KEY not found. Please configure it in your .env file or Streamlit Cloud Secrets.")
    st.stop()

client = Groq(api_key=api_key)
MODEL = "openai/gpt-oss-20b"


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "pdf_text": "",
    "quiz_data": None,
    "quiz_answers": {},
    "quiz_submitted": False,
    "page": "Home",
    "show_features": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def go_to_page(page):
    st.session_state.page = page
    st.session_state.show_features = True


# --------------------------------------------------
# AI RESPONSE
# --------------------------------------------------

def generate_ai_response(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI Study Assistant. "
                        "Explain everything in simple English with headings, "
                        "bullet points and examples."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_completion_tokens=3000
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Something went wrong: {str(e)}"


# --------------------------------------------------
# QUIZ GENERATION
# --------------------------------------------------

def generate_quiz(notes, number):
    prompt = f"""
Create exactly {number} MCQs from these notes.

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "question": "Question",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "answer": "A",
      "explanation": "Explanation"
    }}
  ]
}}

Generate exactly {number} questions.
Use four options per question.
The answer must be A, B, C or D.
Return valid JSON only.

NOTES:
{notes[:12000]}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Generate accurate educational MCQs. Return valid JSON only."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_completion_tokens=6000
        )

        content = response.choices[0].message.content.strip()
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            raise ValueError("AI did not return valid JSON.")

        questions = json.loads(match.group(0))["questions"]

        if len(questions) != number:
            raise ValueError("Incorrect number of questions.")

        for q in questions:
            if not all(
                k in q for k in ["question", "options", "answer", "explanation"]
            ):
                raise ValueError("A question is missing information.")

            if q["answer"] not in ["A", "B", "C", "D"]:
                raise ValueError("Invalid answer.")

            if not all(k in q["options"] for k in ["A", "B", "C", "D"]):
                raise ValueError("Missing options.")

        return questions

    except Exception as e:
        st.error(f"Quiz generation failed: {str(e)}")
        return None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.markdown("# 📚 AI Study Assistant")
st.sidebar.caption("Your personal learning companion")
st.sidebar.markdown("---")

if st.sidebar.button("🏠 Home", use_container_width=True):
    st.session_state.page = "Home"
    st.session_state.show_features = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Available Features")

for feature in [
    "Summarize Notes",
    "Explain a Topic",
    "Generate Questions",
    "Practice Quiz"
]:
    if st.sidebar.button(feature, use_container_width=True):
        go_to_page(feature)
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("✨ Powered by Groq AI")


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

if st.session_state.page == "Home":

    st.markdown("""
    <div class="welcome-box">
        <h1>Welcome to AI Study Assistant 👋</h1>
        <p>
        Your personal AI learning companion.
        Learn smarter, understand better and prepare confidently.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<h3 style='text-align:center; color:#111111;'>"
        "Explore Your Learning Space</h3>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("🏠 HOME", use_container_width=True):
            st.session_state.show_features = True
            st.rerun()

    if st.session_state.show_features:

        st.markdown("---")
        st.subheader("✨ Choose Your Feature")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="feature-card">
                <h3>📄 Summarize Notes</h3>
                <p>Upload PDF notes and get simple AI summaries.</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Open Summarizer", use_container_width=True):
                go_to_page("Summarize Notes")
                st.rerun()

        with col2:
            st.markdown("""
            <div class="feature-card">
                <h3>💡 Explain a Topic</h3>
                <p>Understand difficult topics with easy explanations.</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Open Topic Explainer", use_container_width=True):
                go_to_page("Explain a Topic")
                st.rerun()

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("""
            <div class="feature-card">
                <h3>📝 Generate Questions</h3>
                <p>Create MCQs and descriptive questions from notes.</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Open Question Generator", use_container_width=True):
                go_to_page("Generate Questions")
                st.rerun()

        with col4:
            st.markdown("""
            <div class="feature-card">
                <h3>🎯 Practice Quiz</h3>
                <p>Take quizzes and check your performance.</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Open Practice Quiz", use_container_width=True):
                go_to_page("Practice Quiz")
                st.rerun()

    else:
        st.markdown(
            "<p style='text-align:center; color:#111111;'>"
            "Click the Home button above to explore all available features."
            "</p>",
            unsafe_allow_html=True
        )


# --------------------------------------------------
# SUMMARIZE NOTES
# --------------------------------------------------

elif st.session_state.page == "Summarize Notes":

    st.title("📄 Summarize Your Notes")
    st.write("Upload your PDF and generate an AI-powered summary.")

    uploaded_file = st.file_uploader(
        "Upload your PDF file",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.button("Extract PDF Text"):

            try:
                reader = PdfReader(uploaded_file)
                extracted_text = ""

                for pdf_page in reader.pages:
                    extracted_text += pdf_page.extract_text() or ""

                if extracted_text.strip():
                    st.session_state.pdf_text = extracted_text
                    st.success("PDF text extracted successfully!")
                else:
                    st.warning("No readable text found in this PDF.")

            except Exception as e:
                st.error(f"PDF extraction failed: {str(e)}")

    if st.session_state.pdf_text:

        st.success("Your study notes are ready!")

        with st.expander("View Extracted PDF Text"):
            st.text_area(
                "Extracted Text",
                st.session_state.pdf_text,
                height=250
            )

        if st.button("Generate AI Summary"):

            with st.spinner("AI is preparing your summary..."):

                summary = generate_ai_response(
                    f"""
Summarize these notes in simple English.
Include main topics, definitions, key points,
examples and revision points.

NOTES:
{st.session_state.pdf_text[:12000]}
"""
                )

            st.subheader("✨ AI Generated Summary")
            st.markdown(summary)


# --------------------------------------------------
# EXPLAIN A TOPIC
# --------------------------------------------------

elif st.session_state.page == "Explain a Topic":

    st.title("💡 Explain a Topic")
    st.write("Understand difficult topics with easy explanations.")

    topic = st.text_input(
        "Enter your topic",
        placeholder="Example: Machine Learning"
    )

    if st.button("Explain Topic"):

        if topic.strip():

            with st.spinner("AI is preparing your explanation..."):

                explanation = generate_ai_response(
                    f"""
Explain {topic} in simple English.
Include definition, how it works, important points,
real-life example, advantages and conclusion.
"""
                )

            st.subheader("✨ AI Explanation")
            st.markdown(explanation)

        else:
            st.warning("Please enter a topic first.")


# --------------------------------------------------
# GENERATE QUESTIONS
# --------------------------------------------------

elif st.session_state.page == "Generate Questions":

    st.title("📝 Generate Questions")

    if not st.session_state.pdf_text:

        st.warning("Please upload and extract a PDF first.")

    else:

        question_type = st.selectbox(
            "Select Question Type",
            [
                "Multiple Choice Questions (MCQ)",
                "Short Answer Questions",
                "Long Answer Questions"
            ]
        )

        number = st.slider(
            "Number of Questions",
            5,
            20,
            5
        )

        if st.button("Generate Questions"):

            prompt = f"""
Generate {number} {question_type} from these notes.
Number each question and provide answers.
Use simple English.

NOTES:
{st.session_state.pdf_text[:12000]}
"""

            with st.spinner("Generating questions..."):
                questions = generate_ai_response(prompt)

            st.subheader("✨ Generated Questions")
            st.markdown(questions)


# --------------------------------------------------
# PRACTICE QUIZ
# --------------------------------------------------

elif st.session_state.page == "Practice Quiz":

    st.title("🎯 Practice Quiz")

    if not st.session_state.pdf_text:

        st.warning("Please upload and extract a PDF first.")

    else:

        if st.session_state.quiz_data is None:

            number = st.slider(
                "Choose Number of Questions",
                3,
                10,
                5
            )

            if st.button("Generate Practice Quiz"):

                with st.spinner("Preparing your quiz..."):

                    quiz = generate_quiz(
                        st.session_state.pdf_text,
                        number
                    )

                if quiz:
                    st.session_state.quiz_data = quiz
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.rerun()

        else:

            questions = st.session_state.quiz_data

            st.subheader(f"You have {len(questions)} questions")

            if not st.session_state.quiz_submitted:

                with st.form("quiz_form"):

                    selected_answers = {}

                    for i, question in enumerate(questions):

                        st.markdown(
                            f"**Question {i + 1}: {question['question']}**"
                        )

                        options = question["options"]

                        answer = st.radio(
                            f"Choose your answer for Question {i + 1}",
                            options=["A", "B", "C", "D"],
                            format_func=lambda option, opts=options:
                                f"{option}. {opts[option]}",
                            key=f"question_{i}",
                            index=None
                        )

                        selected_answers[i] = answer

                        st.markdown("---")

                    submitted = st.form_submit_button(
                        "Submit My Answers"
                    )

                    if submitted:

                        st.session_state.quiz_answers = selected_answers
                        st.session_state.quiz_submitted = True
                        st.rerun()

            else:

                score = sum(
                    1 for i, question in enumerate(questions)
                    if st.session_state.quiz_answers.get(i) == question["answer"]
                )

                percentage = score / len(questions) * 100

                st.subheader("🏆 Your Quiz Results")

                col1, col2, col3 = st.columns(3)

                col1.metric("Total Questions", len(questions))
                col2.metric("Correct Answers", score)
                col3.metric("Your Score", f"{percentage:.1f}%")

                st.progress(percentage / 100)

                if percentage >= 80:
                    st.success("Excellent work! Great understanding!")

                elif percentage >= 50:
                    st.info("Good effort! Keep practicing.")

                else:
                    st.warning("Keep learning and try again!")

                st.markdown("---")
                st.subheader("📋 Answer Review")

                for i, question in enumerate(questions):

                    user_answer = st.session_state.quiz_answers.get(i)
                    correct_answer = question["answer"]

                    st.markdown(
                        f"**Question {i + 1}: {question['question']}**"
                    )

                    if user_answer == correct_answer:

                        st.success(
                            f"Correct! Your answer: {user_answer}"
                        )

                    else:

                        st.error(
                            f"Your answer: {user_answer or 'Not answered'} | "
                            f"Correct answer: {correct_answer}"
                        )

                    st.write(
                        f"**Explanation:** {question['explanation']}"
                    )

                    st.markdown("---")

                if st.button("Try Another Quiz"):

                    st.session_state.quiz_data = None
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.rerun()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.markdown(
    "<center style='color:#111111;'>"
    "📚 AI Study Assistant | Powered by Groq AI"
    "</center>",
    unsafe_allow_html=True
)