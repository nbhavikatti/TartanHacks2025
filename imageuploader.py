import google.generativeai as genai
import streamlit as st
import os
from PIL import Image
import io
import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("GOOGLE_API_KEY"))  # Debugging step


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY")) 

@st.cache_resource
def initialize_model():
    return genai.GenerativeModel('gemini-1.5-flash')

@st.cache_data(ttl=3600)
def get_gemini_response(_model, input_prompt, image_data):
    try:
        response = _model.generate_content([input_prompt, image_data])
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
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
        img_byte_arr = img_byte_arr.getvalue()
        
        return image, [{"mime_type": "image/jpeg", "data": img_byte_arr}]
    return None, None

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

model = initialize_model()

st.markdown("""
    <h1 style='text-align: center; color: #2E7D32;'>🌱 Carbon Receipt Analyzer</h1>
    <p style='text-align: center;'>Upload your receipt to analyze the carbon footprint of your purchases.</p>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "jpeg", "png"], key="file_uploader")

if uploaded_file is not None:
    display_image, image_data = process_receipt_image(uploaded_file)
    if display_image:
        st.session_state.image_data = image_data
        st.image(display_image, caption="Uploaded Receipt", use_column_width=True)

submit = st.button("Analyze Carbon Footprint")

if submit and st.session_state.image_data:
    with st.spinner('Analyzing receipt...'):
        input_prompt = "Analyze the receipt in the uploaded image. Extract the purchased items, quantities, and calculate the carbon footprint of each. Provide a total carbon score in kg CO2, and the cost in USD to offset the emissions."
        
        response = get_gemini_response(model, input_prompt, st.session_state.image_data)
        
        if "Error" not in response:
            try:
                lines = response.split("\n")
                st.session_state.carbon_score = float([line for line in lines if "Total Carbon Emissions" in line][0].split(":")[1].strip().split()[0])
                st.session_state.offset_cost = float([line for line in lines if "Offset Cost" in line][0].split(":")[1].strip().split()[0])
                
                st.markdown("### 📊 Carbon Footprint Analysis")
                st.markdown(f"**Total Carbon Emissions:** {st.session_state.carbon_score} kg CO2")
                st.markdown(f"**Offset Cost:** ${st.session_state.offset_cost}")
                st.session_state.analysis_complete = True
            except Exception as e:
                st.error(f"Error in extracting data: {str(e)}")
        else:
            st.error(response)
elif submit:
    st.warning("Please upload an image first! 📸")
