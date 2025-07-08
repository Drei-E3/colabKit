# utils/notebook_utils.py

import os
import shutil
from datetime import datetime

TEMPLATE_DIR = "notebook_templates"

def generate_notebook(project_name, target_path, template_name="notebook_template.ipynb"):
    os.makedirs(target_path, exist_ok=True)
    src = os.path.join(TEMPLATE_DIR, template_name)
    dest = os.path.join(target_path, f"{project_name}.ipynb")
    shutil.copyfile(src, dest)

    return {
        "name": f"{project_name}.ipynb",
        "path": dest,
        "created_at": datetime.now().isoformat(),
        "link": f"https://colab.research.google.com/drive/your_drive_file_id"  # Optional: Fill in actual Drive ID after upload
    }