# EcoSpend! - AI-Powered Carbon Footprint Analyzer 🌿

EcoSpend! is a fintech-inspired application created during TartanHacks2025 by two Dartmouth and two CMU students that empowers users to monitor and reduce their carbon footprint by analyzing purchase receipts. Utilizing AI-driven receipt parsing and SQL-based analytics, the platform provides real-time estimates of carbon emissions and calculates offset costs, promoting eco-conscious spending habits.

## Features 🚀

- **AI-Powered Receipt Analysis**: Upload receipts to extract purchase details using Google's Gemini AI.
- **Carbon Emission Calculation**: Estimate total CO₂ emissions based on product categories, materials, and transportation impact.
- **Offset Cost Estimation**: Calculate the cost to neutralize emissions using up-to-date carbon credit pricing.
- **User Accounts & History Tracking**: Secure login system with password hashing and a history of past carbon scores.
- **SQL-Based Data Analytics**: Aggregate carbon impact over time, view trends, and compare footprints across users.
- **Minimalistic Fintech UI**: Built with Streamlit, featuring a forest-inspired design for clarity and ease of use.
- **Time-Series Data Visualization**: Track carbon footprint trends over time with interactive charts.

## Tech Stack 🛠️

- **Frontend**: Streamlit (Gradio-style UI)
- **Backend**: Python, OpenAI Gemini API
- **Database**: SQL (Scalable user authentication, carbon history tracking, and data storage for future analytics)
- **AI Model**: Google Gemini-1.5 Flash for receipt processing
- **Data Visualization**: Matplotlib & Pandas for trend analysis

## How to Run the Code ##

First, clone the github repository. Then, setup a (virtual) python environment. Then follow the steps below.

## Libraries to Download (Using Python3) 
```bash
pip3 install streamlit flask werkzeug pandas mysql-connector-python
```

## Run the Streamlit App  
```bash
python3 -m streamlit run login.py
```
You should see a local URL (something like "http://localhost:8501"). Open the URL in your web browser.

Contact: vtoolsid@andrew.cmu.edu, neil.bhavikatti.28@dartmouth.edu, jx.28@dartmouth.edu, bnajibmo@andrew.cmu.edu





