import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="US Visa DS-160 Professional Tracker", layout="wide")

# Google Sheet से कनेक्शन
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # सीधा आपकी गूगल शीट से डेटा लोड करेगा
        return conn.read(worksheet="MasterSheet", ttl="0d")
    except Exception:
        return pd.DataFrame(columns=["Applicant Name", "DS-160 Number", "Portal Username", "Portal Password", "Application Date", "Submission Status", "Appointment Date", "Handled By", "Branch Location"])

st.title("📋 US Visa DS-160 Professional Tracker")
st.write("---")

df = load_data()
if df.empty:
    df = pd.DataFrame(columns=["Applicant Name", "DS-160 Number", "Portal Username", "Portal Password", "Application Date", "Submission Status", "Appointment Date", "Handled By", "Branch Location"])

total_pax = len(df)
submitted_count = len(df[df["Submission Status"].str.contains("Submitted —", na=False)]) if total_pax > 0 else 0
pending_count = total_pax - submitted_count

col1, col2, col3 = st.columns(3)
with col1: st.metric("Total Applicants (PAX)", total_pax)
with col2: st.metric("Submitted", submitted_count)
with col3: st.metric("Pending Review", pending_count)

st.write("---")
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
        status = st.radio("Submission Status", ["Not Submitted — pending review or submission", "Submitted — confirmation received"])
        app_slot = st.date_input("Visa Appointment Date", value=None)
        branch = st.selectbox("Branch Location", ["Noida", "CP", "Gurgaon", "Other"])
        
    submit_btn = st.form_submit_button("💾 Save & Add to Master Sheet")
    
    if submit_btn:
        if app_name and ds160_num and handled_by:
            new_row = {
                "Applicant Name": app_name, "DS-160 Number": ds160_num, "Portal Username": p_user,
                "Portal Password": p_pass, "Application Date": app_date.strftime("%Y/%m/%d") if app_date else "",
                "Submission Status": status, "Appointment Date": app_slot.strftime("%Y/%m/%d") if app_slot else "",
                "Handled By": handled_by, "Branch Location": branch
            }
            # नया डेटा पुरानी लिस्ट में जोड़ें
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            # सीधा गूगल शीट में सेव करें
            conn.update(worksheet="MasterSheet", data=updated_df)
            st.success(f"Successfully saved details for {app_name}!")
            st.rerun()
        else:
            st.error("Please fill all the mandatory (*) fields.")

st.write("---")
st.subheader("🔍 Master Data View & Excel Export")
search_query = st.text_input("Quick Search:", "")

display_df = df.copy()
if search_query and not display_df.empty:
    search_query = search_query.lower()
    mask = (display_df["Applicant Name"].astype(str).str.lower().str.contains(search_query, na=False) |
            display_df["DS-160 Number"].astype(str).str.lower().str.contains(search_query, na=False))
    display_df = display_df[mask]

if not display_df.empty:
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("No records found.")
