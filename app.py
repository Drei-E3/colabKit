# app.py

import streamlit as st
from utils.drive_oauth import (
    get_authorization_url,
    exchange_code_for_tokens,
    get_drive_service)
from utils.drive_helper import ensure_config_folder,list_config_files
from utils.config_handler import list_project_configs

st.set_page_config(
    page_title="ColabKit",
    page_icon="🗂️",
    layout="wide",
    menu_items={
        "About": "A visual tool to simplify Colab project setup and config management."
    }
)

st.title("⚡️ ColabKit")
st.markdown("""
Welcome to **ColabKit** – a lightweight tool for managing Google Colab projects with configuration files, sensitive token hiding, and one-click notebook generation.
""")

# -- Google Drive Login Section --
st.subheader("🔐 Google Drive Login")

if "drive_service" not in st.session_state:
    auth_url = get_authorization_url()
    st.markdown(f"[🔗 Click here to authorize with Google Drive]({auth_url})")

    code = st.text_input("Paste the authorization code here:")
    if st.button("🔐 Submit Code") and code:
        with st.spinner("Exchanging code for tokens..."):
            try:
                token_dict = exchange_code_for_tokens(code)
                drive_service = get_drive_service(token_dict)
                st.session_state.drive_service = drive_service
                st.success("✅ Google Drive connected successfully!")
            except Exception as e:
                st.error(f"❌ Failed to connect: {e}")
else:
    st.success("✅ You are already connected to Google Drive.")
    
# -- init button --
if "drive_service" in st.session_state:
    if st.button("🔄 Initialize Workspace"):
        with st.spinner("Initializing..."):
            drive_service = st.session_state.drive_service
            config_folder_id = ensure_config_folder(drive_service)
            st.session_state.config_folder_id = config_folder_id
            projects = list_config_files(drive_service)
            st.session_state.projects = projects

        if len(projects) == 0:
            st.warning("No configuration files found. Redirecting...")
            st.session_state["flash_message"] = "No configuration files found. create a new project."
            st.switch_page("pages/1_project_creator.py")
        else:
            st.success(f"✅ Initialization complete. A total of {len(projects)} project configuration files were found.")
            for proj in projects:
                st.markdown(f"- 📁 **{proj['filename']}** -")
            st.success("You can now browse your projects or create a new one using the sidebar.")  

# -- Features Overview --
st.markdown("---")
st.subheader("🚀 What you can do")

st.markdown("""
- 🔧 **Create and save project configs** with paths and API tokens  
- 📁 **Browse your existing Colab projects** in Google Drive `.config/`  
- 📓 **Generate notebooks from templates**, saved into your Drive  
- 🔐 **Hide sensitive info (tokens, passwords)** securely outside notebooks  
- 🌐 **Seamlessly switch between Colab and Jupyter environments**
""")

st.info("👉 Use the **left sidebar** to navigate between features.")