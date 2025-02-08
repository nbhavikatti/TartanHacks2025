import streamlit as st
import hashlib
import json
import os

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

DB_FILE = "users.json"  # Store users here

# ✅ Load user data from JSON
def load_users():
    if not os.path.exists(DB_FILE):  
        return {}  # Return empty dict if file doesn't exist
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
