import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Page configuration
st.set_page_config(page_title="Cloud Credit Card Bills Dashboard", layout="wide")
st.title("☁️ Cloud Credit Card Bills Dashboard")

# Function to connect and fetch data manually
def get_gsheet_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Map secrets to the structure gspread expects
    # Ensure all these keys exist in your Streamlit Secrets
    creds_dict = {
        "type": "service_account",
        "project_id": st.secrets["project_id"],
        "private_key": st.secrets["private_key"].replace('\\n', '\n'),
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    }
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Open the sheet by URL and select the "Bills" worksheet
    sheet_url = "https://docs.google.com/spreadsheets/d/1jP6Ki5jcqqKW_NuUvtCo0nwuFnDp2ZQQt-ScLIf4xSI/edit"
    sheet = client.open_by_url(sheet_url).worksheet("Bills")
    
    # Return as DataFrame
    return pd.DataFrame(sheet.get_all_records())

# Display data
try:
    with st.spinner("Connecting to Google Sheets..."):
        df = get_gsheet_data()
        st.success("Data loaded successfully!")
        st.dataframe(df)
except Exception as e:
    st.error(f"Error connecting to Google Sheets: {e}")
