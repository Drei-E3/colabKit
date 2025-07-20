# pages/2_Project_Browser.py
import streamlit as st
import json
from utils.drive_helper import (
    ensure_config_folder,
    list_config_files,
    delete_drive_file,
    get_folder_id_from_path, 
    get_notebook_id_in_folder
)

st.title("📁 Project Browser")
if "root_rows" not in st.session_state:
    st.session_state["root_rows"] = [
        {"key": "project name", "type": "normal", "value": ""},
        {"key": "colab path", "type": "normal", "value": ""},
        {"key": "gdrive path", "type": "normal", "value": ""},
        {"key": "description", "type": "normal", "value": ""},
    ]

# Require login
if "drive" not in st.session_state:
    st.warning("Please login and initialize workspace first on the Home page.")
    st.stop()

drive = st.session_state.drive

# Load all project configs
st.session_state.projects = list_config_files(drive)

if not st.session_state.projects:
    st.info("No project config found. Go to Create Config page to start.")
    st.stop()

# Display projects
for proj in st.session_state.projects:
    st.subheader(f"📂 {proj['filename']}")
    config = proj.get("config", {})
    
    project_name = config.get("project name", proj['filename'].replace('.conf', ''))
    gdrive_path = config.get("gdrive path", "")  # like "/MyDrive/Colab Notebooks/ProjectFolder"

    folder_id = get_folder_id_from_path(drive, gdrive_path)
    notebook_name = f"{project_name}.ipynb"
    notebook_id = get_notebook_id_in_folder(drive, folder_id, notebook_name) if folder_id else None
    
    if config:
        st.json(config)
    else:
        st.error("❌ Could not parse config.")

    if notebook_id:
        colab_url = f"https://colab.research.google.com/drive/{notebook_id}"
        st.markdown(f"[🚀 New Notebook in Colab]({colab_url})", unsafe_allow_html=True)
    else:
        st.warning("⚠️ No notebook found in project folder.")
    if folder_id:
        folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
        st.markdown(f"[📂 Open Project Folder in Google Drive]({folder_url})", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button(f"✏️ Edit {proj['filename']}"):
            st.session_state.editing_project = proj
            st.rerun()
    with col2:
        if st.button(f"🗑️ Delete {proj['filename']}"):
            if st.confirm(f"Are you sure you want to delete '{proj['filename']}'?"):
                try:
                    delete_drive_file(drive, proj["id"])
                    st.success(f"✅ Deleted '{proj['filename']}' successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Delete failed: {e}")
    st.markdown("---")

# Editor for selected project
if "editing_project" in st.session_state:
    proj = st.session_state.editing_project
    st.header(f"Editing Config: {proj['filename']}")

    raw_json = json.dumps(proj.get("config", {}), indent=4)
    edited_text = st.text_area("Edit JSON Config", raw_json, height=300)

    if st.button("💾 Save Changes"):
        try:
            new_config = json.loads(edited_text)
            file = drive.CreateFile({'id': proj['id']})
            file.SetContentString(json.dumps(new_config, indent=2))
            file.Upload()

            st.success("✅ Saved successfully!")
            st.session_state.editing_project = None
            st.rerun()
        except Exception as e:
            st.error(f"❌ Save failed: {e}")

    if st.button("Cancel"):
        st.session_state.editing_project = None
        st.rerun()