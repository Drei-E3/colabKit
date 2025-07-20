# pages/auth_callback.py
import streamlit as st
from urllib.parse import urlparse, parse_qs
from utils.drive_oauth import exchange_code_for_tokens, get_drive_service

st.set_page_config(layout="wide")

query_params = st.query_params

# 检查URL中是否存在'code'参数
if "code" in query_params:
    auth_code = query_params["code"]
    try:
        tokens = exchange_code_for_tokens(auth_code)
        st.session_state.tokens = tokens
        st.session_state.drive = get_drive_service(tokens)
        st.success("🎉 Google Drive connected successfully!")
        # 清除URL参数，并重定向到主页或项目创建页
        # Streamlit 没有直接的重定向，但可以改变页面状态并rerun
        st.session_state["flash_message"] = "🎉 Google Drive connected successfully!"
        st.experimental_rerun() # This will clear query params implicitly on next load if not explicitly handled
        # Alternatively, use st.write(f'<meta http-equiv="refresh" content="0;URL=/">', unsafe_allow_html=True)
        # to redirect to the home page after processing
    except Exception as e:
        st.error(f"❌ Failed to connect to Google Drive: {e}")
        st.stop() # 停止后续代码执行
elif "error" in query_params:
    st.error(f"❌ Google OAuth error: {query_params['error_description']}")
    st.stop()
else:
    st.info("Waiting for Google Drive authorization...")

# 可以在这里添加一个按钮让用户回到主页
if st.button("Go to Home"):
    st.session_state["flash_message"] = "Returning to Home page."
    st.switch_page("Home.py") # 或者你的主入口文件