import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page configuration
st.set_page_config(page_title="US Visa DS-160 Professional Tracker", layout="wide")

# File path for data storage
DATA_FILE = "ds160_data.xlsx"

# Load or initialize data
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_excel(DATA_FILE)
        except Exception:
            return pd.DataFrame(columns=[
                "Applicant Name", "DS-160 Number", "Portal Username", 
                "Portal Password", "Application Date", "Submission Status", 
                "Appointment Date", "Handled By", "Branch Location"
            ])
    else:
        return pd.DataFrame(columns=[
            "Applicant Name", "DS-160 Number", "Portal Username", 
            "Portal Password", "Application Date", "Submission Status", 
            "Appointment Date", "Handled By", "Branch Location"
        ])

def save_data(df):
    df.to_excel(DATA_FILE, index=False)

# App layout
st.title("📋 US Visa DS-160 Professional Tracker")
st.write("---")

df = load_data()

# Counters Overview
total_pax = len(df)
submitted_count = len(df[df["Submission Status"].str.contains("Submitted —", na=False)])
pending_count = total_pax - submitted_count

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Applicants (PAX)", total_pax)
with col2:
    st.metric("Submitted", submitted_count)
with col3:
    st.metric("Pending Review", pending_count)

st.write("---")

# Data Entry Form
st.subheader("➕ Add New Applicant Details")
with st.form("entry_form", clear_on_submit=True):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        app_name = st.text_input("Applicant Name*")
        ds160_num = st.text_input("DS-160 Number*")
        p_user = st.text_input("Portal Username")
        app_date = st.date_input("Application Creation Date", datetime.today())
        handled_by = st.text_input("Handled By (Staff Name)*")
    with f_col2:
        p_pass = st.text_input("Portal Password")
        status = st.radio("Submission Status", [
            "Not Submitted — pending review or submission", 
            "Submitted — confirmation received"
        ])
        app_slot = st.date_input("Visa Appointment Date", value=None)
        branch = st.selectbox("Branch Location", ["Noida", "CP", "Gurgaon", "Other"])
        
    submit_btn = st.form_submit_button("💾 Save & Add to Master Sheet")
    
    if submit_btn:
        if app_name and ds160_num and handled_by:
            new_row = {
                "Applicant Name": app_name,
                "DS-160 Number": ds160_num,
                "Portal Username": p_user,
                "Portal Password": p_pass,
                "Application Date": app_date.strftime("%Y/%m/%d") if app_date else "",
                "Submission Status": status,
                "Appointment Date": app_slot.strftime("%Y/%m/%d") if app_slot else "",
                "Handled By": handled_by,
                "Branch Location": branch
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"Successfully saved details for {app_name}!")
            st.rerun()
        else:
            st.error("Please fill all the mandatory (*) fields.")

st.write("---")

# Master Data Table Section - FIXED TO SHOW ALL BY DEFAULT
st.subheader("🔍 Master Data View & Excel Export")

# Optional Search Bar
search_query = st.text_input("Quick Search (Search by Name, DS-160, Staff or Branch):", "")

# Filter data dynamically only if search query is provided
display_df = df.copy()
if search_query:
    search_query = search_query.lower()
    mask = (
        display_df["Applicant Name"].str.lower().str.contains(search_query, na=False) |
        display_df["DS-160 Number"].str.lower().str.contains(search_query, na=False) |
        display_df["Handled By"].str.lower().str.contains(search_query, na=False) |
        display_df["Branch Location"].str.lower().str.contains(search_query, na=False)
    )
    display_df = display_df[mask]

# ALWAYS SHOW THE COMPLETE DATA TABLE BELOW
if not display_df.empty:
    st.dataframe(display_df, use_container_width=True)
    
    # Export Option
    try:
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            display_df.to_excel(writer, sheet_name='DS160_Master', index=False)
        st.download_button(
            label="📥 Download List as Excel (XLSX)",
            data=buffer.getvalue(),
            file_name=f"DS160_Master_Report_{datetime.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception:
        st.info("Excel download ready upon system integration.")
else:
    st.info("No records found matching the current search query. Clear the search box to view all data.")
