from snownlp import SnowNLP
from itertools import combinations
from collections import defaultdict

def extract_characters_from_paragraph(text, known_characters):
    """從段落中抽取出現過的角色名"""
    return [name for name in known_characters if name in text]

def normalize_pair(a, b):
    """將角色對排序為無向鍵"""
    return tuple(sorted([a, b]))

def analyze_sentiment(text):
    """使用 SnowNLP 分析情緒傾向（0~1）"""
    try:
        return round(SnowNLP(text).sentiments, 4)
    except:
        return 0.5  # 預設中性

def update_interactions(paragraphs, character_cards):
    known_characters = list(character_cards.keys())
    pairs = {}
    appearances = defaultdict(list)
    matrix = defaultdict(lambda: defaultdict(int))

    for idx, para in enumerate(paragraphs):
        present = extract_characters_from_paragraph(para, known_characters)
        for name in present:
            appearances[name].append(idx)

        sentiment = analyze_sentiment(para)

        for a, b in combinations(present, 2):
            pair_key = normalize_pair(a, b)
            if pair_key not in pairs:
                pairs[pair_key] = {
                    "count": 1,
                    "paragraphs": [idx],
                    "sentiments": [sentiment]
                }
            else:
                pairs[pair_key]["count"] += 1
                pairs[pair_key]["paragraphs"].append(idx)
                pairs[pair_key]["sentiments"].append(sentiment)

            matrix[a][b] += 1
            matrix[b][a] += 1

    for pair_key, data in pairs.items():
        avg = round(sum(data["sentiments"]) / len(data["sentiments"]), 4)
        data["avg_sentiment"] = avg
        if avg >= 0.66:
            data["type"] = "合作"
        elif avg <= 0.33:
            data["type"] = "對立"
        else:
            data["type"] = "中立"

    return {
        "pairs": pairs,
        "appearances": dict(appearances),
        "matrix": {k: dict(v) for k, v in matrix.items()}
    }