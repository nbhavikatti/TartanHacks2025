import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import io

load_dotenv()
genai.configure(api_key=os.getenv("AIzaSyBvmzdEkv49o4T6It7YiQ4fh2NQgfRhDBE"))

@st.cache_resource
def initialize_model():
    return genai.GenerativeModel('gemini-1.5-flash')

@st.cache_data(ttl=3600)
def get_gemini_response(_model, input_prompt, image_hash):
    try:
        response = _model.generate_content([input_prompt, st.session_state.image_data[0]])
        return response.text
    except Exception as e:
        return f"Error in analysis: {str(e)}"

def get_modification_response(_model, modification_prompt):
    try:
        response = _model.generate_content([modification_prompt, st.session_state.image_data[0]])
        return response.text
    except Exception as e:
        return f"Error in generating modification: {str(e)}"

def process_image(upload):
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
        
        return image, [{
            "mime_type": "image/jpeg",
            "data": img_byte_arr
        }]
    return None, None

st.set_page_config(
    page_title="CarbonBank - Your Personal Carbon Transaction Tracker",
    page_icon="🥗",
    layout="centered"
)

if 'image_data' not in st.session_state:
    st.session_state.image_data = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'custom_prompt' not in st.session_state:
    st.session_state.custom_prompt = ""
if 'show_custom_input' not in st.session_state:
    st.session_state.show_custom_input = False

st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem;
        border-radius: 0.5rem;
        border: none;
        margin-bottom: 0.5rem;
    }
    .stButton>button:hover { background-color: #45a049; }
    .upload-text {
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    .title {
        color: #2E7D32;
        text-align: center;
        padding: 1rem;
        border-bottom: 2px solid #4CAF50;
        margin-bottom: 2rem;
    }
    .stSpinner > div { border-top-color: #4CAF50 !important; }
    .modification-button {
        margin: 0.25rem;
        padding: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

model = initialize_model()

st.markdown("<h1 class='title'>🥗 CarbonBank</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; margin-bottom: 2rem;'>Upload your meal, know it, eat better!</p>", unsafe_allow_html=True)

with st.container():
    st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 2rem;">
            <p class="upload-text" style="text-align: center;">📸 Choose an image:</p>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="file_uploader"
    )

    if uploaded_file is not None:
        display_image, image_data = process_image(uploaded_file)
        if display_image:
            st.session_state.image_data = image_data
            st.image(display_image, use_column_width=True)

    analyze_button_html = """
    
    """
    analyze_button_script = """
    <script>
        document.getElementById('analyze_button').onclick = function() {
            document.getElementById('streamlitSubmitButton').click();
        }
    </script>
    """

    st.markdown(analyze_button_html, unsafe_allow_html=True)
    st.markdown(analyze_button_script, unsafe_allow_html=True)
    submit = st.button("Analyze Nutrition", key="streamlitSubmitButton", use_container_width=False)

if submit and st.session_state.image_data:
    with st.spinner('Analyzing your meal...'):
        input_prompt = "Analyze the nutritional content of the meal in the uploaded image."

        image_hash = hash(str(st.session_state.image_data[0]['data']))
        response = get_gemini_response(model, input_prompt, image_hash)
        
        st.markdown("### 📊 Analysis Results")
        st.markdown("""
            <div style='background-color: #f5f5f5; 
                        padding: 1.5rem; 
                        border-radius: 0.5rem; 
                        border-left: 5px solid #4CAF50;'>
        """, unsafe_allow_html=True)
        st.write(response)
        st.markdown("</div>", unsafe_allow_html=True)
        st.session_state.analysis_complete = True
elif submit:
    st.warning("Please upload an image first! 📸")

if st.session_state.analysis_complete:
    st.markdown("### 🔄 Modify Recipe")
    
    mod_col1, mod_col2 = st.columns([3, 1])
    
    with mod_col1:
        st.markdown("<p style='margin-top: 1rem;'>Use the button to the right to ask anything about this meal!</p>", unsafe_allow_html=True)
    
    with mod_col2:
        if st.button("Other Options 🔍"):
            st.session_state.show_custom_input = True

    if st.session_state.show_custom_input:
        custom_input = st.text_input(
            "Ask anything about this meal:",
            key="custom_query",
            help="Press Enter after typing your question"
        )
        
        if custom_input:
            with st.spinner('Generating response...'):
                custom_response = get_modification_response(model, custom_input)
                st.success(custom_response)