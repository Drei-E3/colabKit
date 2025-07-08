import streamlit as st
from utils.config_handler import save_config
from utils.drive_browser import drive_folder_picker
from utils.drive_helper import authenticate_drive, ensure_config_folder

# Set up the page configuration
st.set_page_config(
    page_title="ColabKit - Create Project Config",
    page_icon="🔧",
    layout="wide",
    menu_items={
        "About": "A visual tool to simplify Colab project setup and config management."
    }
)       

# show flash message if exists (after redirect)
if "flash_message" in st.session_state:
    st.success(st.session_state.flash_message)
    del st.session_state["flash_message"]  

# -- Page title and description
st.title("🔧 Create New Project Config")

if "drive" not in st.session_state:
    st.warning("Please login to Google Drive first.")
    st.stop()


project = st.text_input("Project Name")
path = st.text_input("Project Path (e.g. /MyDrive/Colab Notebooks/ProjX)")
token = st.text_input("API Token", type="password")

extra_keys = {}
if st.checkbox("Add extra keys"):
    with st.expander("Add custom config keys"):
        for i in range(3):
            key = st.text_input(f"Key {i+1}", key=f"key_{i}")
            val = st.text_input(f"Value {i+1}", key=f"val_{i}")
            if key:
                extra_keys[key] = val

if st.button("💾 Save Config"):
    save_config(project, path, token, extra_keys)
    st.success(f"Saved config for project `{project}`.")