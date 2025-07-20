# utils/drive_browser.py
# This module provides utilities for browsing Google Drive files and folders
# It uses Streamlit's file browser component to allow users to select folders
# and returns the selected folder path and ID.
import os
import streamlit as st
from streamlit_file_browser import st_file_browser

def path_to_title(path_chain):
    return " › ".join(folder["title"] for folder in path_chain)

# utils/drive_browser.py

import streamlit as st
from streamlit_file_browser import st_file_browser

def drive_file_browser(drive, key="gdrive_picker", start_id="root"):
    if key not in st.session_state:
        st.session_state[key] = {
            "chain": [{"id": start_id, "title": "MyDrive"}],
            "selected_id": None
        }

    state = st.session_state[key]
    chain = state["chain"]
    current = chain[-1]

    # 面包屑
    st.markdown("📁 **Path:** " + " / ".join([c["title"] for c in chain]))

    # 当前层所有内容
    query = f"'{current['id']}' in parents and trashed=false"
    items = drive.ListFile({'q': query}).GetList()

    # 构造结构
    files = []
    for item in items:
        files.append({
            "name": item["title"],
            "type": "directory" if item["mimeType"] == "application/vnd.google-apps.folder" else "file",
            "metadata": {"id": item["id"]}
        })

    event = st_file_browser(
        path=files,
        key=key,
        show_choose_folder=True,
        show_choose_file=False,
        show_upload_file=False,
        show_new_folder=False,
        show_delete_file=False,
        show_rename_folder=False
    )

    if event:
        if event["type"] == "directory":
            state["chain"].append({"id": event["metadata"]["id"], "title": event["name"]})
            st.experimental_rerun()

    # 返回完整路径和当前文件夹ID
    full_path = "/".join([c["title"] for c in chain[1:]]) 
    print(f"Current folder path: {full_path}")
    return full_path, current["id"]