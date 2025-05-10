import re

def parse_roles_from_outline(text):
    roles = {}

    lines = text.strip().splitlines()

    # 嘗試找出角色表格的起始行
    table_start = -1
    for i, line in enumerate(lines):
        if ("角色姓名" in line and "身份定位" in line) or ("角色" in line and "定位" in line):
            table_start = i + 1
            break

    if table_start == -1:
        return roles

    # 嘗試解析 markdown 表格 或 tab 分隔格式
    for line in lines[table_start:]:
        line = line.strip()
        if not line or line.startswith("|--") or line.startswith("----"):
            continue

        # 支援 Markdown 格式
        if '|' in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
        else:
            # 支援 Tab 分隔格式
            parts = [p.strip() for p in line.split('\t') if p.strip()]

        if len(parts) >= 3:
            name = parts[0].replace('：', '').strip()
            role = parts[1].strip()
            desc = parts[2].strip()
            roles[name] = {
                "定位": role if role in ["主角", "反派", "配角"] else "未設定",
                "背景": desc,
                "成長線": ""
            }

    return roles