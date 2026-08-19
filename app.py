import os
from dotenv import load_dotenv
from google import genai
from PIL import Image
import streamlit as st

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 1. Page Configuration
st.set_page_config(
    page_title="AI Plant Doctor Pro",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Ultra-Clean & Professional CSS Styling (No unwanted lines)
st.markdown(
    """
    <style>
    /* Clean Soft Background */
    .stApp {
        background-color: #F4F7F6;
    }
    
    /* Title Styling */
    .main-title {
        font-size: 2.6rem;
        color: #1b4332;
        text-align: center;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        color: #40916c;
        font-size: 1.1rem;
        margin-bottom: 30px;
        font-weight: 500;
    }

    /* Clean Card Layout without glitches */
    div.element-container {
        margin-bottom: 10px;
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #2d6a4f, #1b4332);
        color: white;
        font-size: 16px;
        font-weight: 600;
        border-radius: 10px;
        padding: 12px 20px;
        border: none;
        box-shadow: 0 4px 10px rgba(45, 106, 79, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1b4332, #081c15);
        color: #d8f3dc;
        transform: translateY(-2px);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Section
st.markdown(
    "<h1 class='main-title'>🌿 AI Plant Doctor & Identifier Pro</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='sub-title'>Advanced Botanical Intelligence for Plant Health & Disease Diagnosis</p>",
    unsafe_allow_html=True,
)

# Sidebar UI
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/628/628324.png", width=60
)
st.sidebar.title("⚙️ Control Panel")

language_option = st.sidebar.selectbox(
    "🌐 Response Language",
    ["Both (English & Urdu)", "English Only", "Urdu Only"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Pro Tips")
st.sidebar.info(
    "• Saaf aur achi roshni mein li gayi tasveer upload karein.\n• Beemari ya paton ka close-up shot behtareen result deta hai."
)

# Main Layout (2 Columns)
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📸 Upload Plant Image")
    uploaded_file = st.file_uploader(
        "Choose a plant image (JPG, PNG)...", type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(
            image,
            caption="Uploaded Specimen",
            use_container_width=True,
        )
        analyze_btn = st.button("🔍 Analyze Plant Health")
    else:
        analyze_btn = False

with col2:
    st.subheader("📋 Botanical Medical Report")

    if uploaded_file is None:
        st.info(
            "👈 Tasveer upload karein aur **Analyze Plant Health** dabayein."
        )

    elif analyze_btn:
        if not GEMINI_API_KEY:
            st.error(
                "⚠️ API Key missing! Please check your `.env` file configuration."
            )
        else:
            with st.spinner(
                "🌱 AI Doctor is examining the plant... Please wait!"
            ):
                try:
                    client = genai.Client(api_key=GEMINI_API_KEY)

                    lang_instruction = ""
                    if language_option == "English Only":
                        lang_instruction = "Provide the entire analysis in professional **English ONLY**."
                    elif language_option == "Urdu Only":
                        lang_instruction = "Provide the entire analysis in clear, natural **Urdu ONLY**."
                    else:
                        lang_instruction = "Provide the entire analysis in **BOTH English and Urdu** (Provide English text first, followed clearly by its Urdu translation below)."

                    prompt = f"""
                    You are an expert master botanist and plant pathologist. Analyze this plant image meticulously.
                    {lang_instruction}

                    Format the response using clean Markdown headings, emojis, and bullet points:
                    1. 🌿 **Plant Name** (Common & Scientific Name)
                    2. 🏥 **Health Status** (Healthy or Diseased - Specific disease name if applicable)
                    3. 💡 **Care Instructions** (Watering frequency, Sunlight requirements, Soil type)
                    4. 💊 **Treatment & Prevention Plan** (Actionable medical/remedial steps if sick, or long-term growth maintenance tips if healthy)
                    """

                    response = client.models.generate_content(
                        model="gemini-3.6-flash", contents=[image, prompt]
                    )

                    result_text = response.text

                    st.success("✅ Diagnosis Completed Successfully!")
                    st.markdown("---")
                    st.markdown(result_text)
                    st.markdown("---")

                    st.download_button(
                        label="📥 Download Official Report (.txt)",
                        data=result_text,
                        file_name="plant_medical_report.txt",
                        mime="text/plain",
                    )

                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")
