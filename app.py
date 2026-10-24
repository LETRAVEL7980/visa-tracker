import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page configuration
st.set_page_config(page_title="US Visa DS-160 Professional Tracker", layout="wide")

# File path for data storage
DATA_FILE = "ds160_data.csv"

# YOUR CORRECT OFFICIAL US VISA PORTAL URL
VISA_PORTAL_URL = "https://usvisascheduling.com"

# Load or initialize data
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            required_cols = [
                "Applicant Name", "DS-160 Number", "Portal Username", 
                "Portal Password", "Application Date", "Submission Status", 
                "Appointment Date", "Handled By", "Branch Location"
            ]
            for col in required_cols:
                if col not in df.columns:
                    df[col] = ""
            return df
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
    df.to_csv(DATA_FILE, index=False)

# App layout
st.title("📋 US Visa DS-160 Professional Tracker")
st.write("---")

df = load_data()

# Clean strings for processing safely
for col in df.columns:
    df[col] = df[col].astype(str).replace("nan", "").replace("None", "").str.strip()

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

# Main Section: Add or Edit Data
st.subheader("📝 Data Management (Add New or Edit Existing)")

tab1, tab2 = st.tabs(["➕ Add New Applicant", "✏️ Edit / Update & Track Appointment"])

# TAB 1: ADD NEW APPLICANT
with tab1:
    with st.form("entry_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            app_name = st.text_input("Applicant Name*")
            ds160_num = st.text_input("DS-160 Number*")
            p_user = st.text_input("Portal Username")
            app_date = st.date_input("Application Creation Date", datetime.today(), key="add_date")
            handled_by = st.text_input("Handled By (Staff Name)*")
        with f_col2:
            p_pass = st.text_input("Portal Password")
            status = st.radio("Submission Status", [
                "Not Submitted — pending review or submission", 
                "Submitted — confirmation received"
            ], key="add_status")
            app_slot = st.date_input("Visa Appointment Date", value=None, key="add_slot")
            branch = st.selectbox("Branch Location", ["Noida", "CP", "Gurgaon", "Other"], key="add_branch")
            
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

# TAB 2: EDIT & PORTAL LINK
with tab2:
    if not df.empty:
        df['select_label'] = df['Applicant Name'] + " (" + df['DS-160 Number'] + ")"
        selected_label = st.selectbox("Select Applicant to Edit or Track:", df['select_label'].tolist())
        
        idx = df[df['select_label'] == selected_label].index
        
        if len(idx) > 0:
            row_idx = idx[0]
            
            # --- QUICK PORTAL LINK SECTION ---
            st.info("💡 **Quick Appointment Tracking:** Click the button below to go directly to the official tracking system. Use credentials displayed down below.")
            st.link_button("🔗 Open Official US Visa scheduling Portal", VISA_PORTAL_URL, type="primary")
            st.write("---")
            
            with st.form("edit_form"):
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    edit_name = st.text_input("Applicant Name*", value=str(df.loc[row_idx, "Applicant Name"]))
                    edit_ds160 = st.text_input("DS-160 Number*", value=str(df.loc[row_idx, "DS-160 Number"]))
                    edit_user = st.text_input("Portal Username", value=str(df.loc[row_idx, "Portal Username"]))
                    
                    try:
                        init_app_date = datetime.strptime(str(df.loc[row_idx, "Application Date"]), "%Y/%m/%d") if df.loc[row_idx, "Application Date"] != "" else datetime.today()
                    except ValueError:
                        init_app_date = datetime.today()
                    edit_app_date = st.date_input("Application Creation Date", init_app_date, key="edit_date")
                    
                    edit_handled = st.text_input("Handled By (Staff Name)*", value=str(df.loc[row_idx, "Handled By"]))
                    
                with e_col2:
                    edit_pass = st.text_input("Portal Password", value=str(df.loc[row_idx, "Portal Password"]))
                    
                    current_status = str(df.loc[row_idx, "Submission Status"])
                    status_options = [
                        "Not Submitted — pending review or submission", 
                        "Submitted — confirmation received"
                    ]
                    status_index = status_options.index(current_status) if current_status in status_options else 0
                    edit_status = st.radio("Submission Status", status_options, index=status_index, key="edit_status")
                    
                    try:
                        init_slot = datetime.strptime(str(df.loc[row_idx, "Appointment Date"]), "%Y/%m/%d").date() if df.loc[row_idx, "Appointment Date"] != "" else None
                    except ValueError:
                        init_slot = None
                    edit_slot = st.date_input("Visa Appointment Date", value=init_slot, key="edit_slot")
                    
                    current_branch = str(df.loc[row_idx, "Branch Location"])
                    branch_options = ["Noida", "CP", "Gurgaon", "Other"]
                    branch_index = branch_options.index(current_branch) if current_branch in branch_options else 0
                    edit_branch = st.selectbox("Branch Location", branch_options, index=branch_index, key="edit_branch")
                    
                update_btn = st.form_submit_button("🔄 Update & Save Changes")
                
                if update_btn:
                    if edit_name and edit_ds160 and edit_handled:
                        df.loc[row_idx, "Applicant Name"] = edit_name
                        df.loc[row_idx, "DS-160 Number"] = edit_ds160
                        df.loc[row_idx, "Portal Username"] = edit_user
                        df.loc[row_idx, "Portal Password"] = edit_pass
                        df.loc[row_idx, "Application Date"] = edit_app_date.strftime("%Y/%m/%d") if edit_app_date else ""
                        df.loc[row_idx, "Submission Status"] = edit_status
                        df.loc[row_idx, "Appointment Date"] = edit_slot.strftime("%Y/%m/%d") if edit_slot else ""
                        df.loc[row_idx, "Handled By"] = edit_handled
                        df.loc[row_idx, "Branch Location"] = edit_branch
                        
                        if 'select_label' in df.columns:
                            df = df.drop(columns=['select_label'])
                            
                        save_data(df)
                        st.success(f"Successfully updated details for {edit_name}!")
                        st.rerun()
                    else:
                        st.error("Please fill all the mandatory (*) fields.")
    else:
        st.info("No data available to edit. Add an applicant first!")

st.write("---")

if 'select_label' in df.columns:
    df = df.drop(columns=['select_label'])

# Master Data Table Section
st.subheader("🔍 Master Data View & Excel Export")

search_query = st.text_input("Quick Search (Search by Name, DS-160, Staff or Branch):", "")

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

if not display_df.empty:
    st.dataframe(display_df, use_container_width=True)
    
