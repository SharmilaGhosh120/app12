# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests
import re

# --- Streamlit frontend ---

# Ensure queries.csv exists
CSV_FILE = "queries.csv"
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Email", "Query", "Timestamp"]).to_csv(CSV_FILE, index=False)

# Set page configuration
st.set_page_config(page_title="Ask Ky’ra – Your Internship Assistant", layout="centered")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Custom styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f6f5;
        padding: 20px;
        border-radius: 10px;
    }
    .stTextInput > div > input {
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    .stTextArea > div > textarea {
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    .submit-button {
        display: flex;
        justify-content: center;
    }
    .submit-button .stButton > button {
        background-color: #2e7d32;
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 8px;
        width: 200px;
    }
    .logo-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 100px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header with logo and welcome message
st.markdown(
    "<img src='https://via.placeholder.com/100?text=Ky%27ra+Logo' class='logo-img'/>",
    unsafe_allow_html=True
)
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>👋 Ask Ky’ra – Your Internship Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Hi! I’m Ky’ra, your internship buddy. Ask me anything about resumes, interviews, or project help - I’ll guide you step-by-step. Let’s grow together!</p>", unsafe_allow_html=True)

# Input fields
st.subheader("Your Details")
email_input = st.text_input("Student Email", placeholder="student123@college.edu", help="Enter your college email address.")
query_text = st.text_area("What would you like to ask Ky’ra?", height=150, placeholder="E.g., How can I prepare for my internship interview?")

# Example prompts
st.markdown("**Example Questions to Ask Ky’ra:**")
st.markdown("- How do I write my internship resume?")
st.markdown("- What are the best final-year projects in AI?")
st.markdown("- How can I prepare for my upcoming interview?")
st.markdown("- What skills should I learn for a career in cybersecurity?")

# Function to validate email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

# Function to call Ky’ra's backend API
def kyra_response(email, query):
    api_url = "http://kyra.kyras.in:8000/student-query"
    payload = {"student_id": email.strip(), "query": query.strip()}
    try:
        # Log payload for debugging
        st.write("Payload:", payload)
        response = requests.post(api_url, params=payload)
        if response.status_code == 200:
            return response.json().get("response", "No response from Ky’ra.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"API call failed: {str(e)}"

# Function to save queries to CSV
def save_query(email, query, timestamp):
    new_row = pd.DataFrame([[email, query, timestamp]], columns=["Email", "Query", "Timestamp"])
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(CSV_FILE, index=False)

# Submit button logic
st.markdown('<div class="submit-button">', unsafe_allow_html=True)
if st.button("Submit", type="primary"):
    if not email_input or not query_text:
        st.error("Please enter both a valid email and a query.")
    elif not is_valid_email(email_input):
        st.error("Please enter a valid email address (e.g., student@college.edu).")
    else:
        try:
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")
            response = kyra_response(email_input, query_text)
            save_query(email_input, query_text, timestamp)
            st.session_state.chat_history.append({
                "email": email_input,
                "query": query_text,
                "response": response,
                "timestamp": timestamp
            })
            st.success("Your query has been submitted. Ky'ra will respond soon!")
            with st.expander("🧠 Ky’ra’s Response", expanded=True):
                st.info(response)
        except Exception as e:
            st.error(f"Failed to process query: {str(e)}")
st.markdown('</div>', unsafe_allow_html=True)

# Display chat history
if st.session_state.chat_history:
    st.markdown("**🧾 Chat History:**")
    for i, entry in enumerate(st.session_state.chat_history):
        st.markdown(f"**{i+1}.** *{entry['email']}*: {entry['query']} *(submitted at {entry['timestamp']})*")
        st.markdown(f"   *Ky’ra*: {entry['response']}")
        st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)

# Note about CSV storage
st.markdown("*Note: Queries are saved in 'queries.csv' in the root folder of the Streamlit app environment.*")