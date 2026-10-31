import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/api/v1/calculate-murabaha"

st.set_page_config(page_title="Murabaha Cost-Plus Calculator", layout="wide")
st.title("🏦 Murabaha (Cost-Plus) Financing Portal")
st.markdown("Sharia-Compliant Cost Markup & Deferred Payment Schedule Generator")

# --- Input Form ---
with st.sidebar:
    st.header("Contract Parameters")
    account_id = st.number_input("Financing Account ID", min_value=1, value=1, step=1)
    asset_cost = st.number_input("Asset Acquisition Cost (₦)", min_value=10000.0, value=5000000.0, step=50000.0)
    profit_rate_pct = st.slider("Annual Profit Rate (%)", min_value=1.0, max_value=50.0, value=10.0, step=0.5)
    tenure_months = st.selectbox("Tenure (Months)", options=[6, 12, 18, 24, 36, 48, 60], index=1)

    submit_btn = st.button("Generate & Persist Contract", type="primary")

# --- Execution & Rendering ---
if submit_btn:
    payload = {
        "account_id": int(account_id),
        "asset_cost": float(asset_cost),
        "profit_rate_annual": float(profit_rate_pct / 100.0),
        "tenure_months": int(tenure_months)
    }

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            summary = data["summary"]
            schedule = data["amortization_schedule"]

            st.success(f"Contract #{data['contract_id']} created and persisted to database!")

            # Metric Cards
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Asset Cost", f"₦{summary['asset_cost']:,.2f}")
            col2.metric("Total Profit Markup", f"₦{summary['total_profit']:,.2f}")
            col3.metric("Total Selling Price", f"₦{summary['total_selling_price']:,.2f}")
            col4.metric("Monthly Installment", f"₦{summary['monthly_installment']:,.2f}")

            st.divider()

            # Schedule Table & Export
            st.subheader("📊 Repayment Schedule Breakdown")
            df_schedule = pd.DataFrame(schedule)
            st.dataframe(df_schedule, use_container_width=True)

            csv = df_schedule.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Amortization Schedule (CSV)",
                data=csv,
                file_name=f"murabaha_contract_{data['contract_id']}_schedule.csv",
                mime="text/csv"
            )
        else:
            st.error(f"API Error ({response.status_code}): {response.json().get('detail')}")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to FastAPI server. Ensure Uvicorn is running on port 8000.")