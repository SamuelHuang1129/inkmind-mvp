
import streamlit as st
from utils.trope_engine import load_tropes, generate_prompt
from utils.deepseek_client import call_deepseek
from utils.story_state import (
    init_session_state,
    split_outline_to_paragraphs,
    get_full_draft,
    get_draft_status,
)
from utils.story_helper import suggest_boosters
from uuid import uuid4

st.set_page_config(page_title="墨心 InkMind", layout="wide")
st.title("墨心 · AI小說創作原型")
st.markdown("### 讓每一滴墨水都有靈魂")
st.markdown("---")

tropes = load_tropes()

col1, col2 = st.columns(2)
with col1:
    selected_type = st.selectbox("選擇小說類型", list(tropes.keys()))
with col2:
    selected_length = st.selectbox("選擇小說長度", ["短篇（3,000字）", "中篇（10,000字）", "長篇（30,000字）"])

st.markdown("#### 根據選擇產生的創作提示")
default_prompt = generate_prompt(tropes, selected_type, selected_length)
custom_prompt = st.text_area("Prompt（可編輯）", value=default_prompt, height=250)

if st.button("🔮 生成故事大綱"):
    with st.spinner("AI 正在創作中，請稍候..."):
        result = call_deepseek(custom_prompt)
        st.session_state["outline_text"] = result
        st.markdown("#### 🎯 AI 回傳的大綱如下：")
        st.success(result)
        init_session_state()
        st.session_state.paragraphs = split_outline_to_paragraphs(result)
        st.session_state.current_index = 0

# 顯示完整大綱（若存在）
if "outline_text" in st.session_state:
    st.markdown("### 📘 完整故事大綱")
    st.info(st.session_state["outline_text"])

# 段落創作模式
if "paragraphs" in st.session_state and st.session_state["paragraphs"]:
    st.sidebar.markdown("### 📑 大綱段落")
    for i, para in enumerate(st.session_state["paragraphs"]):
        status = get_draft_status(i)
        if st.sidebar.button(f"{status} 段落 {i+1}", key=f"pbtn_{i}"):
            st.session_state.current_index = i

    st.markdown("---")
    idx = st.session_state["current_index"]
    current_outline = st.session_state["paragraphs"][idx]

    st.markdown(f"### ✏️ 正在創作：段落 {idx+1}")
    st.markdown(f"**提示內容：** {current_outline}")

    if f"draft_{idx}" not in st.session_state["drafts"]:
        st.session_state["drafts"][f"draft_{idx}"] = ""

    if st.button("✨ 生成段落文字"):
        with st.spinner("AI 寫作中..."):
            new_text = call_deepseek(f"請根據以下提示寫一段小說文字：\n{current_outline}")
            st.session_state["drafts"][f"draft_{idx}"] = new_text

    text_key = f"edit_{idx}_{str(uuid4())}"
    new_draft = st.text_area("創作文本（可修改）", value=st.session_state["drafts"].get(f"draft_{idx}", ""), height=300, key=text_key)

    if st.button("💾 儲存目前段落"):
        st.session_state["drafts"][f"draft_{idx}"] = new_draft
        st.success("✅ 已儲存段落！")

    st.markdown("#### 💡 建議可插入的創作元素")
    tips = suggest_boosters(current_outline)
    for tip in tips:
        st.info(f"📌 {tip}")

# 草稿總覽與匯出
st.markdown("---")
st.markdown("## 🧾 草稿總覽與匯出")

if "drafts" in st.session_state and st.session_state["paragraphs"]:
    full_draft = get_full_draft()

    with st.expander("📄 展開預覽完整草稿"):
        st.text_area("整篇草稿", value=full_draft, height=400, key="preview_area")

    if st.download_button("📥 匯出為 TXT 檔", file_name="inkmind_draft.txt", mime="text/plain", data=full_draft.encode()):
        st.success("✅ 匯出成功！")

    if st.download_button("📥 匯出為 JSON 檔", file_name="inkmind_draft.json", mime="application/json",
                          data=str(st.session_state["drafts"]).encode()):
        st.success("✅ JSON 已下載")
