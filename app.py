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

# --- CUSTOM CSS (STATIC HEADER - SCROLLS AWAY) ---
st.markdown("""
    <style>
    /* --- GLOBAL THEME ADAPTATION --- */
    
    /* STATIC HEADER */
    /* Changed from 'fixed' to standard flow so it scrolls away */
    .header-container {
        width: 100%;
        
        /* Use the Theme's Background Color */
        background-color: var(--background-color);
        
        /* Use the Theme's Text Color */
        color: var(--text-color);
        
        padding: 30px 2rem 20px 2rem;
        border-bottom: 1px solid rgba(150, 150, 150, 0.2);
        
        /* Pull it up to the very top of the page */
        margin-top: -70px; 
        margin-bottom: 20px;
        
        /* CENTER ALIGNMENT */
        display: flex;
        flex-direction: column;
        align-items: center; 
        justify-content: center;
        text-align: center;
    }

    /* HEADER TYPOGRAPHY */
    .header-title {
        color: var(--text-color);
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.2;
    }
    .header-sub {
        color: var(--primary-color);
        font-size: 1rem;
        font-weight: 600;
        margin: 5px 0 0 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .header-desc {
        color: var(--text-color);
        opacity: 0.8;
        font-size: 0.9rem;
        margin: 5px 0 0 0;
    }

    /* PADDING ADJUSTMENT */
    /* Reset padding since header is no longer floating */
    .block-container {
        padding-top: 2rem !important; 
        padding-bottom: 80px !important; 
    }
    
    /* --- SIDEBAR & DEFAULT HEADER --- */
    
    /* Make default header transparent so hamburger button is visible 
       but doesn't block the custom header look */
    header[data-testid="stHeader"] {
        background-color: transparent;
        border: none;
    }
    
    /* Hide the colored top decoration line */
    [data-testid="stDecoration"] {
        display: none;
    }

    /* Ensure Sidebar is on top */
    [data-testid="stSidebar"] {
        z-index: 999999 !important;
    }

    /* --- CARDS & UI --- */
    .metric-card {
        background-color: var(--secondary-background-color);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(150, 150, 150, 0.1);
    }
    .metric-card h2 {
        color: var(--text-color) !important;
    }
    .metric-card p {
        color: var(--text-color) !important;
        opacity: 0.7;
    }
    
    .step-card {
        background-color: var(--secondary-background-color);
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid var(--primary-color);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: var(--text-color);
    }
    
    .step-card-locked {
        background-color: var(--secondary-background-color);
        opacity: 0.5;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid gray;
        color: var(--text-color);
    }
    
    /* STICKY FOOTER */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: var(--background-color);
        color: var(--text-color);
        opacity: 0.6;
        text-align: center;
        padding: 15px;
        border-top: 1px solid rgba(150, 150, 150, 0.2);
        font-size: 14px;
        z-index: 99999;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
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

# --- HEADER (SCROLLS WITH PAGE) ---
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

st.write("") 

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
        score_color = '#28a745' if score > 70 else '#ffa500' if score > 50 else '#dc3545'
        
        st.markdown(f"""
            <div class="metric-card">
                <h2 style="font-size: 3rem; margin:0; color: {score_color} !important;">{score}%</h2>
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
        st.markdown("Select skills you possess and **add context** so the AI can update each section of your resume.")
        
        with st.form("optimization_form"):
            col_sel, col_txt = st.columns([1, 1])
            
            with col_sel:
                selected_skills = st.multiselect("1. I possess these skills:", missing)
            
            with col_txt:
                # User context input
                user_context = st.text_area(
                    "2. Add Context/Proof (Crucial):", 
                    placeholder="E.g. I have experience with Python for 2 years and used it for automation...",
                    height=100
                )

            generate_btn = st.form_submit_button("✨ Generate Optimized Resume Content")

        if generate_btn and selected_skills:
            with st.spinner("🤖 Phase 2: Agent is analyzing and rewriting specific sections..."):
                try:
                    # --- UPDATED PROMPT LOGIC ---
                    opt_prompt = f"""
                    You are an expert Resume Strategist.
                    
                    INPUT DATA:
                    1. USER'S OLD RESUME: {st.session_state.resume_text[:15000]}
                    2. TARGET JOB DESCRIPTION (JD): {st.session_state.job_description[:5000]}
                    3. MISSING KEYWORDS USER ACTUALLY HAS: {selected_skills}
                    4. USER'S ADDED CONTEXT: "{user_context}"

                    YOUR TASK:
                    Rewrite specific sections of the resume to align with the JD, integrating the missing keywords naturally.
                    Do NOT invent false information. Only use the User's Context and the Old Resume.

                    OUTPUT FORMAT (Markdown):
                    
                    ### 1. Optimized Profile / Summary
                    (Rewrite the "About" or "Profile" section to focus on the JD's role. Incorporate the missing skills if they fit here conceptually.)
                    
                    ### 2. Updated Skills Section
                    (Provide a clean list of skills to Copy/Paste. Add the selected missing keywords to the appropriate category. Remove irrelevant legacy skills if the list is too long.)
                    
                    ### 3. Optimized Bullet Points (Experience/Projects)
                    (Identify 2-3 specific bullet points from the resume that can be upgraded. Rewrite them to include the missing keywords and use strong action verbs. Highlight the keywords in **bold**.)
                    
                    STRICT RULES:
                    - Do not mention "Here is the rewritten section". Just give the content.
                    - If the user context is insufficient for a bullet point, do not fake a number.
                    - Keep the tone professional.
                    """
                    
                    client = OpenAI(api_key=api_key)
                    opt_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": opt_prompt}],
                        temperature=0.4
                    )
                    
                    st.success("✅ Content Generated! Copy these sections directly into your resume editor:")
                    st.markdown("---")
                    st.markdown(opt_response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"Optimization Error: {e}")

# --- FOOTER ---
st.markdown("""
    <div class="footer">
        <p>AlignAI by Devesh Singh Yadav | Powered by OpenAI & Streamlit</p>
    </div>
""", unsafe_allow_html=True)