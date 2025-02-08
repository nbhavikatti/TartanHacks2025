import google.generativeai as genai
import streamlit as st
import os
from PIL import Image
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the Google API key from the environment variables
google_api_key = os.getenv("GOOGLE_API_KEY")

# Ensure the API key is loaded correctly
if google_api_key is None:
    print("Error: GOOGLE_API_KEY not found in .env file")
else:
    print("Google API Key loaded successfully")

# Set page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="Carbon Receipt Analyzer",
    page_icon="🌱",
    layout="centered"
)

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("API Key not found! Ensure .env file is set up.")
    raise ValueError("Google API Key not found.")
genai.configure(api_key=api_key)

@st.cache_resource
def initialize_model():
    return genai.GenerativeModel('gemini-1.5-flash')

@st.cache_data(ttl=3600)
def get_gemini_response(_model, input_prompt, extracted_items):
    try:
        # Combine prompt and items for analysis
        prompt = input_prompt + "\n" + extracted_items
        response = _model.generate_content([prompt])
        return response.text
    except Exception as e:
        return None

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
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
        img_byte_arr = img_byte_arr.getvalue()
        return image, [{"mime_type": "image/jpeg", "data": img_byte_arr}]
    return None, None

def estimate_carbon_footprint(items):
    # Sample carbon emissions in kg CO2 per item
    carbon_emissions = {
        "shirt": 2.1,
        "pants": 3.0,
        "shoes": 4.5,
        "electronics": 50.0,
        "food": 1.5,
        "default": 5.0  # Default value for unrecognized items
    }

    total_emissions = 0
    for item, quantity in items.items():
        emission_per_item = carbon_emissions.get(item.lower(), carbon_emissions["default"])
        total_emissions += emission_per_item * quantity

    return total_emissions

model = initialize_model()

# Streamlit UI
st.markdown("""
    <h1 style='text-align: center; color: #2E7D32;'>🌱 Carbon Receipt Analyzer</h1>
    <p style='text-align: center;'>Upload your receipt to analyze the carbon footprint of your purchases.</p>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "jpeg", "png"], key="file_uploader")

if uploaded_file is not None:
    display_image, image_data = process_receipt_image(uploaded_file)
    if display_image:
        st.image(display_image, caption="📸 Uploaded Receipt", use_container_width=True)

submit = st.button("Analyze Carbon Footprint")

if submit and uploaded_file:
    with st.spinner("Analyzing receipt..."):
        # Example extracted items (in production, use OCR or manual text input)
        extracted_items = {
            "Shirt": 2,
            "Pants": 1,
            "Shoes": 1,
            "Food": 3
        }

        # Generate estimate
        total_emissions = estimate_carbon_footprint(extracted_items)
        offset_cost = round(total_emissions * 0.10, 2)  # $0.10 per kg CO2 to offset

        st.markdown("### 📊 Carbon Footprint Analysis")
        st.markdown(f"**🌍 Total Carbon Emissions:** {round(total_emissions, 2)} kg CO2")
        st.markdown(f"**💰 Offset Cost:** ${offset_cost}")
