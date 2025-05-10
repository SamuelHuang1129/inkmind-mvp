import streamlit as st
from utils.trope_engine import load_tropes, generate_prompt
from utils.deepseek_client import call_deepseek
from utils.story_state import init_session_state, split_outline_to_paragraphs, get_full_draft, get_draft_status
from utils.story_helper import suggest_boosters
from utils.character_helper import parse_roles_from_outline
from uuid import uuid4
import json
import re

st.set_page_config(page_title="墨心 InkMind", layout="wide")
st.title("墨心 · AI小說創作編輯")
st.markdown("### 讓每一滴墨水都有靈魂")
st.markdown("---")

tropes = load_tropes()
available_types = list(tropes.keys())

if "outline_text" in st.session_state:
    if "character_cards" not in st.session_state or not st.session_state["character_cards"]:
        parsed = parse_roles_from_outline(st.session_state["outline_text"])
        if parsed:
            st.session_state["character_cards"] = parsed

col1, col2 = st.columns(2)
with col1:
    selected_type = st.selectbox("選擇小說類型", available_types, index=0)
with col2:
    selected_length = st.selectbox("選擇小說長度", ["短篇（3,000字）", "中篇（10,000字）", "長篇（30,000字）"])

if not isinstance(selected_type, str) or selected_type not in tropes:
    st.error("❗ 類型錯誤，請重新選擇")
    st.stop()

st.markdown("#### 根據選擇產生的創作提示")
default_prompt = generate_prompt(tropes, selected_type, selected_length)
custom_prompt = st.text_area("Prompt（可編輯）", value=default_prompt, height=250)

if st.button("🔮 生成故事大綱"):
    with st.spinner("AI 創作中，請稍候..."):
        result = call_deepseek(custom_prompt)
    if isinstance(result, str) and result.startswith("❌"):
        st.error(result)
    else:
        st.session_state["outline_text"] = result
        init_session_state()
        st.session_state["paragraphs"] = split_outline_to_paragraphs(result)
        st.session_state["current_index"] = 0
        parsed = parse_roles_from_outline(result)
        if parsed:
            st.session_state["character_cards"] = parsed
        st.success("✅ 大綱生成完成")

if "outline_text" in st.session_state:
    st.markdown("### 📘 完整故事大綱")
    st.info(st.session_state["outline_text"])

if "paragraphs" in st.session_state:
    st.sidebar.markdown("### 📑 大綱段落")
    for i, para in enumerate(st.session_state["paragraphs"]):
        status = get_draft_status(i)
        if st.sidebar.button(f"{status} 段落 {i+1}", key=f"pbtn_{i}"):
            st.session_state["current_index"] = i

    st.markdown("---")
    idx = st.session_state["current_index"]
    st.markdown(f"### ✏️ 正在創作：段落 {idx+1}")
    st.markdown(f"**提示內容：** {st.session_state['paragraphs'][idx]}")

    draft_key = f"draft_{idx}"
    if draft_key not in st.session_state["drafts"]:
        st.session_state["drafts"][draft_key] = ""

    if st.button("✨ 生成段落文字"):
        with st.spinner("AI 寫作中..."):
            new_text = call_deepseek(st.session_state["paragraphs"][idx])
        if isinstance(new_text, str) and new_text.startswith("❌"):
            st.error(new_text)
        else:
            st.session_state["drafts"][draft_key] = new_text
            st.success("✅ 段落生成完成")

    edit_key = f"edit_{idx}_{uuid4()}"
    new_draft = st.text_area("創作文本（可修改）", value=st.session_state["drafts"].get(draft_key, ""), height=300, key=edit_key)

    if st.button("💾 儲存目前段落"):
        st.session_state["drafts"][draft_key] = new_draft
        st.success("✅ 已儲存段落")

    st.markdown("#### 💡 創作輔助建議")
    for tip in suggest_boosters(st.session_state["paragraphs"][idx]):
        st.info(f"📌 {tip}")

st.markdown("---")
st.markdown("## 🧾 草稿總覽與匯出")
if "drafts" in st.session_state:
    full = get_full_draft()
    with st.expander("展開預覽完整草稿"):
        st.text_area("全文草稿", value=full, height=300)
    st.download_button("📄 匯出為 TXT 檔", file_name="inkmind.txt", data=str(full), mime="text/plain")
    json_data = json.dumps(st.session_state["drafts"], ensure_ascii=False, indent=2)
    st.download_button("📄 匯出為 JSON 檔", file_name="inkmind.json", data=json_data, mime="application/json")

# 角色卡管理區
st.markdown("---")
st.markdown("## 📇 角色卡管理")

if st.button("🔄 重新從大綱提取角色卡", key="reload_roles"):
    parsed = parse_roles_from_outline(st.session_state.get("outline_text", ""))
    if parsed:
        st.session_state["character_cards"] = parsed
        st.success(f"✅ 已重新載入 {len(parsed)} 個角色卡")
    else:
        st.warning("⚠️ 大綱中未解析出角色")

if "character_cards" not in st.session_state or not st.session_state["character_cards"]:
    st.info("目前尚無角色資料，請先生成大綱以初始化角色卡")
else:
    st.markdown("### 🧠 檢視 / 編輯角色卡")
    for name in list(st.session_state["character_cards"].keys()):
        info = st.session_state["character_cards"][name]
        st.markdown(f"#### 🧾 {name}")
        col1, col2 = st.columns([4, 1])
        with col1:
            valid_roles = ["主角", "反派", "配角", "未設定"]
            v = info["定位"].strip()
            if v not in valid_roles:
                v = "未設定"
            role = st.selectbox("角色定位", valid_roles, key=f"role_{name}", index=valid_roles.index(v))
            bg = st.text_input("背景描述", info["背景"], key=f"bg_{name}")
            growth = st.text_area("成長線", info["成長線"], key=f"growth_{name}")
            st.session_state["character_cards"][name] = {
                "定位": role,
                "背景": bg,
                "成長線": growth,
            }
        with col2:
            if st.button("🗑️ 刪除", key=f"del_{name}"):
                del st.session_state["character_cards"][name]
                st.experimental_rerun()

st.markdown("---")
st.markdown("## 📨 匯出角色卡")
if "character_cards" in st.session_state and st.session_state["character_cards"]:
    role_data = json.dumps(st.session_state["character_cards"], ensure_ascii=False, indent=2)
    st.download_button(label="📥 匯出為 JSON 檔",data=role_data, file_name="roles.json",mime="application/json")
else:
    st.info("目前尚未有可匯出的角色卡")