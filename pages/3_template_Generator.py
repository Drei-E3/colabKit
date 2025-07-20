# pages/3_template_Generator.py
import streamlit as st
from utils.notebook_utils import generate_notebook

st.title("📓 Notebook template Generator")

project = st.text_input("Project Name")
target_path = st.text_input("Target Folder Path")

if st.button("⚙️ Generate Notebook from Template"):
    result = generate_notebook(project, target_path)
    st.success("Notebook created successfully!")
    st.markdown(f"[📄 Open `{result['name']}`]({result['link']})")