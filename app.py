import streamlit as st
import PyPDF2
import io
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AlignAI",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    
    /* STICKY HEADER CONFIGURATION */
    .header-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #ffffff;
        padding: 15px 2rem;
        border-bottom: 1px solid #e1e4e8;
        z-index: 9999; /* Ensures it stays on top */
        text-align: left; /* Left align like Gemini */
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* Adjust Streamlit's default top padding so content isn't hidden behind the header */
    .block-container {
        padding-top: 140px !important; 
    }
    
    /* Hide the default Streamlit rainbow decoration bar for a cleaner look */
    header[data-testid="stHeader"] {
        display: none;
    }

    /* TYPOGRAPHY IN HEADER */
    .header-title {
        color: #2e3b4e;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.2;
        letter-spacing: -0.5px;
    }
    .header-sub {
        color: #007bff;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .header-desc {
        color: #6c757d;
        font-size: 0.85rem;
        margin: 2px 0 0 0;
    }
    
    /* STANDARD UI ELEMENTS */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .step-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .step-card-locked {
        background-color: #e9ecef;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #6c757d;
        color: #6c757d;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #ffffff;
        color: #888;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #e1e4e8;
        font-size: 14px;
        z-index: 100;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'job_description' not in st.session_state:
    st.session_state.job_description = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 👨‍💻 About this Project")
    st.info(
        """
        **AlignAI** is an advanced career tool designed to optimize job applications.
        
        * **Built with:** Python, OpenAI GPT-4, and Streamlit.
        * **Gap Analysis:** Identifies keyword gaps between Resume & JD.
        * **Agentic Workflow:** Autonomously rewrites resume points based on your context.
        """
    )
    
    st.markdown("---")
    st.header("⚙️ Settings")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.warning("⚠️ No API Key found.")
        api_key = st.text_input("Enter OpenAI API Key", type="password")
    else:
        st.success("✅ API Key loaded.")

# --- STICKY HEADER SECTION ---
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">AlignAI</h1>
        <p class="header-sub">by Devesh Singh Yadav</p>
        <p class="header-desc">AI-Powered Resume Tailoring & Gap Analysis System</p>
    </div>
""", unsafe_allow_html=True)

# --- WORKFLOW VISUALIZATION ---
st.markdown("#### 🚀 Workflow Roadmap")
step_col1, step_col2 = st.columns(2)
with step_col1:
    st.markdown("""
    <div class="step-card">
        <strong>Step 1: Analyze Match</strong><br>
        Upload Resume & JD to detect semantic gaps.
    </div>
    """, unsafe_allow_html=True)
with step_col2:
    if st.session_state.analysis_result:
        st.markdown("""
        <div class="step-card" style="border-left: 5px solid #28a745;">
            <strong>Step 2: AI Optimization</strong><br>
            Agent unlocked! Ready to rewrite content.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="step-card-locked">
            <strong>Step 2: AI Optimization</strong><br>
            🔒 Locked. Runs after Gap Analysis is complete.
        </div>
        """, unsafe_allow_html=True)

st.write("") # Spacer

# --- HELPER FUNCTIONS ---
def extract_text_from_file(uploaded_file):
    uploaded_file.seek(0)
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or "" + '\n'
        return text
    else:
        return uploaded_file.read().decode("utf-8")

# --- PHASE 1: INPUTS ---
input_container = st.container()
with input_container:
    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        st.subheader("📂 Step 1: Upload Resume")
        uploaded_file = st.file_uploader("Drop your PDF or TXT file here", type=["pdf", "txt"])
    
    with col2:
        st.subheader("📋 Step 2: Job Description")
        jd_input = st.text_area("Paste the JD here", height=150, placeholder="Copy and paste the job description here...")

    st.write("")
    
    if st.button("🔍 Run AlignAI Analysis", type="primary"):
        if not api_key or not uploaded_file or not jd_input:
            st.error("⚠️ Please provide API Key, Resume, and Job Description.")
            st.stop()

        with st.spinner("🤖 Phase 1: Analyzing Semantic Match..."):
            try:
                st.session_state.resume_text = extract_text_from_file(uploaded_file)
                st.session_state.job_description = jd_input

                # Analysis Prompt
                prompt = f"""
                Act as a strict, nitpicky ATS (Applicant Tracking System). 
                Compare the Resume against the Job Description.
                
                You MUST identify missing keywords. Even if the match is good, find skills in the JD that are not explicitly in the Resume.
                
                Return a valid JSON object with exactly these keys:
                {{
                    "match_score": (integer 0-100),
                    "summary": (brief summary),
                    "missing_keywords": (list of specific strings, e.g. ["Python", "Agile", "AWS"])
                }}
                
                RESUME: {st.session_state.resume_text[:15000]}
                JD: {st.session_state.job_description[:5000]}
                """
                
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={ "type": "json_object" },
                    temperature=0.1
                )
                st.session_state.analysis_result = json.loads(response.choices[0].message.content)
                st.rerun()

            except Exception as e:
                st.error(f"Error: {e}")

# --- PHASE 2: RESULTS & OPTIMIZATION ---
if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    
    st.markdown("---")
    st.subheader("📊 Phase 1 Report: Assessment")
    
    col_score, col_summary = st.columns([1, 2])
    
    with col_score:
        score = result.get('match_score', 0)
        st.markdown(f"""
            <div class="metric-card">
                <h2 style="font-size: 3rem; margin:0; color: {'#28a745' if score > 70 else '#ffa500' if score > 50 else '#dc3545'};">{score}%</h2>
                <p style="margin:0;">Match Score</p>
            </div>
        """, unsafe_allow_html=True)
        st.progress(score / 100)
    
    with col_summary:
        st.markdown("**Analysis Summary:**")
        st.info(result.get('summary', 'No summary available.'))
    
    # Missing Keywords
    st.markdown("### ⚠️ Missing Keywords Detected")
    st.caption("The following skills were found in the JD but are missing from your resume context:")
    
    missing = result.get('missing_keywords', [])
    if isinstance(missing, str):
         missing = [x.strip() for x in missing.split(',') if x.strip()]
    
    if missing:
        with st.expander("View Missing Keywords", expanded=True):
            kw_cols = st.columns(3)
            for i, kw in enumerate(missing):
                kw_cols[i % 3].markdown(f"🔴 **{kw}**")
    else:
        st.success("✅ No critical keywords missing!")

    # --- PHASE 2: OPTIMIZATION AGENT ---
    st.markdown("---")
    st.header("🛠️ Phase 2: Optimization Agent")
    
    if not missing:
        st.info("Nothing to optimize! Your resume is well-matched.")
    else:
        st.markdown("Select skills you possess and **add context** so the AI can write true bullets, not fake ones.")
        
        with st.form("optimization_form"):
            col_sel, col_txt = st.columns([1, 1])
            
            with col_sel:
                selected_skills = st.multiselect("1. I possess these skills:", missing)
            
            with col_txt:
                # NEW FEATURE: User context input
                user_context = st.text_area(
                    "2. Add Context/Proof (Crucial):", 
                    placeholder="E.g. I used Python at Company X to build a scraper...",
                    height=100
                )

            generate_btn = st.form_submit_button("✨ Generate Optimized Resume Content")

        if generate_btn and selected_skills:
            with st.spinner("🤖 Phase 2: Agent is rewriting sections..."):
                try:
                    # UPDATED PROMPT with User Context
                    opt_prompt = f"""
                    You are an expert Resume Writer.
                    The user has a resume but failed to mention these specific skills: {selected_skills}.
                    
                    USER CONTEXT/ACHIEVEMENTS (Use this to write the bullets):
                    "{user_context}"
                    
                    TASK:
                    1. Identify the best section in their resume to insert these skills.
                    2. Write specific, professional bullet points using the skills and the user's provided context.
                    
                    OUTPUT FORMAT:
                    Provide 2 options.
                    Option 1: A rewrite of an existing bullet point.
                    Option 2: A new "Skills" or "Summary" line.
                    Use Markdown for bolding the keywords.
                    
                    RESUME: {st.session_state.resume_text[:15000]}
                    """
                    
                    client = OpenAI(api_key=api_key)
                    opt_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": opt_prompt}],
                        temperature=0.4
                    )
                    
                    st.success("✅ Content Generated! Copy these snippets into your resume:")
                    st.markdown("### 📋 Suggested Edits")
                    st.markdown(opt_response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"Optimization Error: {e}")

# --- FOOTER ---
st.markdown("""
    <div class="footer">
        <p>AlignAI by Devesh Singh Yadav | Powered by OpenAI & Streamlit</p>
    </div>
    <div style="margin-bottom: 50px;"></div> 
""", unsafe_allow_html=True)