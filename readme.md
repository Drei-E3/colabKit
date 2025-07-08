# ColabKit

> ⚡️A lightweight tool to simplify Google Colab project setup, hide sensitive tokens, and manage project configurations with ease.

---

## ✨ What is ColabKit?

**ColabKit** is a lightweight [Streamlit](https://streamlit.io/) web app that helps you manage your Google Colab projects in a clean and secure way. It allows you to:

- Configure project paths and API tokens via UI
- Generate `.conf` files in JSON format
- Create Colab-ready notebooks from a template
- Browse, edit, and launch existing projects stored on Google Drive
- Securely manage sensitive credentials (e.g., API keys, tokens) outside of the notebook
- Use the same configuration across both Colab and Jupyter environments
- Seamlessly interact with Google Drive using [PyDrive2](https://github.com/iterative/PyDrive2)

---

## 📦 Key Features

- ✅ Web UI form to enter project name, path, and tokens
- ✅ Save configurations as `.conf` (JSON)
- ✅ Automatically create a project folder with a pre-filled notebook template
- ✅ One-click upload to Google Drive (OAuth 2.0 via PyDrive2)
- ✅ Clean, beginner-friendly interface
- ✅ 🔍 **Browse all existing Colab projects in `.config/`**
- ✅ 📁 **Visualize project folder structure in Google Drive**
- ✅ ✏️ **Edit config files or create new documents/folders directly**
- ✅ 🚀 **One-click launch of Colab notebooks from your Drive**

---

## 📂 Project Structure Example

```
My Drive/
└── Colab Notebooks/
│   └── .config/
│       ├── MyNLPProject.conf
│       └── VisionProject.conf
├── MyNLPProject/
│   └── MyNLPProject.ipynb
└── VisionProject/
    └── VisionProject.ipynb
```

Each `.conf` file defines:
```
{
  "project name": "MyNLPProject",
  "colab path": "/MyDrive/Colab Notebooks/MyNLPProject",
  "gdrive path": "/My Drive / ", // actually the name of My Drive is "root"
  "secrets":{
    "openai_key": "..." // only an example, optional
  }
  
}

```

---

## 🔧 How to deploy


1. Clone the repository

git clone https://github.com/yourusername/colabkit.git
cd colabkit

2. Install dependencies

pip install -r requirements.txt

3. Run the app

streamlit run app.py

---

## 🧪 Try It Online

You can deploy it to Streamlit Community Cloud or run locally. For Colab integration, upload your config and notebooks to Google Drive and access them via drive.mount().

--- 

## 📁 Example Colab Snippet (in generated notebook)
generate colab notebook using the App which automatically including:

```
try:
  from google.colab import drive
  import json

  drive.mount('/content/drive')
  config_path = "/content/drive/MyDrive/Colab Notebooks/.config/MyNLPProject.conf"

  with open(config_path, 'r') as f:
      config = json.load(f)

  %cd {config['colab path']}
```
you can create any jupyter / colab notebook templates.
This approach lets you share notebooks without exposing secrets and cooperate with non colab env. Only the config file (outside notebook) contains API keys and tokens. This app allows you to place your project anywhere in GDrive and manage them in one place.

--- 

🚧 Roadmap
- [x] Project creation + config editing  
- [x] Drive integration  
- [x] Project browser with config inspector  
- [x] File explorer viewer  
- [ ] One-click Colab launch  
- [ ] Add encryption encoder and decoder for sensitive keys  
- [ ] Add notebook preview and file versioning  

---

🤝 Contributing

PRs welcome! If you want to add features like encryption, project templates, or Drive sync improvements, feel free to fork and submit a pull request.

---

📄 License Open Source

Apache 2.0 License © 2025 Zeming Leng & tinfant

--- 