# utils/drive_browser.py

import streamlit as st
from pydrive2.drive import GoogleDrive


def get_subfolders(drive: GoogleDrive, parent_id: str):
    """List subfolders under a given folder ID."""
    query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    folder_list = drive.ListFile({'q': query}).GetList()
    return folder_list

def get_folder_name(drive: GoogleDrive, folder_id: str) -> str:
    """Get folder name by ID."""
    try:
        file = drive.CreateFile({'id': folder_id})
        file.FetchMetadata(fields='title')
        return file['title']
    except:
        return "[Unknown Folder]"

def drive_folder_picker(drive: GoogleDrive,render_id_drive_folder_picker , start_id: str = "root", label: str = "📂 Browse Drive Folders",):
    """
    Interactive folder browser. Returns selected folder path and ID.
    """
    
    render_id_drive_folder_picker = render_id_drive_folder_picker
    if "folder_stack" not in st.session_state:
        st.session_state.folder_stack = [start_id]  # Stack of folder IDs
    if "state" not in st.session_state:
        st.session_state["state"] = {}
        
        
    current_folder_id = st.session_state.folder_stack[-1]
    current_folder_name = get_folder_name(drive, current_folder_id)

    st.markdown(f"**Current Folder:** `/{'/'.join([get_folder_name(drive, fid) for fid in st.session_state.folder_stack])}`")

    subfolders = get_subfolders(drive, current_folder_id)
    
    def clean_folder_label(name, max_len=25):
        return (name[:max_len] + '...') if len(name) > max_len else name
    
    col_a, col_b = st.columns(2)

    def format_folder_label(title: str, max_length: int = 25) -> str:
        plain = f"📁 {title}"
        if len(plain) > max_length:
            return plain[:max_length - 3] + "..."
        else:
            return plain.ljust(max_length)

    for idx, folder in enumerate(subfolders):
        label = format_folder_label(folder['title'])

        if idx % 2 == 0:
            with col_a:
                if st.button(label, key=folder['id']):
                    st.session_state.folder_stack.append(folder['id'])
                    st.rerun()
        else:
            with col_b:
                if st.button(label, key=folder['id']):
                    st.session_state.folder_stack.append(folder['id'])
                    st.rerun()

    # ：Go Back | Create Folder | Select This Folder
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔙 Go Back"):
            if len(st.session_state.folder_stack) > 1:
                st.session_state.folder_stack.pop()
                st.rerun()
            else:
                st.warning("You are already at the root folder.")

    with col2:
        with st.popover("📁 Create Folder"):
            new_folder_name = st.text_input("Folder name", key="new_folder_input")
            if st.button("➕ Create", key="create_folder_btn") and new_folder_name.strip():
                new_folder = drive.CreateFile({
                    'title': new_folder_name.strip(),
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [{'id': current_folder_id}]
                })
                new_folder.Upload()
                st.rerun()

    with col3:
        selected = st.button("✅ Select This Folder")
        if selected:
            selected_id = current_folder_id
            selected_path = " / ".join([get_folder_name(drive, fid) for fid in st.session_state.folder_stack])
            return selected_path, selected_id
    
    st.session_state["state"][render_id_drive_folder_picker] = "rendered"
    return None, None