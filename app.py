import os
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv
import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Page Configuration
st.set_page_config(
    page_title="AI Plant Doctor Pro",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern UI/UX
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    .stDownloadButton>button {
        border-radius: 8px;
        font-weight: 600;
        background-color: #2e7d32;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Initialize Session State for History
if "history" not in st.session_state:
    st.session_state.history = []

# Load Environment Variables / Streamlit Secrets
load_dotenv()
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

# 3. Sidebar Configuration
st.sidebar.image("https://img.icons8.com/color/96/potted-plant.png", width=70)
st.sidebar.title("Control Panel")

language_choice = st.sidebar.selectbox(
    "Response Language",
    ["Both (English & Urdu)", "English Only", "Urdu Only"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🌱 Pro Tips")
st.sidebar.info(
    "• Upload a clear, well-lit photo for best results.\n\n"
    "• اچھے نتائج کے لیے پتے کی صاف اور واضح تصویر اپ لوڈ کریں۔"
)

# Feature 3: Plant Care Reminders / Watering Schedule Calculator in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("💧 Watering Calculator")
plant_type_input = st.sidebar.text_input("Plant Name", "e.g. Money Plant / Rose")
environment_type = st.sidebar.selectbox("Environment", ["Indoor (AC/Room)", "Outdoor (Sunny)", "Balcony (Indirect Light)"])

if st.sidebar.button("Get Schedule"):
    if environment_type == "Indoor (AC/Room)":
        st.sidebar.success(f"📌 **{plant_type_input}**: Water every 7-10 days when topsoil is dry.")
    elif environment_type == "Outdoor (Sunny)":
        st.sidebar.success(f"📌 **{plant_type_input}**: Water daily or every 2 days due to sun exposure.")
    else:
        st.sidebar.success(f"📌 **{plant_type_input}**: Water every 4-5 days.")

# Feature 1: Sidebar History Section
st.sidebar.markdown("---")
st.sidebar.subheader("📜 Past Diagnoses")
if st.session_state.history:
    for idx, item in enumerate(st.session_state.history):
        if st.sidebar.button(f"{item['plant']} ({item['time']})", key=f"hist_{idx}"):
            st.session_state.selected_history = item
else:
st.sidebar.caption("No history yet.")

# Main Application Header
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🌿 AI Plant Doctor & Identifier Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6c757d;'>Advanced Botanical Intelligence for Plant Health & Disease Diagnosis</p>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top: 0px;'>", unsafe_allow_html=True)

# Feature 2: Function to generate PDF Report
def generate_pdf(report_text, plant_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=12
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#333333')
    )
    
    story = []
    story.append(Paragraph(f"<b>Botanical Medical Report: {plant_name}</b>", title_style))
    story.append(Spacer(1, 10))
    
    for line in report_text.split('\n'):
        if line.strip():
            story.append(Paragraph(line, body_style))
            story.append(Spacer(1, 4))
            
    doc.build(story)
    buffer.seek(0)
    return buffer

# Main Interface Layout
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📷 Upload Plant Image")
    uploaded_file = st.file_uploader("Choose a plant image (JPG, PNG)...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Plant", use_container_width=True)

with col2:
    st.markdown("### 📋 Botanical Medical Report")
    
    if uploaded_file is not None:
        if st.button("🔍 Analyze Plant Health", type="primary", use_container_width=True):
            if not GEMINI_API_KEY:
                st.error("⚠️ API Key missing! Please configure Streamlit Secrets.")
            else:
                with st.spinner("Analyzing botanical health and diagnosing diseases..."):
                    try:
                        client = genai.Client(api_key=GEMINI_API_KEY)
                        
                        prompt = f"""
                        You are an expert plant pathologist and botanist. Analyze this plant image and provide:
                        1. Plant Name (Common and Scientific)
                        2. Health Status (Healthy or Diseased)
                        3. Disease/Issue Identification (if any)
                        4. Detailed Causes
                        5. Step-by-Step Cure & Treatment Plan with specific medicine/fungicide recommendations if needed
                        6. Preventive Care Guidelines & Watering Schedule
                        
                        Response Language Requirement: {language_choice}
                        """
                        
                        response = client.models.generate_content(
                            model='gemini-3.6-flash',
                            contents=[image, prompt]
                        )
                        
                        report_output = response.text
                        st.success("Diagnosis Completed Successfully!")
                        st.markdown(report_output)
                        
                        # Save to history session state
                        current_time = datetime.datetime.now().strftime("%H:%M")
                        st.session_state.history.append({
                            "plant": "Plant Scan",
                            "time": current_time,
                            "report": report_output
                        })
                        
                        # PDF Download Button
                        pdf_file = generate_pdf(report_output, "Plant Analysis")
                        st.download_button(
                            label="📥 Download Professional PDF Report",
                            data=pdf_file,
                            file_name="plant_medical_report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
    else:
        st.info("👈 Tasveer upload karein aur **Analyze Plant Health** dabayein.")
        
        # Display selected history item if clicked
        if "selected_history" in st.session_state:
            st.markdown("### 📜 Selected Past Report")
            st.markdown(st.session_state.selected_history["report"])
