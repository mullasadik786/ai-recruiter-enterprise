import streamlit as st
import json
import os
import pandas as pd
import random
import string
import smtplib
import sqlite3
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
from pypdf import PdfReader

# Safe handler to prevent SendGrid import failure from crashing the app
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

# ==============================================================================
# 1. DATABASE SETUP (Streamlit Cloud Safe Mode)
# ==============================================================================
DB_FILE = "/tmp/ai_recruiter.db" if not os.access('.', os.W_OK) else "ai_recruiter.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                candidate_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                phone TEXT,
                final_score REAL,
                comm_score REAL,
                tech_score REAL,
                meet_link TEXT,
                justification TEXT,
                email_status TEXT DEFAULT 'Pending'
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        pass

def save_candidate_to_db(c):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO candidates 
            (candidate_id, name, email, phone, final_score, comm_score, tech_score, meet_link, justification, email_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (c['candidate_id'], c['extracted_name'], c['email'], c['phone'], 
              c['final_weighted_score'], c['communication_score'], c['technical_fit_score'], 
              c['meet_link'], c['justification'], c.get('email_status', 'Pending')))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

init_db()

# ==============================================================================
# 2. APPLICATION VIEWPORT SETUP & SIDEBAR
# ==============================================================================
st.set_page_config(page_title="AI Recruiter Enterprise Pro", page_icon="🚀", layout="wide")

st.title("🎯 AI Recruiter Enterprise Pro - End-to-End Talent Pipeline")
st.caption("Frontier LLM Resume Ingestion ➔ Dynamic Matrix Weighting ➔ Multi-Channel Dispatch Gateway ➔ Virtual Room Provisioning")
st.markdown("---")

st.sidebar.header("⚙️ Core Engine Configuration")

# Input for OpenAI API Key
api_key = os.environ.get("OPENAI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("OpenAI Token Key Space:", type="password", help="Input your sk-... token layer here.")

st.sidebar.subheader("📊 Algorithmic Scoring Weightage")
comm_weight = st.sidebar.slider("💬 Communication Vector Weight (%)", 0, 100, 50)
tech_weight = 100 - comm_weight
st.sidebar.info(f"💻 Automated Technical Competency Alignment: {tech_weight}%")

st.sidebar.subheader("📧 Outbound Communications Pipeline")
email_gateway = st.sidebar.selectbox("Active Protocol Layer:", ["Gmail SMTP Gateway", "SendGrid API Server"])
sender_email = st.sidebar.text_input("Validated Sender Address:", "sriskms786@gmail.com")

if email_gateway == "Gmail SMTP Gateway":
    gateway_password = st.sidebar.text_input("16-Digit App Encryption Password:", type="password")
else:
    gateway_password = st.sidebar.text_input("SendGrid Bearer API Token (SG...):", type="password")

st.sidebar.subheader("🏢 Corporate Layout Identity")
company_name = st.sidebar.text_input("Branding Identity Title:", "TechInno Solutions")

# ==============================================================================
# 3. HELPER UTILITIES
# ==============================================================================
def generate_mock_google_meet():
    p1 = ''.join(random.choices(string.ascii_lowercase, k=3))
    p2 = ''.join(random.choices(string.ascii_lowercase, k=4))
    p3 = ''.join(random.choices(string.ascii_lowercase, k=3))
    return f"https://google.com{p1}-{p2}-{p3}"

def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Inbound Document Parse Error ({pdf_file.name}): {e}")
        return ""

def show_pdf_preview(file):
    try:
        base64_pdf = base64.b64encode(file.getvalue()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"PDF Preview Generation Error: {e}")

def get_html_template(candidate_name, meet_link, comp_name, is_reminder=False):
    title = f"{comp_name} - Urgent Reminder" if is_reminder else f"{comp_name} - Interview Invitation"
    greeting = "This is a gentle reminder that we are waiting for your confirmation." if is_reminder else "We are thrilled to inform you that you have been shortlisted for the interview rounds."
    
    return f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1e293b; background-color: #f8fafc; padding: 30px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);">
            <div style="text-align: center; border-bottom: 4px solid #2563eb; padding-bottom: 20px; margin-bottom: 25px;">
                <h2 style="color: #1e3a8a; margin: 0; font-size: 24px; font-weight: 700;">{title}</h2>
            </div>
            <p>Dear <strong>{candidate_name}</strong>,</p>
            <p>{greeting}</p>
            <p>Please click the secure <strong>Google Meet Link</strong> below to join your allocated assessment panel:</p>
            <div style="text-align: center; margin: 35px 0;">
                <a href="{meet_link}" style="background-color: #2563eb; color: #ffffff; padding: 14px 32px; text-decoration: none; font-weight: bold; border-radius: 6px; display: inline-block;">👉 Access Live Interview Room</a>
            </div>
            {"<p style='color: #ef4444; font-weight: bold;'>⚠️ Note: This link will expire shortly. If you do not click within 24 hours, your application may automatically expire.</p>" if is_reminder else ""}
            <p>Best Regards,<br><strong>HR Team ({comp_name})</strong></p>
        </div>
    </body>
    </html>
    """

def send_enterprise_email(to_email, candidate_name, meet_link, comp_name, is_reminder=False):
    if not gateway_password:
        st.error("⚠️ Authentication Parameter Missing: Provide a valid password/API-key.")
        return False
    
    html_body = get_html_template(candidate_name, meet_link, comp_name, is_reminder)
    subject = f"⚠️ [Reminder] Interview Call - {comp_name}" if is_reminder else f"Interview Invitation - {comp_name}"
    
    if email_gateway == "Gmail SMTP Gateway":
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            server = smtplib.SMTP('://gmail.com', 587)
            server.starttls()
            server.login(sender_email, gateway_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            st.error(f"Gmail Mail Transmission Error: {e}")
            return False
    else:
        if not SENDGRID_AVAILABLE:
            st.error("SendGrid package is not fully initialized in this environment yet. Try Gmail SMTP Gateway.")
            return False
        
        try:
            message = Mail(
                from_email=sender_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_body
            )
            sg = SendGridAPIClient(gateway_password)
            response = sg.send(message)
            # FIX 1: Fixed the broken 'in' syntax error here
            if response.status_code in:
                return True
            else:
                st.error(f"SendGrid returned unhealthy status code: {response.status_code}")
                return False
        except Exception as e:
            st.error(f"SendGrid Mail Transmission Error: {e}")
            return False

# ==============================================================================
# 4. CORE APPLICATION INTERACTIVE VIEWS
# ==============================================================================
# FIX 2: Split tabs properly into separate distinct variables
tab1, tab2 = st.tabs(["📥 Resume Ingestion Engine", "📊 Candidate Calibration Pipeline"])

# ---- TAB 1: RESUME INGESTION ENGINE ----
with tab1:
    st.subheader("Upload Inbound Documents")
    uploaded_files = st.file_uploader("Drop candidate resumes here (PDF only)", type=["pdf"], accept_multiple_files=True)
    
    job_description = st.text_area("Target Job Profile Matrix:", "Looking for a Software Engineer proficient in Python, SQL, Cloud Architectures, with exceptional communication skills.")
    
    if st.button("🚀 Execute Ingestion & Analysis Engine"):
        if not api_key:
            st.warning("Please configure your OpenAI Token Key Space in the sideb
