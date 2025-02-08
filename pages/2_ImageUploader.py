import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image, ImageEnhance
import io
import re
import base64
import json
import datetime

# 1) Ensure set_page_config is the first Streamlit call
st.set_page_config(
    page_title="Carbon Receipt Analyzer",
    page_icon="🌱",
    layout="wide"
)

# 2) Then bring in your custom CSS
st.markdown("""
<style>
/* Import the "Inter" font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body {
    background-color: #F4F7F5;
    margin: 0 auto;
    font-family: 'Inter', sans-serif;
    color: #222222;
}

/* Center the layout and set a max width */
.main .block-container {
    max-width: 900px;
    padding: 24px;
    border-radius: 8px;
    margin: 0 auto;
    background-color: #FFFFFF;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
}

/* Headings */
h1, h2, h3 {
    color: #114B5F;
    font-weight: 700;
    margin-top: 16px;
    margin-bottom: 16px;
}
h1 { font-size: 32px; }
h2 { font-size: 28px; }
h3 { font-size: 24px; }

/* Body text and labels */
p, div, label, span, input {
    font-size: 16px;
}

/* Input fields */
.stTextInput, .stFileUploader, .stNumberInput {
    padding: 12px;
    border: 1px solid #C4C4C4;
    border-radius: 8px;
}
.stTextInput:focus, .stFileUploader:focus, .stNumberInput:focus {
    outline: none !important;
    box-shadow: 0 0 4px 2px #88D498;
}

/* Primary buttons */
.stButton button {
    background: linear-gradient(to right, #1A936F, #114B5F);
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s ease-in-out;
}
.stButton button:hover {
    transform: scale(1.02);
}
.stButton>button:focus:not(:active) {
    box-shadow: 0 0 5px 2px #88D498;
}

/* Alert boxes */
[data-testid="stAlert"] {
    border-radius: 8px;
}
.st-error {
    color: #D72638 !important;
}
.st-success {
    color: #3A7D44 !important;
}
</style>
""", unsafe_allow_html=True)

DB_FILE = "users.json"  # Path to users.json

# ✅ Authentication Check
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("🚨 You must be logged in to access this page.")
    st.switch_page("Login")  # Redirect if not authenticated

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

@st.cache_resource
def initialize_model():
    return genai.GenerativeModel('gemini-1.5-flash')

def get_gemini_response(_model, input_prompt, _image_object):
    try:
        img_byte_arr = io.BytesIO()
        _image_object.save(img_byte_arr, format='PNG')
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")

        response = _model.generate_content([input_prompt, {"mime_type": "image/png", "data": img_base64}])
        return response.text
    except Exception as e:
        return f"Error in analysis: {str(e)}"

def process_receipt_image(upload):
    if upload is not None:
        image = Image.open(upload)
        max_size = 1024
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        if image.mode != 'RGB':
            image = image.convert('RGB')

        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

        return image
    return None

def extract_numeric_value(text, pattern):
    match = re.search(pattern, text)
    if match:
        return float(match.group(1))
    return None

# ✅ Load user data from JSON
def load_users():
    try:
        with open(DB_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # If file doesn't exist, return empty dict

# ✅ Save user data to JSON
def save_users(users):
    with open(DB_FILE, "w") as file:
        json.dump(users, file, indent=4)

# ✅ Store Carbon Score in `users.json`
def save_carbon_score(username, carbon_score, offset_cost):
    users = load_users()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if username not in users:
        st.error("User not found in database!")
        return

    # If user only has a password, convert their data into a dict
    if isinstance(users[username], str):
        users[username] = {"password": users[username], "carbon_history": []}

    # Append new carbon footprint data
    users[username]["carbon_history"].append({
        "timestamp": timestamp,
        "carbon_score": carbon_score,
        "offset_cost": offset_cost
    })

    save_users(users)

if 'image_data' not in st.session_state:
    st.session_state.image_data = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'carbon_score' not in st.session_state:
    st.session_state.carbon_score = None
if 'offset_cost' not in st.session_state:
    st.session_state.offset_cost = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None

model = initialize_model()

st.markdown("""
    <h1 style='text-align: center; color: #114B5F;'>🌱 Carbon Receipt Analyzer</h1>
    <p style='text-align: center;'>Upload your receipt to analyze the carbon footprint of your purchases.</p>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "jpeg", "png"], key="file_uploader")

if uploaded_file is not None:
    display_image = process_receipt_image(uploaded_file)
    if display_image:
        st.session_state.image_data = display_image
        st.image(display_image, caption="Uploaded Receipt", use_container_width=True)
        st.session_state.analysis_complete = False
        st.session_state.carbon_score = None
        st.session_state.offset_cost = None
        st.session_state.error_message = None  # reset

submit = st.button("Analyze Carbon Footprint")

if submit and st.session_state.image_data:
    st.session_state.analysis_complete = False
    st.session_state.carbon_score = None
    st.session_state.offset_cost = None
    st.session_state.error_message = None

    with st.spinner('Analyzing receipt...'):
        input_prompt = (
            "Analyze the uploaded receipt and extract items purchased along with their quantities. "
            "Perform an in-depth analysis of the carbon footprint by considering product categories, materials, transportation, and manufacturing impact. "
            "Provide a refined estimate in kilograms of CO2 for the entire purchase, ensuring the use of industry-standard emission values where available. "
            "Calculate the estimated cost in USD to offset this carbon footprint using up-to-date carbon credit prices. "
            "Ensure that the response contains: 'Total Carbon Emissions: X kg CO2' and 'Offset Cost: $X' as exact phrases for extraction. "
            "If the image is not a receipt or is invalid, respond with an error message: 'Error: The uploaded image is not a valid receipt.'"
        )

        try:
            response = get_gemini_response(model, input_prompt, st.session_state.image_data)

            st.session_state.carbon_score = extract_numeric_value(response, r"Total Carbon Emissions:\s*([\d\.]+)")
            st.session_state.offset_cost = extract_numeric_value(response, r"Offset Cost:\s*\$([\d\.]+)")

            if st.session_state.carbon_score is not None and st.session_state.offset_cost is not None:
                st.markdown("### 📊 Carbon Footprint Analysis")
                st.markdown(f"**Total Carbon Emissions:** {st.session_state.carbon_score} kg CO2")
                st.markdown(f"**Offset Cost:** ${st.session_state.offset_cost}")
                st.session_state.analysis_complete = True

                if "username" in st.session_state:
                    save_carbon_score(st.session_state.username, st.session_state.carbon_score, st.session_state.offset_cost)
                else:
                    st.error("🚨 Error: No username found in session state!")

            elif "Error:" in response:
                st.session_state.error_message = response
                st.error(st.session_state.error_message)
            else:
                st.error("Failed to extract values. Please check the receipt's clarity or try a different image.")
        except Exception as e:
            st.error(f"Error in processing the image: {str(e)}")
elif submit:
    st.warning("Please upload an image first! 📸")

if st.button("Logout"):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.switch_page("Login")
