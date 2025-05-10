
import streamlit as st

def split_outline_to_paragraphs(outline_text):
    parts = [p.strip() for p in outline_text.split("\n") if p.strip()]
    return parts

def init_session_state():
    if "paragraphs" not in st.session_state:
        st.session_state["paragraphs"] = []
    if "current_index" not in st.session_state:
        st.session_state["current_index"] = 0
    if "drafts" not in st.session_state:
        st.session_state["drafts"] = {}

def get_full_draft():
    if "paragraphs" not in st.session_state:
        return ""
    combined = []
    for i, p in enumerate(st.session_state["paragraphs"]):
        draft = st.session_state["drafts"].get(f"draft_{i}", "").strip()
        paragraph_title = f"【段落 {i+1}】{p[:30]}..." if len(p) > 30 else f"【段落 {i+1}】"
        content = draft if draft else "(尚未創作)"
        combined.append(f"{paragraph_title}\n{content}\n")
    return "\n".join(combined)

def get_draft_status(i):
    key = f"draft_{i}"
    draft = st.session_state["drafts"].get(key, "").strip()
    if draft:
        return "🟢"  # 已完成
    else:
        return "⚪"  # 尚未撰寫
