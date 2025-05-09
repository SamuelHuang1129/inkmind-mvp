import json

def load_tropes(filepath="data/tropes.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_prompt(trope_data, selected_type, length):
    base = trope_data.get(selected_type, {})
    prompt = f"""小說類型：{selected_type}
小說長度：{length}

開場情節：{base.get("開場", "")}
故事轉折：{base.get("轉折", "")}
高光場面：{base.get("高光", "")}
主題關鍵詞：{base.get("主題詞", "")}
請根據以上信息，幫我生成一份適合這個類型的故事大綱。
"""
    return prompt
