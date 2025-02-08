import streamlit as st
import hashlib
import json
import os

st.set_page_config(page_title="Register", page_icon="📝", layout="centered")

DB_FILE = "users.json"

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

st.title("📝 Register for GreenTracker")

username = st.text_input("Choose a Username")
password = st.text_input("Choose a Password", type="password")

if st.button("Register"):
    if username in st.session_state.USER_DB:
        st.error("🚨 Username already exists! Choose a different one.")
    else:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        st.session_state.USER_DB[username] = hashed_password  # Store hashed password
        save_users(st.session_state.USER_DB)  # Save to JSON file
        st.success("✅ Registration successful! Redirecting to Login...")
        st.switch_page("login.py")

if st.button("Back to Login 🔑"):
    st.switch_page("login.py")
