import streamlit as st
import json
from googleapiclient.discovery import Resource

def ensure_config_folder(service: Resource):
    """
    Ensure 'Colab Notebooks' and '.config' folders exist in root of Drive.
    Return the folder ID of '.config'.
    """
    def get_or_create_folder(name, parent_id='root'):
        query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{name}' and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']

        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        file = service.files().create(body=file_metadata, fields='id').execute()
        return file['id']

    colab_id = get_or_create_folder('Colab Notebooks')
    config_id = get_or_create_folder('.config', colab_id)
    return config_id

def list_config_files(service: Resource):
    config_folder_id = ensure_config_folder(service)
    query = f"'{config_folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    configs = []
    for file in files:
        try:
            content = service.files().get_media(fileId=file['id']).execute().decode('utf-8')
            config = json.loads(content)
        except Exception:
            config = None
        configs.append({
            'id': file['id'],
            'filename': file['name'],
            'config': config
        })
    return configs

def get_folder_id_from_path(service: Resource, path: str):
    if not path.startswith('/'):
        raise ValueError("Path must start with '/'")

    root_aliases = ['root', 'mydrive', 'my drive', 'google drive', 'gdrive', 'drive']
    parts = path.strip('/').split('/')

    root = parts[0].lower().replace(' ', '')
    if root not in [alias.replace(' ', '') for alias in root_aliases]:
        raise FileNotFoundError(f"Unsupported root folder alias '{parts[0]}'.")

    parent_id = 'root'
    for name in parts[1:]:
        query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{name}' and trashed=false"
        result = service.files().list(q=query, fields="files(id, name)").execute()
        files = result.get('files', [])
        if not files:
            raise FileNotFoundError(f"Folder '{name}' not found under parent ID '{parent_id}'")
        parent_id = files[0]['id']
    return parent_id

def get_notebook_id_in_folder(service: Resource, folder_id: str, notebook_name: str):
    query = f"'{folder_id}' in parents and name='{notebook_name}' and mimeType='application/vnd.google.colaboratory' and trashed=false"
    result = service.files().list(q=query, fields="files(id)").execute()
    files = result.get('files', [])
    if files:
        return files[0]['id']
    
    # fallback