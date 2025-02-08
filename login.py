import streamlit as st
import hashlib
import json
import os

# 1) Ensure set_page_config is the first Streamlit call
st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

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
.stTextInput, .stPasswordInput {
    padding: 12px;
    border: 1px solid #C4C4C4;
    border-radius: 8px;
}
.stTextInput:focus, .stPasswordInput:focus {
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

DB_FILE = "users.json"  # Store users here

# ✅ Load user data from JSON
def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as file:
        return json.load(file)

# ✅ Save user data to JSON
def save_users(users):
    with open(DB_FILE, "w") as file:
        json.dump(users, file, indent=4)

# Load users into session state
if "USER_DB" not in st.session_state:
    st.session_state.USER_DB = load_users()

st.title("🔐 Login to GreenTracker")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    if username in st.session_state.USER_DB and st.session_state.USER_DB[username] == hashed_password:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.success("✅ Login successful! Redirecting...")
        st.switch_page("pages/2_ImageUploader.py")
        st.rerun()
    else:
        st.error("🚨 Invalid username or password!")

if st.button("Register Here 📝"):
    st.switch_page("pages/1_Register.py")  # Redirect to Register page
