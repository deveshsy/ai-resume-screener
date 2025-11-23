# AlignAI 💼
> **AI-Powered Resume Tailoring & Gap Analysis System**
>
> *Built by Devesh Singh Yadav*

AlignAI goes beyond simple keyword stuffing. It is an intelligent, agentic workflow designed to help job seekers understand why their resume might be getting rejected by ATS (Applicant Tracking Systems) and provides a factually accurate way to tailor it.

By keeping the "human-in-the-loop," AlignAI ensures that optimized resume content is based on your actual experience, not AI hallucinations.


## ✨ Key Features

* **🤖 Phase 1: Strict ATS "Critic" Agent:** Analyzes your resume against a job description using a low-temperature LLM to provide a realistic match score and identify hard-to-find semantic keyword gaps.
* **🛠️ Phase 2: "Resume Strategist" Agent:** An optimization agent that doesn't just invent content. It takes the missing keywords you select, combines them with context/proof you provide, and rewrites specific resume sections (Profile, Skills, Bullet Points).
* **✅ Human-in-the-Loop Verification:** Crucially, you select which missing skills you actually possess and provide the proof. The AI uses *only* this information to ensure the output is truthful.
* **📄 PDF & TXT Support:** Handles common resume formats using PyPDF2.
* **🎨 Theme-Adaptive UI:** A custom-styled Streamlit interface featuring sticky headers and card-based layouts that automatically adjusts to light or dark mode settings.



## 🚀 How It Works: The Agentic Workflow

AlignAI follows a linear process designed to mimic working with a professional resume writer.

### 

**Phase 1: The Gap Analysis**
1.  Upload your current resume (PDF or TXT).
2.  Paste the target Job Description (JD).
3.  The "Critic" agent analyzes both documents to find semantic gaps, returning a match score and a list of missing keywords.

**Phase 2: The Optimization**
1.  Review the "Missing Keywords" list.
2.  **Crucial Step:** Select the skills you genuinely possess from the list.
3.  **Add Context:** Provide a brief sentence explaining *how* you used those skills (e.g., "I used Python at Company X to automate daily reporting").
4.  The "Strategist" agent uses your context to generate professional, targeted rewrites for your Profile, Skills section, and specific bullet points.
5.  Copy the optimized snippets directly into your resume editor.



## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Custom CSS styling for adaptive theme)
* **AI/LLM:** OpenAI API (GPT-4o-mini model for speed and efficiency)
* **Data Processing:** PyPDF2 (PDF extraction), standard JSON libraries for structured output handling.
* **Environment:** Python 3.9+, python-dotenv



## 💻 Local Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/alignai.git](https://github.com/yourusername/alignai.git)
    cd alignai
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows use: venv\Scripts\activate
    # On macOS/Linux use: source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY=your_api_key_here
    ```

5.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
