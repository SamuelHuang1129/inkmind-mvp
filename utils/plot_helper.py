import networkx as nx
from pyvis.network import Network

def generate_character_interaction_graph(interactions, character_cards):
    G = nx.Graph()
    appearances = interactions.get("appearances", {})
    pairs = interactions.get("pairs", {})

    role_colors = {
        "主角": "blue",
        "反派": "red",
        "配角": "green",
        "未設定": "gray"
    }

    for name in appearances:
        size = len(appearances[name]) * 10 + 10
        role = character_cards.get(name, {}).get("定位", "未設定")
        label = f"{name}（{role}）"
        color = role_colors.get(role, "gray")
        G.add_node(name, label=label, size=size, color=color)

    for (a, b), info in pairs.items():
        label = f"{info['type']}｜{info['count']}次"
        width = max(1, info["count"])
        G.add_edge(a, b, value=width, title=label, label=label)

    net = Network(height="600px", width="100%", notebook=False, directed=False)
    net.from_nx(G)
    net.repulsion(node_distance=200, central_gravity=0.3)
    return net