import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import io
import re
import base64
import json
import datetime
import matplotlib.pyplot as plt

# ✅ Set page config
st.set_page_config(
    page_title="Carbon Footprint Dashboard",
    page_icon="🌱",
    layout="wide"
)

# ✅ Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ✅ Mock Carbon Data (initial reference)
weekly_emissions = {
    "Monday": {"👕 Clothes": 5, "🚆 Transport": 15, "🥩 Food": 25},
    "Tuesday": {"👟 Clothes": 8, "🚗 Car": 20, "🍔 Fast Food": 15},
    "Wednesday": {"💻 Electronics": 120, "🚆 Transport": 10, "🥩 Food": 30},
    "Thursday": {"🚲 Bicycle": 2, "🥩 Food": 40, "🛒 Shopping": 25},
    "Friday": {"📱 Mobile": 5, "🚗 Car": 50, "🌿 Green Energy": -10},
    "Saturday": {"✈️ Flights": 100, "🥗 Vegan": 5, "🎮 Gaming": 20},
    "Sunday": {"🚆 Transport": 25, "🚗 Car": 30, "🛒 Shopping": 12},
}

mock_transactions = [
    {"date": "2024-02-05", "item": "T-Shirt", "category": "👕 Clothes", "co2": 2.5, "offset_cost": 0.75},
    {"date": "2024-02-05", "item": "Train Ticket", "category": "🚆 Transport", "co2": 10.2, "offset_cost": 3.10},
    {"date": "2024-02-04", "item": "Steak", "category": "🥩 Food", "co2": 30.0, "offset_cost": 9.00},
]

# ✅ Calculate total weekly emissions
total_weekly_emissions = sum(sum(day.values()) for day in weekly_emissions.values())

# ✅ Generate Stacked Bar Chart
def create_stacked_chart():
    days = list(weekly_emissions.keys())
    categories = {cat for day in weekly_emissions.values() for cat in day.keys()}
    category_colors = plt.cm.Paired.colors

    fig, ax = plt.subplots(figsize=(8, 4))
    bottom = [0] * len(days)

    for i, category in enumerate(categories):
        values = [weekly_emissions[day].get(category, 0) for day in days]
        ax.bar(days, values, label=category, bottom=bottom, color=category_colors[i % len(category_colors)])
        bottom = [b + v for b, v in zip(bottom, values)]

    ax.set_ylabel("CO₂ Emissions (kg)")
    ax.set_title("Weekly Carbon Emissions Breakdown")
    ax.legend(title="Categories", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)

    chart_path = "stacked_chart.png"
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close(fig)
    return chart_path

# ✅ Display Dashboard
st.markdown(f"""
    <h1 style='color: #114B5F;'>Hi, User!</h1>
    <div style='background: #88D498; padding: 16px; border-radius: 8px; color: white; text-align: center;'>
        <h2>You have emitted {total_weekly_emissions} kg of CO₂ this week 🌎</h2>
        <p>Track your impact and offset your emissions for a greener planet.</p>
    </div>
""", unsafe_allow_html=True)

# ✅ Display Stacked Bar Chart
chart_path = create_stacked_chart()
st.image(chart_path, caption="Weekly Carbon Footprint Breakdown", use_container_width=True)

# ✅ Display Recent Transactions
st.markdown("### 🛒 Recent Transactions")
for tx in mock_transactions:
    st.markdown(f"""
        <div style='background: white; padding: 16px; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); margin-bottom: 10px;'>
            <p><b>{tx['item']}</b> ({tx['category']})</p>
            <p><i>Date:</i> {tx['date']}</p>
            <p><b>Carbon Emitted:</b> {tx['co2']} kg CO₂</p>
            <p><b>Offset Cost:</b> ${tx['offset_cost']}</p>
        </div>
    """, unsafe_allow_html=True)

# ✅ Upload Receipt Section
st.markdown("## 🌱 Upload Your Receipt")
uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    display_image = Image.open(uploaded_file)
    if display_image:
        st.image(display_image, caption="Uploaded Receipt", use_container_width=True)
        st.session_state.image_data = display_image

submit = st.button("Analyze Carbon Footprint")

if submit and st.session_state.get("image_data") is not None:
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
            # Convert uploaded image to base64
            img_byte_arr = io.BytesIO()
            st.session_state.image_data.save(img_byte_arr, format='PNG')
            img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")

            # Call Generative AI model
            response = genai.GenerativeModel('gemini-1.5-flash').generate_content(
                [input_prompt, {"mime_type": "image/png", "data": img_base64}]
            ).text

            # Regex extraction
            st.session_state.carbon_score = float(re.search(r"Total Carbon Emissions:\s*([\d\.]+)", response).group(1))
            st.session_state.offset_cost = float(re.search(r"Offset Cost:\s*\$([\d\.]+)", response).group(1))

            if st.session_state.carbon_score and st.session_state.offset_cost:
                st.markdown("### 📊 Carbon Footprint Analysis")
                st.markdown(f"**Total Carbon Emissions:** {st.session_state.carbon_score} kg CO2")
                st.markdown(f"**Offset Cost:** ${st.session_state.offset_cost}")
                st.session_state.analysis_complete = True

                # ✅ Update users.json with new carbon score
                username = st.session_state.get("username", None)
                if username is None:
                    st.warning("No user is currently logged in. Please log in to update carbon history.")
                else:
                    try:
                        with open("users.json", "r") as f:
                            users_data = json.load(f)

                        # Ensure the user exists; if it's a string, convert it into a dict
                        if username in users_data:
                            if isinstance(users_data[username], str):
                                # Convert string into a dict: password = the existing string, add carbon_history
                                existing_password = users_data[username]
                                users_data[username] = {
                                    "password": existing_password,
                                    "carbon_history": []
                                }

                            if isinstance(users_data[username], dict):
                                carbon_history_entry = {
                                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "carbon_score": st.session_state.carbon_score,
                                    "offset_cost": st.session_state.offset_cost
                                }
                                users_data[username].setdefault("carbon_history", []).append(carbon_history_entry)
                                
                                with open("users.json", "w") as f:
                                    json.dump(users_data, f, indent=4)
                            else:
                                st.warning("Unable to update carbon history in users.json - invalid entry format.")
                        else:
                            st.warning("Unable to update carbon history in users.json - user not found.")

                    except FileNotFoundError:
                        st.error("users.json file not found. Cannot update carbon history.")

                # ✅ Regenerate the stacked_chart.png to reflect the new data
                # For demonstration, we'll just add the newly analyzed footprint to 'Sunday' as an extra category.
                weekly_emissions["Sunday"]["📄 Receipt Upload"] = st.session_state.carbon_score
                updated_chart_path = create_stacked_chart()
                st.image(updated_chart_path, caption="Updated Weekly Carbon Footprint Breakdown", use_container_width=True)

            else:
                st.error("Failed to extract values. Please check the receipt's clarity or try a different image.")

        except Exception as e:
            st.error(f"Error in processing the image: {str(e)}")

elif submit:
    st.warning("Please upload an image first! 📸")

# ✅ Logout Button
if st.button("Logout"):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.experimental_rerun()
