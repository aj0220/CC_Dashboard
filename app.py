import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Cloud Credit Card Dashboard", layout="wide")
st.title("☁️ Cloud Credit Card Bills Dashboard")

# Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Read data from the "Bills" worksheet
df = conn.read(worksheet="Bills", ttl=5) 
df = df.dropna(subset=['Card']).copy()

# Ensure proper data types
df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
df['Payment done'] = df['Payment done'].fillna('Pending').astype(str).str.title().str.strip()
df['Payment Status'] = df['Payment done'].apply(
    lambda x: 'Paid' if x.lower() in ['na', 'yes', 'done', 'paid'] else 'Pending'
)

# --- ADD NEW BILL FORM ---
with st.expander("➕ Add a New Bill"):
    with st.form("add_bill_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        new_card = col1.text_input("Card Name")
        new_holder = col2.text_input("Issued To")
        new_amount = col1.number_input("Amount (₹)", min_value=0.0, step=0.01)
        new_date = col2.date_input("Due Date")
        new_status = st.selectbox("Status", ["Pending", "Paid"])
        
        submitted = st.form_submit_button("Save to Cloud")
        if submitted and new_card:
            # Create new row
            new_row = pd.DataFrame([{
                'Card': new_card, 
                'Issued to': new_holder, 
                'amount': new_amount, 
                'due date': new_date.strftime("%Y-%m-%d"), 
                'Payment done': new_status
            }])
            # Combine with existing data and update Google Sheet
            updated_df = pd.concat([new_row, df], ignore_index=True)
            conn.update(worksheet="Bills", data=updated_df)
            st.success("Bill added successfully! Reloading...")
            st.rerun()

# --- KPI METRICS ---
total_amount = df['amount'].sum()
pending_amount = df[df['Payment Status'] == 'Pending']['amount'].sum()
paid_amount = df[df['Payment Status'] == 'Paid']['amount'].sum()

st.markdown("### 📊 Quick Summary")
c1, c2, c3 = st.columns(3)
c1.metric("Total Billed Amount", f"₹ {total_amount:,.2f}")
c2.metric("Total Pending Amount", f"₹ {pending_amount:,.2f}")
c3.metric("Total Paid Amount", f"₹ {paid_amount:,.2f}")

st.divider()

# --- CHARTS ---
col_charts1, col_charts2 = st.columns(2)
with col_charts1:
    st.subheader("Bill Amounts by Credit Card")
    chart_df = df[df['amount'] > 0]
    if not chart_df.empty:
        fig_bar = px.bar(chart_df, x='Card', y='amount', color='Payment Status', 
                         color_discrete_map={"Paid": "#2ecc71", "Pending": "#e74c3c"})
        st.plotly_chart(fig_bar, use_container_width=True)

with col_charts2:
    st.subheader("Amount Breakdown")
    if total_amount > 0:
        fig_pie = px.pie(df, names='Payment Status', values='amount', hole=0.4,
                         color='Payment Status', color_discrete_map={"Paid": "#2ecc71", "Pending": "#e74c3c"})
        st.plotly_chart(fig_pie, use_container_width=True)

# --- DATA TABLE ---
st.subheader("📝 Live Master Data")
st.dataframe(df[['Card', 'Issued to', 'amount', 'due date', 'Payment Status']], use_container_width=True, hide_index=True)