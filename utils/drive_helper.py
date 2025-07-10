import streamlit as st
import json
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

@st.cache_resource
def authenticate_drive():
    """Authenticate and return Google Drive client."""
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive

def ensure_config_folder(drive):
    """
    Ensure 'Colab Notebooks' and '.config' folders exist in root of Drive.
    Return the folder ID of '.config'.
    """
    # Helper: find or create folder by name under parent_id
    def get_or_create_folder(name, parent_id='root'):
        query = f"title='{name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
        file_list = drive.ListFile({'q': query}).GetList()
        if file_list:
            return file_list[0]['id']
        folder_metadata = {'title': name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [{'id': parent_id}]}
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        return folder['id']

    colab_id = get_or_create_folder('Colab Notebooks')
    config_id = get_or_create_folder('.config', colab_id)
    return config_id

def list_config_files(drive):
    """
    List all JSON config files under the '.config' folder in 'Colab Notebooks'.
    Return list of dict: {id, filename, config (json dict)}.
    """
    config_folder_id = ensure_config_folder(drive)
    query = f"'{config_folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()
    configs = []
    for file in file_list:
        try:
            content = file.GetContentString()
            config = json.loads(content)
        except Exception:
            config = None
        configs.append({
            'id': file['id'],
            'filename': file['title'],
            'config': config
        })
    return configs

def get_folder_id_from_path(drive, path):
    """
    Given a path like '/MyDrive/Folder1/Folder2' or '/My Drive/Folder1', return folder ID.
    Supports root aliases and common variations.
    Raises FileNotFoundError if any part is not found.
    """
    if not path.startswith('/'):
        raise ValueError("Path must start with '/'")

    # 支持根目录多种别名，忽略大小写和空格
    root_aliases = ['root', 'mydrive', 'my drive', 'google drive', 'gdrive', 'drive']
    parts = path.strip('/').split('/')

    root = parts[0].lower().replace(' ', '')
    if root not in [alias.replace(' ', '') for alias in root_aliases]:
        raise FileNotFoundError(f"Unsupported root folder alias '{parts[0]}'. Supported: {root_aliases}")

    parent_id = 'root'
    for folder_name in parts[1:]:
        folder_name_escaped = folder_name.replace("'", "\\'")
        query = f"title='{folder_name_escaped}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
        folders = drive.ListFile({'q': query}).GetList()
        if not folders:
            raise FileNotFoundError(f"Folder '{folder_name}' not found under parent ID '{parent_id}'")
        parent_id = folders[0]['id']
    return parent_id

def get_notebook_id_in_folder(drive, folder_id, notebook_name):
    """
    Find the file ID of a Colab notebook (.ipynb) by name in a folder.
    """
    # 首先尝试查找Colab专用的MIME类型
    query = f"title='{notebook_name}' and '{folder_id}' in parents and mimeType='application/vnd.google.colaboratory' and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()
    if file_list:
        return file_list[0]['id']
    # 其次尝试查找任意类型
    query = f"title='{notebook_name}' and '{folder_id}' in parents and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()
    if file_list:
        return file_list[0]['id']
    return None

def delete_drive_file(drive, file_id):
    """
    Delete a file by ID.
    """
    file = drive.CreateFile({'id': file_id})
    file.Delete()