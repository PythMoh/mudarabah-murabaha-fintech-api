import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit Page Configuration
st.set_page_config(
    page_title="Sharia Fintech Portal",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Mudarabah Profit-Sharing Calculator")
st.markdown("Automated non-interest banking profit distribution and accounting platform.")

# API Backend URL
API_URL = "http://127.0.0.1:8000/api/v1/calculate-mudarabah"

# Layout Columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Transaction Parameters")
    
    with st.form("mudarabah_form"):
        account_id = st.number_input("Financing Account ID", min_value=1, value=1, step=1)
        gross_revenue = st.number_input("Gross Revenue (₦)", min_value=1000.0, value=350000.0, step=10000.0)
        operating_expenses = st.number_input("Operating Expenses (₦)", min_value=0.0, value=50000.0, step=5000.0)
        
        # Bank Profit Sharing Ratio Slider
        bank_psr_percent = st.slider("Bank Profit-Sharing Ratio (%)", min_value=5, max_value=95, value=30)
        bank_psr_ratio = bank_psr_percent / 100.0
        
        submit_button = st.form_submit_button("Calculate & Persist Record")

if submit_button:
    payload = {
        "account_id": account_id,
        "gross_revenue": gross_revenue,
        "operating_expenses": operating_expenses,
        "bank_psr_ratio": bank_psr_ratio
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            st.success(f"Record successfully saved! Calculation ID: {data['calculation_id']}")
            
            # Compute Display Values
            net_profit = gross_revenue - operating_expenses
            bank_share = net_profit * bank_psr_ratio if net_profit > 0 else 0
            customer_share = net_profit * (1 - bank_psr_ratio) if net_profit > 0 else net_profit

            with col2:
                st.subheader("📈 Profit Share Summary")
                st.metric("Net Profit", f"₦{net_profit:,.2f}")
                
                m1, m2 = st.columns(2)
                m1.metric("Bank Share", f"₦{bank_share:,.2f}", f"{bank_psr_percent}%")
                m2.metric("Customer Share", f"₦{customer_share:,.2f}", f"{100 - bank_psr_percent}%")
                
                # Visual Breakdown Chart
                if net_profit > 0:
                    fig, ax = plt.subplots()
                    labels = ['Bank Share', 'Customer Share']
                    sizes = [bank_share, customer_share]
                    colors = ['#1f77b4', "#30a02c"]
                    
                    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
                    ax.axis('equal')
                    st.pyplot(fig)
        else:
            err_detail = response.json().get("detail", "Calculation Error")
            st.error(f"API Error ({response.status_code}): {err_detail}")
            
    except Exception as e:
        st.error(f"Failed to communicate with FastAPI backend server: {e}")