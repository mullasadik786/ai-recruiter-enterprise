# 🎯 AI Recruiter Enterprise Pro - Intelligent Talent Pipeline

AI Recruiter Enterprise Pro is a robust, production-hardened Proof of Concept (PoC) candidate screening and ranking system. Powered by frontier LLM (OpenAI GPT-4o) analytics, this application transforms unstructured resume data into an expertly ranked shortlist while managing communications seamlessly.

---

## 🚀 Core Features

1. **Intelligent Semantic Ranking:** Moves beyond keyword filtering to understand candidate context, project complexity, and semantic fit.
2. **Mass Bulk PDF Ingestion:** Upload multiple candidate resumes simultaneously to parse text payloads asynchronously.
3. **Dynamic Weightage Sliders:** Recruiters can shift weight parameters dynamically on the UI to adjust core focus (e.g., higher weight on communication for sales, or higher weight on technical skill for engineering).
4. **Automated Contact Extraction:** Automatically identifies and harvests candidate names, phone numbers, and emails without relying on brittle regex patterns.
5. **Live PDF Preview Window:** View candidate resumes natively side-by-side right next to the rank leaderboard.
6. **Multi-Channel Email Gateway:** Seamlessly toggle between Gmail SMTP relays and high-volume SendGrid APIs.
7. **Automated Calendar/Meeting Provisioning:** Generates dynamic, secure virtual rooms (Google Meet format) embedded inside responsive corporate HTML emails.
8. **24h Automated Follow-up Reminder:** One-click automated urgency notifications for candidates who haven't confirmed yet.
9. **Permanent Local Database Layer:** Fully integrated with an SQLite persistent backend to store candidate profiles, history, and communication logs safely.

---

## 🛠️ Step-by-Step Installation & Setup

Follow these commands to deploy and test the project in your local development environment.

### Step 1: Clone or Set up the Project Files
Ensure your project folder contains the following core files:
- `app.py` (The main engine script)
- `requirements.txt` (System dependencies)
- `README.md` (Documentation)

### Step 2: Install System Software Dependencies
Open your terminal (Command Prompt, Git Bash, or macOS Terminal) inside the project folder and run:
```bash
pip install -r requirements.txt
```

### Step 3: Establish OpenAI API Environment Variables (Recommended)
Inject your OpenAI secret token into your active environment session:
- **Windows (Command Prompt):** `set OPENAI_API_KEY="your-secret-api-key-here"`
- **Linux / macOS Terminal:** `export OPENAI_API_KEY="your-secret-api-key-here"`
*(Note: You can also type this API key manually inside the dashboard sidebar interface).*

### Step 4: Run the Dashboard Framework Server
Execute the hosting runtime stream using this command:
```bash
streamlit run app.py
```
The framework listener will automatically map and launch the live web application in your default browser at: **`http://localhost:8501`**

---

## 📧 Secure Email Infrastructure Setup

### Gateway Choice A: Gmail SMTP Bridge (Development/Testing)
1. Go to your [Google Account Settings](https://google.com).
2. Navigate to **Security** and ensure **2-Step Verification** is enabled.
3. Search for **"App Passwords"** inside the settings lookup index box.
4. Input a custom application name (e.g., `AI Recruiting System`), click **Create**, and copy the unique **16-digit secret key**.
5. Use this 16-digit app password in the sidebar configuration input panel of the running web application.

### Gateway Choice B: SendGrid API Integration (Enterprise Production)
1. Log into your [SendGrid Dashboard](https://sendgrid.com).
2. Navigate to **Settings** -> **API Keys** -> **Create API Key** with Full Access permissions.
3. Select `SendGrid API Server` from the application dropdown, enter your `SG...` signature token key, and input your validated sender email identity.

---

## 🗄️ Architecture & Data Layer
- **Frontend / Execution Interface:** Streamlit Engine
- **LLM Engine:** OpenAI GPT-4o API Model
- **Data Storage:** Local Persistence SQLite3 File (`ai_recruiter.db`)
- **Document Scraping Module:** PyPDF Pipeline Reader
