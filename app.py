import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yagmail
from datetime import datetime, timedelta
import streamlit_authenticator as stauth

# Dummy User Data
user_data = {
    "usernames": ["admin", "marketer1", "marketer2"],
    "passwords": ["admin123", "marketer1pass", "marketer2pass"],
    "names": ["Admin User", "Marketer One", "Marketer Two"],
    "emails": ["admin@example.com", "marketer1@example.com", "marketer2@example.com"],
}

# Authentication
authenticator = stauth.Authenticate(user_data["usernames"], user_data["names"], user_data["passwords"], "some_cookie_name", "some_signature_key", cookie_expiry_days=30)

# Login Section
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.write(f"Welcome **{name}**!")

    # Marketer Data Storage
    if 'marketer_data' not in st.session_state:
        st.session_state.marketer_data = pd.DataFrame(columns=["Customer Name", "Brand Name", "Meeting Rate", "Next Meeting Date", "Sold Product", "Product Price"])

    # Input Form for Marketers
    if username.startswith("marketer"):
        st.header("Add Customer Information")
        with st.form(key='customer_info_form'):
            customer_name = st.text_input("Customer Name")
            brand_name = st.text_input("Brand Name")
            meeting_rate = st.selectbox("Rate Meeting", options=["Excellent", "Good", "Average", "Poor"])
            next_meeting_date = st.date_input("Next Meeting Date", datetime.now() + timedelta(days=1))
            sold_product = st.radio("Did you sell the product?", options=["Yes", "No"])
            product_price = st.number_input("If yes, how much did you sell it for?", min_value=0.0, format="%.2f", disabled=(sold_product == "No"))
            
            submit_button = st.form_submit_button("Submit")
            if submit_button:
                st.session_state.marketer_data = st.session_state.marketer_data.append({
                    "Customer Name": customer_name,
                    "Brand Name": brand_name,
                    "Meeting Rate": meeting_rate,
                    "Next Meeting Date": next_meeting_date,
                    "Sold Product": sold_product,
                    "Product Price": product_price if sold_product == "Yes" else 0
                }, ignore_index=True)
                st.success("Customer information added!")

                st.write(st.session_state.marketer_data)

    # Show the data and performance charts
    if st.session_state.marketer_data.shape[0] > 0:
        st.header("Customer Data")
        st.dataframe(st.session_state.marketer_data)

        # Performance Chart
        st.header("Performance Chart")
        performance_data = st.session_state.marketer_data.groupby('Meeting Rate').sum().reset_index()
        fig = px.bar(performance_data, x='Meeting Rate', y='Product Price', title="Sales Performance by Meeting Rate")
        st.plotly_chart(fig)

    # Reminder for Meetings
    if username.startswith("marketer"):
        st.header("Meeting Reminders")
        for index, row in st.session_state.marketer_data.iterrows():
            if row["Next Meeting Date"] == datetime.now().date() + timedelta(days=1):
                yag = yagmail.SMTP("your_email@example.com", "your_email_password")
                yag.send(to=row["Customer Name"], subject="Meeting Reminder", contents=f"Reminder for your meeting scheduled tomorrow.")

else:
    if authentication_status is False:
        st.error("Username/password is incorrect")
    elif authentication_status is None:
        st.warning("Please enter your username and password")
