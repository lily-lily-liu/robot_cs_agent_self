from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from agent.react_agent import ReactAgent


st.set_page_config(
    page_title="扫地机器人智能客服",
    page_icon="🤖",
    layout="centered",
)

st.markdown(
    """
    <style>
    .block-container { max-width: 860px; padding-top: 2rem; }
    [data-testid="stChatMessage"] { padding: .6rem 0; }
    .source-title { color: #64748b; font-size: .82rem; margin-top: .6rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_agent() -> ReactAgent:
    return ReactAgent()


def render_sources(sources: list[dict[str, Any]]) -> None:
    """Render unique source files and the exact retrieved chunks."""
    if not sources:
        return
    unique_sources = list(
        dict.fromkeys(str(item.get("source", "未知文件")) for item in sources)
    )
    st.markdown(
        f'<div class="source-title">引用 {len(unique_sources)} 个知识库文件</div>',
        unsafe_allow_html=True,
    )
    with st.expander("查看引用", expanded=False):
        for index, source in enumerate(unique_sources, start=1):
            st.markdown(f"**{index}. {Path(source).name}**")
            for item in sources:
                if str(item.get("source", "")) == source:
                    chunk = item.get("chunk")
                    label = (
                        f"第 {chunk + 1} 个片段"
                        if isinstance(chunk, int)
                        else "检索片段"
                    )
                    st.caption(label)
                    excerpt = str(item.get("content", "")).replace("\n", "  \n")
                    st.markdown(f"> {excerpt}")


st.title("扫地机器人智能客服")
st.caption("基于知识库回答，简洁、准确，并保留可追溯引用。")

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.sidebar.button("清空对话"):
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_sources(message.get("sources", []))

if prompt := st.chat_input("请输入您的问题…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            agent = get_agent()
            with st.spinner("思考中…"):
                result = agent.execute_with_sources(prompt)
            response = str(result["answer"])
            st.markdown(response)
            render_sources(result.get("sources", []))
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response,
                    "sources": result.get("sources", []),
                }
            )
        except Exception as error:
            st.error(f"出错了：{error}")
