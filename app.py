import streamlit as st
import json
from uuid import uuid4
from pathlib import Path
import streamlit.components.v1 as components
from utils.trope_engine import load_tropes, generate_prompt
from utils.deepseek_client import call_deepseek
from utils.story_state import init_session_state, split_outline_to_paragraphs, get_full_draft, get_draft_status
from utils.story_helper import suggest_boosters
from utils.character_helper import parse_roles_from_outline
from utils.interaction_parser import update_interactions

st.set_page_config(page_title="墨心 InkMind", layout="wide")
st.title("墨心 · AI小說創意編輯管理")
st.markdown("### 讓每一滴墨水都有靈魂")
st.markdown("---")

tropes = load_tropes()
available_types = list(tropes.keys())

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
        st.session_state["interactions"] = update_interactions(
            st.session_state["paragraphs"],
            st.session_state["character_cards"]
        )
        try:
            from utils.plot_helper import generate_character_interaction_graph
            fig = generate_character_interaction_graph(
    st.session_state["interactions"],
    st.session_state["character_cards"]
)
            fig.write_html("static/interaction_graph.html")
        except Exception as e:
            st.warning(f"互動圖生成失敗：{e}")
        st.success("✅ 大綱生成完成")

# 正確三欄佈局
left, center, right = st.columns([1, 3, 2])

with left:
    if "paragraphs" in st.session_state:
        st.markdown("### 📑 段落選擇")
        for i, para in enumerate(st.session_state["paragraphs"]):
            status = get_draft_status(i)
            if st.button(f"{status} 段落 {i+1}", key=f"pbtn_{i}"):
                st.session_state["current_index"] = i

with center:
    if "outline_text" in st.session_state:
        st.markdown("### 📘 AI 產生的大綱（供創作參考）")
        st.info(st.session_state["outline_text"])

    
    if "paragraphs" in st.session_state:
        idx = st.session_state.get("current_index", 0)
        current_outline = st.session_state["paragraphs"][idx]

        st.markdown(f"### ✏️ 正在創作：段落 {idx+1}")
        with st.expander("🧭 對應大綱提示", expanded=True):
            st.markdown(current_outline)

        draft_key = f"draft_{idx}"
        if draft_key not in st.session_state["drafts"]:
            st.session_state["drafts"][draft_key] = ""

        if st.button("✨ 生成段落文字"):
            with st.spinner("AI 寫作中..."):
                new_text = call_deepseek(f"請根據以下提示寫一段小說文字：\n{current_outline}")
            if isinstance(new_text, str) and new_text.startswith("❌"):
                st.error(new_text)
            else:
                st.session_state["drafts"][draft_key] = new_text
                st.success("✅ 段落生成完成")

        edit_key = f"edit_{idx}_{uuid4()}"
        new_draft = st.text_area("創作文本（可修改）", value=st.session_state["drafts"].get(draft_key, ""), height=300, key=edit_key)

        if st.button("💾 儲存目前段落"):
            st.session_state["drafts"][draft_key] = new_draft
            st.success("✅ 已儲存段落！")
            st.session_state["interactions"] = update_interactions(
                list(st.session_state["drafts"].values()),
                st.session_state["character_cards"]
            )

        st.markdown("#### 💡 創作輔助建議")
        for tip in suggest_boosters(current_outline):
            st.info(f"📌 {tip}")

with right:
    st.markdown("### 🧑‍🤝‍🧑 角色互動摘要")
    if "interactions" in st.session_state:
        pairs = st.session_state["interactions"].get("pairs", {})
        top_pairs = sorted(pairs.items(), key=lambda x: x[1]["count"], reverse=True)[:5]
        for (a, b), info in top_pairs:
            st.markdown(f"- **{a} × {b}**：{info['count']} 次，`{info['type']}` (avg {info['avg_sentiment']})")

    st.markdown("---")
    st.markdown("### 📇 角色卡管理")
    if "character_cards" in st.session_state:
        for name in list(st.session_state["character_cards"].keys()):
            info = st.session_state["character_cards"][name]
            st.markdown(f"#### 🧾 {name}")
            role = st.selectbox("角色定位", ["主角", "反派", "配角", "未設定"], index=["主角", "反派", "配角", "未設定"].index(info["定位"]), key=f"role_{name}")
            bg = st.text_input("背景描述", info["背景"], key=f"bg_{name}")
            growth = st.text_area("成長線", info["成長線"], key=f"growth_{name}")
            st.session_state["character_cards"][name] = {
                "定位": role,
                "背景": bg,
                "成長線": growth,
            }
            if st.button("🗑️ 刪除", key=f"del_{name}"):
                del st.session_state["character_cards"][name]

                st.session_state["interactions"] = update_interactions(
                    list(st.session_state["drafts"].values()),
                    st.session_state["character_cards"]
                )
                st.stop()
    else:
        st.info("目前尚無角色資料")

    st.markdown("### 📊 角色互動頻譜圖")
    graph_path = Path("static/interaction_graph.html")
    if graph_path.exists():
        components.html(graph_path.read_text(encoding="utf-8"), height=600, scrolling=True)
    else:
        st.info("尚未生成互動圖")

# 匯出功能區
st.markdown("---")
st.markdown("## 🧾 草稿總覽與匯出")

if "drafts" in st.session_state and st.session_state["drafts"]:
    full_text = get_full_draft()
    with st.expander("展開預覽完整草稿"):
        st.text_area("全文草稿", value=full_text, height=300)
    st.download_button("📄 匯出為 TXT 檔", data=full_text, file_name="inkmind.txt", mime="text/plain")
    json_data = json.dumps(st.session_state["drafts"], ensure_ascii=False, indent=2)
    st.download_button("📄 匯出為 JSON 檔", data=json_data, file_name="inkmind_drafts.json", mime="application/json")

st.markdown("## 📨 匯出角色卡")
if "character_cards" in st.session_state and st.session_state["character_cards"]:
    role_data = json.dumps(st.session_state["character_cards"], ensure_ascii=False, indent=2)
    st.download_button("📥 匯出為 JSON 檔", data=role_data, file_name="roles.json", mime="application/json")
else:
    st.info("目前尚未有可匯出的角色卡")