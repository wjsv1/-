import streamlit as st
import dashscope
from dashscope import Application
import uuid

# ================= 配置区域 =================
# 从 Streamlit Cloud 的 Secrets 中读取 API Key (安全做法)
# 如果本地测试没有 secrets，可以暂时在这里硬编码，但提交到 GitHub 前请务必删除硬编码部分！
try:
    api_key = st.secrets["DASHSCOPE_API_KEY"]
except KeyError:
    st.error("❌ 未在 Secrets 中找到 API Key。请在 Streamlit Cloud 后台配置 DASHSCOPE_API_KEY。")
    st.stop()

dashscope.api_key = api_key
APP_ID = "570b427c5af24869b40b18492588925d" # 你的应用 ID
# ===========================================

st.set_page_config(page_title="中南大学小南助手", page_icon="🎓")

st.title("🎓 中南大学小南助手")
st.caption("基于阿里云百炼打造的智能问答 Agent")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 处理用户输入
if prompt := st.chat_input("请输入您的问题..."):
    # 1. 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. 调用百炼 API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            with st.spinner("小南正在思考..."):
                response = Application.call(
                    app_id=APP_ID,
                    prompt=prompt,
                    session_id=st.session_state.session_id  # 保持多轮对话记忆
                )
            
            if response.status_code == 200:
                full_response = response.output.text
                message_placeholder.markdown(full_response)
            else:
                error_msg = f"⚠️ 请求失败: {response.code} - {response.message}"
                message_placeholder.error(error_msg)
                full_response = error_msg
                
        except Exception as e:
            error_msg = f"💥 系统错误: {str(e)}"
            message_placeholder.error(error_msg)
            full_response = error_msg

    # 3. 保存助手回复
    st.session_state.messages.append({"role": "assistant", "content": full_response})
