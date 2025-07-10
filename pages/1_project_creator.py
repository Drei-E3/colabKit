# pages/1_🔧_Create_Config.py

import streamlit as st
import os
import json
from utils.drive_browser import drive_file_browser
from utils.json_editor import render_editor, build_json

# show flash message if exists (after redirect)
if "flash_message" in st.session_state:
    st.success(st.session_state.flash_message)
    del st.session_state["flash_message"]  

st.title("🔧 Create New Project Config")

if "drive" not in st.session_state:
    st.warning("Please login to Google Drive first.")
    st.stop()

st.markdown("### 📂 Step 1: Select Project Folder from Drive")

# Drive Folder Picker
render_id_drive_folder_picker = 0
folder_path, folder_id = drive_file_browser(st.session_state.drive)

# If user selected a folder, update the editor's "path" value
if folder_path:
    st.success(f"Selected path: {folder_path}")
    # Update path-related fields
    for row in st.session_state["root_rows"]:
        if row["key"] == "colab path":
            row["value"] = f"/content/drive/{folder_path}"
        elif row["key"] == "gdrive path":
            row["value"] = f"/{folder_path}"
        elif row["key"] == "folder id":
            row["value"] = folder_id
            break
    
    if st.session_state["state"][0] == "rendered":
        # Now render the editor only after folder is selected
        st.markdown("---")
        st.markdown("### 🧩 Step 2: Edit Config as JSON")

        render_editor(st.session_state["root_rows"], "root")
        config_data = build_json(st.session_state["root_rows"])

        st.markdown("### 🧾 Final JSON Config")
        st.json(config_data)

        # Save the config to `.config` directory
        if st.button("💾 Save Config to Drive"):
            drive = st.session_state.get("drive")
            if not drive:
                st.error("Google Drive not initialized.")
                st.stop()

            config_folder_name = "Colab Notebooks/.config"

            # Search for existing `.config` folder
            file_list = drive.ListFile({
                'q': f"title='{config_folder_name.split('/')[-1]}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            }).GetList()

            # Locate or create `.config` inside Colab Notebooks
            if file_list:
                config_folder_id = file_list[0]['id']
            else:
                notebooks = drive.ListFile({
                    'q': "title='Colab Notebooks' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                }).GetList()
                if notebooks:
                    parent_id = notebooks[0]['id']
                else:
                    parent_folder = drive.CreateFile({'title': 'Colab Notebooks', 'mimeType': 'application/vnd.google-apps.folder'})
                    parent_folder.Upload()
                    parent_id = parent_folder['id']

                config_folder = drive.CreateFile({
                    'title': '.config',
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [{'id': parent_id}]
                })
                config_folder.Upload()
                config_folder_id = config_folder['id']

            # Prepare filename and check for existence
            project_name = config_data.get("project name", "unnamed_project")
            filename = f"{project_name}.conf"
            existing = drive.ListFile({
                'q': f"'{config_folder_id}' in parents and title='{filename}' and trashed=false"
            }).GetList()

            if existing and not st.session_state.get("overwrite_confirmed", False):
                st.warning(f"A config named `{filename}` already exists.")
                st.session_state["cached_config_data"] = config_data

                if st.button("⚠️ Confirm Overwrite"):
                    st.session_state["overwrite_confirmed"] = True
                else:
                    st.stop()

            config_to_save = st.session_state.get("cached_config_data", config_data)
            file = existing[0] if existing else drive.CreateFile({'title': filename, 'parents': [{'id': config_folder_id}]})
            file.SetContentString(json.dumps(config_to_save, indent=2))
            file.Upload()

            st.session_state["overwrite_confirmed"] = False
            st.success(f"✅ Uploaded `{filename}` to `/MyDrive/Colab Notebooks/.config/`")
            st.session_state.pop("cached_config_data", None)

        # Optional clear all
        if st.button("🧹 Clear Form"):
            st.session_state["root_rows"] = [
                {"key": "project", "type": "normal", "value": ""},
                {"key": "colab path", "type": "normal", "value": ""},
                {"key": "gdrive path", "type": "normal", "value": ""},
                {"key": "description", "type": "normal", "value": ""},
            ]