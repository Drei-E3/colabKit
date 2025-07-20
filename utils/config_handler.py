# utils/config_handler.py
# This module handles reading and writing project configurations
import os, json

def save_config(project, path, token, extras={}):
    conf = {"project": project, "path": path, "token": token}
    conf.update(extras)
    os.makedirs(".config", exist_ok=True)
    with open(f".config/{project}.conf", "w") as f:
        json.dump(conf, f, indent=4)

def load_config(project):
    with open(f".config/{project}.conf", "r") as f:
        return json.load(f)

def list_configs():
    return [f.split(".")[0] for f in os.listdir(".config") if f.endswith(".conf")]

def list_project_configs(drive, config_folder_id):
    file_list = drive.ListFile({
        'q': f"'{config_folder_id}' in parents and trashed=false and mimeType='application/json'"
    }).GetList()

    projects = []
    for f in file_list:
        f.GetContentFile(f"/tmp/{f['title']}")
        try:
            with open(f"/tmp/{f['title']}", "r") as json_file:
                import json
                config_data = json.load(json_file)
                projects.append({
                    "filename": f['title'],
                    "config": config_data,
                    "drive_link": f['alternateLink'],
                    "id": f['id']
                })
        except Exception as e:
            projects.append({
                "filename": f['title'],
                "config": {},
                "error": str(e)
            })
    return projects