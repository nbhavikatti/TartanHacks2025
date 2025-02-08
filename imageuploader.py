import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image, ImageEnhance
import io
import re
import base64

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

@st.cache_resource
def initialize_model():
    return genai.GenerativeModel('gemini-1.5-flash')

def get_gemini_response(_model, input_prompt, _image_object):
    try:
        # Convert PIL Image to base64 before passing to Gemini API
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

        # Enhance image contrast for better OCR results
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

        return image
    return None

def extract_numeric_value(text, pattern):
    match = re.search(pattern, text)
    if match:
        return float(match.group(1))
    return None

st.set_page_config(
    page_title="Carbon Receipt Analyzer",
    page_icon="🌱",
    layout="centered"
)

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
    <h1 style='text-align: center; color: #2E7D32;'>🌱 Carbon Receipt Analyzer</h1>
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
        st.session_state.error_message = None  # Reset error message

submit = st.button("Analyze Carbon Footprint")

if submit and st.session_state.image_data:
    st.session_state.analysis_complete = False  # Reset state before analysis
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

            # Debug: Log the raw response
            st.text("Debug: Raw Response from Model")
            st.write(response)

            # Improved extraction patterns
            st.session_state.carbon_score = extract_numeric_value(response, r"Total Carbon Emissions:\s*([\d\.]+)")
            st.session_state.offset_cost = extract_numeric_value(response, r"Offset Cost:\s*\$([\d\.]+)")

            if st.session_state.carbon_score is not None and st.session_state.offset_cost is not None:
                st.markdown("### 📊 Carbon Footprint Analysis")
                st.markdown(f"**Total Carbon Emissions:** {st.session_state.carbon_score} kg CO2")
                st.markdown(f"**Offset Cost:** ${st.session_state.offset_cost}")
                st.session_state.analysis_complete = True
            elif "Error:" in response:
                st.session_state.error_message = response
                st.error(st.session_state.error_message)
            else:
                st.error("Failed to extract values. Please check the receipt's clarity or try a different image.")
        except Exception as e:
            st.error(f"Error in processing the image: {str(e)}")
elif submit:
    st.warning("Please upload an image first! 📸")
