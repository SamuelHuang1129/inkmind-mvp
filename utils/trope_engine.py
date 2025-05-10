import json
import os

def load_tropes():
    path = os.path.join("data", "tropes.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_prompt(tropes, selected_type, selected_length):
    trope_data = tropes[selected_type]
    outline_parts = f"""
【開場】{trope_data.get('開場', '')}
【轉折】{trope_data.get('轉折', '')}
【高光】{trope_data.get('高光', '')}
"""
    keywords = trope_data.get("主題詞", "")
    return f"""請幫我寫一篇{selected_type}類型的{selected_length}小說，主題如下：
----
{outline_parts}
關鍵詞：{keywords}
----
請根據此主題，生成約 {10 if "短" in selected_length else 20} 段的大綱，每段請包含簡要劇情摘要。

此外，請在大綱最後統一列出本故事的核心角色，包括：
- 角色姓名
- 身份定位（主角、反派、配角等）
- 其與主角的關係或初始設定（如：退婚對象、宿敵、暗戀者）
請以列表方式條列角色設定。
"""


