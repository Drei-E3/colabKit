# utils/drive_helper.py

import os
import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import json


@st.cache_resource(show_spinner=False)
def authenticate_drive():
    import json
    client_config = {"web": dict(st.secrets["web"])}
    secrets_path = "/tmp/client_secrets.json"

    with open(secrets_path, "w") as f:
        json.dump(client_config, f)

    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(secrets_path)
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive

def list_configs(drive):
    file_list = drive.ListFile({
        'q': f"'{get_config_folder_id(drive)}' in parents and trashed=false and mimeType='application/json'"
    }).GetList()
    return [f['title'] for f in file_list]

def get_config_folder_id(drive):
    file_list = drive.ListFile({
        'q': "title = '.config' and mimeType = 'application/vnd.google-apps.folder' and trashed=false"
    }).GetList()
    if file_list:
        return file_list[0]['id']
    else:
        folder = drive.CreateFile({'title': '.config', 'mimeType': 'application/vnd.google-apps.folder', 'parents': [{'id': get_colab_notebooks_id(drive)}]})
        folder.Upload()
        return folder['id']

def get_colab_notebooks_id(drive):
    colab_folders = drive.ListFile({
        'q': "title contains 'Colab Notebooks' and mimeType = 'application/vnd.google-apps.folder' and trashed=false"
    }).GetList()
    return colab_folders[0]['id'] if colab_folders else 'root'

def load_config(drive, filename):
    file_list = drive.ListFile({
        'q': f"title = '{filename}' and '{get_config_folder_id(drive)}' in parents and trashed=false"
    }).GetList()
    if not file_list:
        return {}
    file = file_list[0]
    file.GetContentFile(f"/tmp/{filename}")
    import json
    with open(f"/tmp/{filename}", 'r') as f:
        return json.load(f)

def show_drive_tree(path, indent=0):
    # This is a stub — replace with actual Google Drive traversal if desired
    st.text("📂 " + "—" * indent + os.path.basename(path))
    # You can optionally implement recursive Drive tree rendering using PyDrive
    
def upload_file(drive, local_path, drive_folder_id, filename=None):
    filename = filename or os.path.basename(local_path)
    file_drive = drive.CreateFile({
        'title': filename,
        'parents': [{'id': drive_folder_id}]
    })
    file_drive.SetContentFile(local_path)
    file_drive.Upload()
    return {
        "title": file_drive['title'],
        "id": file_drive['id'],
        "link": file_drive['alternateLink']
    }

def create_or_get_folder(drive, folder_name, parent_id='root'):
    file_list = drive.ListFile({
        'q': f"title = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
    }).GetList()

    if file_list:
        return file_list[0]['id']
    else:
        folder = drive.CreateFile({
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{'id': parent_id}]
        })
        folder.Upload()
        return folder['id']

def ensure_config_folder(drive):
    # ensure the .config folder exists in the Colab Notebooks directory
    colab_id = create_or_get_folder(drive, "Colab Notebooks", parent_id="root")
    config_id = create_or_get_folder(drive, ".config", parent_id=colab_id)
    return config_id

def delete_drive_file(drive, file_id):
    file = drive.CreateFile({'id': file_id})
    file.Delete()

def list_config_files(drive):
    """Return a list of config files in .config folder with their metadata and parsed JSON"""
    folder_id = ensure_config_folder(drive)
    file_list = drive.ListFile({
        'q': f"'{folder_id}' in parents and trashed=false"
    }).GetList()

    configs = []
    for file in file_list:
        try:
            content = file.GetContentString()
            config_data = json.loads(content)
            configs.append({
                "id": file['id'],
                "filename": file['title'],
                "config": config_data
            })
        except Exception as e:
            st.error(f"Failed to parse {file['title']}: {e}")
    return configs

# utils/drive_helper.py

def get_folder_id_by_path(drive, folder_path):
    """
    Traverse a Google Drive folder path like '/MyDrive/Colab Notebooks/ProjectX'
    and return the folder ID of the last folder.
    """
    parts = folder_path.strip("/").split("/")
    parent_id = 'root'  # start from root
    
    for part in parts:
        # Query folder named `part` under current parent_id
        query = (
            f"title = '{part}' and "
            f"mimeType = 'application/vnd.google-apps.folder' and "
            f"'{parent_id}' in parents and trashed = false"
        )
        file_list = drive.ListFile({'q': query}).GetList()
        if not file_list:
            # Folder not found
            return None
        parent_id = file_list[0]['id']  # descend into this folder
    
    return parent_id


def get_notebook_id_in_folder(drive, folder_id, notebook_name):
    """
    Search for a notebook file by name inside a folder and return its file ID.
    """
    query = (
        f"'{folder_id}' in parents and "
        f"title = '{notebook_name}' and "
        f"mimeType = 'application/vnd.google.colaboratory' and "
        f"trashed = false"
    )
    file_list = drive.ListFile({'q': query}).GetList()
    if file_list:
        return file_list[0]['id']
    else:
        # Sometimes Colab notebooks are saved as Google Docs mimeType
        # Try common notebook mime types as fallback
        alt_query = (
            f"'{folder_id}' in parents and "
            f"title = '{notebook_name}' and "
            f"trashed = false"
        )
        file_list = drive.ListFile({'q': alt_query}).GetList()
        if file_list:
            return file_list[0]['id']
    return None

def build_proj_tree(drive, folder_id):
    """
    递归遍历 Google Drive 文件夹，构建 proj tree 字典结构。
    仅遍历当前文件夹下文件和文件夹，不包括回收站中的文件。
    """
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    proj_tree = {}

    for file in file_list:
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            # 是文件夹，递归处理子文件夹
            children = build_proj_tree(drive, file['id'])
            proj_tree[file['title']] = children
        else:
            # 普通文件，记录基本信息
            proj_tree[file['title']] = {
                "name": file['title'],
                "file id": file['id'],
                "relative path": file['title'],  # 可以改进为相对路径
            }
    return proj_tree


def get_gdrive_path_from_colab_path(colab_path):
    """
    根据 colab path 简单推导 gdrive path。
    这里是示例实现，可以根据你的逻辑调整。
    """
    import os
    if colab_path.startswith("/content/drive/MyDrive/"):
        return colab_path.replace("/content/drive/MyDrive", "/MyDrive")
    return "/gdrive/MyDrive/" + os.path.basename(colab_path.strip("/"))

def get_folder_id_from_path(drive: GoogleDrive, path: str) -> str:
    """
    Given a folder path like '/My Drive / folderA / folderB', return the folder ID.
    """
    parts = [p.strip() for p in path.strip('/').split('/') if p.strip()]
    
    if not parts:
        raise ValueError("Invalid path: empty")

    #  root/My Drive/MyDrive
    root_aliases = {'root', 'my drive', 'mydrive'}
    if parts[0].lower() not in root_aliases:
        raise ValueError("Path must start with 'root', 'My Drive', or 'MyDrive'")

    parent_id = 'root'
    for folder_name in parts[1:]:
        query = (
            f"'{parent_id}' in parents and "
            f"title = '{folder_name}' and "
            f"mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        )
        folders = drive.ListFile({'q': query}).GetList()

        if not folders:
            raise FileNotFoundError(f"Folder '{folder_name}' not found under parent ID '{parent_id}'")
        
        # Use first match
        parent_id = folders[0]['id']

    return parent_id