
def suggest_boosters(paragraph_outline):
    suggestions = []

    if "退婚" in paragraph_outline or "羞辱" in paragraph_outline:
        suggestions.append("插入打臉情節：主角反將前未婚妻一軍，展示實力")
    if "重生" in paragraph_outline or "記憶" in paragraph_outline:
        suggestions.append("添加金手指：前世知識 + 現世系統雙加持")
    if "修仙" in paragraph_outline or "門派" in paragraph_outline:
        suggestions.append("設計法寶：主角獲得失傳古劍或靈根覺醒")
    if "系統" in paragraph_outline:
        suggestions.append("提升節奏：任務觸發 → 屬性暴漲 → 戰力碾壓")
    if "凡人" in paragraph_outline:
        suggestions.append("升級出身設定：主角其實是隱世強者後代 / 真命天子")

    if not suggestions:
        suggestions.append("加入高潮：反派登場、意外變故、戀情轉折")

    return suggestions
