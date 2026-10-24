import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import pandas as pd
import math
import io

# 日本語フォントの設定（Windows / Mac / Linux 自動対応）
plt.rcParams['font.sans-serif'] = [
    'Meiryo', 'Yu Gothic', 'MS Gothic', 'Hiragino Sans', 'Hiragino Kaku Gothic ProN',
    'IPAexGothic', 'IPAGothic', 'Noto Sans CJK JP', 'VL Gothic', 'DejaVu Sans'
]
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 1. 路線・駅名・施設・座標データ (ver4.3)
# ==========================================
def get_station_kana():
    return {
        "一ノ瀬": "いちのせ", "境港": "さかいみなと", "谷上町": "たにかみちょう", "第1拠点": "だいいちきょてん",
        "晴海坂": "はるみざか", "滝沢": "たきさわ", "終宮": "ついのみや", "新蒼海宮": "しんそうかいぐう",
        "蒼海宮": "そうかいぐう", "荒山村": "あらやまむら", "桜町一丁目": "さくらまちいっちょうめ",
        "谷上三丁目": "たにかみさんちょうめ", "白浜崎": "しらはまざき", "砂炭江": "さずみえ",
        "霧ヶ峰": "きりがみね", "霧ヶ峰湖": "きりがみねこ", "東都": "とうと", "風見野": "かざみの",
        "北茜ヶ原": "きたあかねがはら", "茜ヶ原": "あかねがはら", "桜坂": "さくらざか",
        "緑山": "みどりやま", "旭ヶ丘": "あさひがおか", "亀浜": "かめはま", "西霧ヶ峰": "にしきりがみね",
        "新都町": "しんみやこまち", "七瀬": "ななせ", "前哨基地": "ぜんしょうきち", "朝凪": "あさなぎ",
        "速見": "はやみ", "南新都町": "みなみしんみやこまち", "朝凪南": "あさなぎみなみ",
        "東晴海坂": "ひがしはるみざか", "南部海岸": "なんぶかいがん", "ポータルシティ": "ぽーたるしてぃ",
        "坂柳": "さかやなぎ"
    }

def get_facilities():
    return {
        "一ノ瀬": "たかのり拠点",
        "境港": "ブランチマイニング場",
        "谷上町": "初拠点付近",
        "桜町一丁目": "初期スポーン地点最寄り",
        "荒山村": "村人交易所",
        "東晴海坂": "天空トラップ",
        "終宮": "エンドポータル最寄り駅",
        "新蒼海宮": "吉岡拠点",
        "蒼海宮": "ガーディアントラップ",
        "亀浜": "霧ヶ峰空港, 竹製造機, 第二拠点中心部",
        "霧ヶ峰": "羊毛製造機",
        "霧ヶ峰湖": "畑, 牧場",
        "茜ヶ原": "メサ最寄り駅",
        "前哨基地": "前哨基地最寄り駅",
        "朝凪": "第3拠点周辺",
        "ポータルシティ": "ネザー要塞最寄り駅"
    }

LINES_STATIONS = {
    "中央線": ["一ノ瀬", "境港", "谷上町", "第1拠点", "晴海坂", "滝沢", "終宮", "新蒼海宮", "蒼海宮"],
    "桜町線(各停)": ["荒山村", "桜町一丁目", "谷上三丁目", "白浜崎", "砂炭江", "霧ヶ峰", "霧ヶ峰湖", "東都", "風見野", "北茜ヶ原", "茜ヶ原"],
    "桜町線(快速)": ["荒山村", "谷上三丁目", "霧ヶ峰", "東都", "茜ヶ原", "南部海岸", "ポータルシティ"],
    "東西線": ["一ノ瀬", "桜坂", "緑山", "旭ヶ丘", "霧ヶ峰", "亀浜"],
    "南北線": ["西霧ヶ峰", "新都町", "七瀬", "前哨基地"],
    "霧ヶ峰線": ["蒼海宮", "亀浜", "西霧ヶ峰", "霧ヶ峰湖", "東都", "風見野"],
    "南辺線": ["風見野", "前哨基地"],
    "新都心線": ["終宮", "亀浜", "新都町", "朝凪", "東都"],
    "中央都市線": ["速見", "霧ヶ峰", "西霧ヶ峰", "南新都町", "朝凪南", "朝凪"],
    "東都線": ["東都", "朝凪", "七瀬", "坂柳"],
    "中央新幹線": ["白浜崎", "新蒼海宮"],
    "晴海坂線": ["砂炭江", "晴海坂", "東晴海坂"]
}

def get_line_colors():
    return {
        "中央線": "#FF8C00",
        "桜町線(各停)": "#FF69B4",
        "桜町線(快速)": "#FF1493",
        "東西線": "#00BFFF",
        "南北線": "#1E90FF",
        "霧ヶ峰線": "#FF0000",
        "南辺線": "#8A2BE2",
        "新都心線": "#8B4513",
        "中央都市線": "#228B22",
        "東都線": "#00CED1",
        "中央新幹線": "#DAA520",
        "晴海坂線": "#808080"
    }

def get_lines_data():
    return {
        "中央線": [
            ("一ノ瀬", "境港", 46), ("境港", "谷上町", 30), ("谷上町", "第1拠点", 14),
            ("第1拠点", "晴海坂", 15), ("晴海坂", "滝沢", 45), ("滝沢", "終宮", 54),
            ("終宮", "新蒼海宮", 90), ("新蒼海宮", "蒼海宮", 51)
        ],
        "桜町線(各停)": [
            ("荒山村", "桜町一丁目", 48), ("桜町一丁目", "谷上三丁目", 16), ("谷上三丁目", "白浜崎", 28),
            ("白浜崎", "砂炭江", 66), ("砂炭江", "霧ヶ峰", 104), ("霧ヶ峰", "霧ヶ峰湖", 26),
            ("霧ヶ峰湖", "東都", 34), ("東都", "風見野", 34), ("風見野", "北茜ヶ原", 91), ("北茜ヶ原", "茜ヶ原", 56)
        ],
        "桜町線(快速)": [
            ("荒山村", "谷上三丁目", 55), ("谷上三丁目", "霧ヶ峰", 160), ("霧ヶ峰", "東都", 50),
            ("東都", "茜ヶ原", 170), ("茜ヶ原", "南部海岸", 120), ("南部海岸", "ポータルシティ", 70)
        ],
        "東西線": [
            ("一ノ瀬", "桜坂", 124), ("桜坂", "緑山", 92), ("緑山", "旭ヶ丘", 28),
            ("旭ヶ丘", "霧ヶ峰", 48), ("霧ヶ峰", "亀浜", 39)
        ],
        "南北線": [
            ("西霧ヶ峰", "新都町", 19), ("新都町", "七瀬", 48), ("七瀬", "前哨基地", 48)
        ],
        "霧ヶ峰線": [
            ("蒼海宮", "亀浜", 197), ("亀浜", "西霧ヶ峰", 22), ("西霧ヶ峰", "霧ヶ峰湖", 40),
            ("霧ヶ峰湖", "東都", 34), ("東都", "風見野", 34)
        ],
        "南辺線": [
            ("風見野", "前哨基地", 62)
        ],
        "新都心線": [
            ("終宮", "亀浜", 138), ("亀浜", "新都町", 27), ("新都町", "朝凪", 60), ("朝凪", "東都", 45)
        ],
        "中央都市線": [
            ("速見", "霧ヶ峰", 16), ("霧ヶ峰", "西霧ヶ峰", 13), ("西霧ヶ峰", "南新都町", 20),
            ("南新都町", "朝凪南", 20), ("朝凪南", "朝凪", 60)
        ],
        "東都線": [
            ("東都", "朝凪", 40), ("朝凪", "七瀬", 40), ("七瀬", "坂柳", 40)
        ],
        "中央新幹線": [
            ("白浜崎", "新蒼海宮", 44)
        ],
        "晴海坂線": [
            ("砂炭江", "晴海坂", 57), ("晴海坂", "東晴海坂", 25)
        ]
    }

# 直交グリッド座標データ (中央線＝横 Y=20, 桜町線＝縦 X=6 で垂直交差)
def get_station_coords():
    return {
        "一ノ瀬": (0, 20), "境港": (2.2, 20), "谷上町": (4.5, 20), "第1拠点": (7.8, 20),
        "晴海坂": (9.8, 20), "滝沢": (11.8, 20), "終宮": (13.8, 20), "新蒼海宮": (15.8, 20), "蒼海宮": (18.0, 20),
        "東晴海坂": (9.8, 22.2),
        "荒山村": (6, 24), "桜町一丁目": (6, 22), "谷上三丁目": (6, 20), "白浜崎": (6, 17.5),
        "砂炭江": (6, 15), "霧ヶ峰": (6, 12), "霧ヶ峰湖": (6, 9.5), "東都": (6, 7),
        "風見野": (6, 4.5), "北茜ヶ原": (6, 2.5), "茜ヶ原": (6, 0.5), "南部海岸": (6, -1.5), "ポータルシティ": (6, -3.5),
        "桜坂": (0, 17.5), "緑山": (0, 15), "旭ヶ丘": (3, 12), "速見": (4.2, 13.5),
        "西霧ヶ峰": (9.8, 11), "亀浜": (13.8, 12), "南新都町": (11.5, 11), "新都町": (11.5, 9),
        "朝凪南": (9.8, 8.2), "朝凪": (9.8, 7), "七瀬": (13.8, 7), "坂柳": (16.5, 7),
        "前哨基地": (13.8, 4.5)
    }

def get_direction(line_name, from_station, to_station):
    if line_name in LINES_STATIONS:
        stations = LINES_STATIONS[line_name]
        if from_station in stations and to_station in stations:
            idx_from = stations.index(from_station)
            idx_to = stations.index(to_station)
            return f"{stations[-1]}方面" if idx_to > idx_from else f"{stations[0]}方面"
    return ""

# ==========================================
# 2. 路線図描画関数
# ==========================================
def draw_railway_map(highlight_stations=None):
    coords = get_station_coords()
    colors = get_line_colors()
    facilities = get_facilities()

    fig, ax = plt.subplots(figsize=(18, 22), dpi=150)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')
    ax.grid(True, which='both', color='#E2E8F0', linestyle='-', linewidth=0.8, zorder=0)

    def plot_route(pts, color, lw=5, ls='-', zorder=3, label=None):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.plot(xs, ys, color=color, linewidth=lw, linestyle=ls,
                solid_capstyle='round', solid_joinstyle='round', zorder=zorder, label=label)

    plot_route([coords[s] for s in LINES_STATIONS["中央線"]], colors["中央線"], lw=6.5, zorder=4, label="中央線")
    s_local = LINES_STATIONS["桜町線(各停)"]
    plot_route([(5.86, coords[s][1]) for s in s_local], colors["桜町線(各停)"], lw=5.5, zorder=4, label="桜町線(各停)")
    s_rapid = LINES_STATIONS["桜町線(快速)"]
    plot_route([(6.14, coords[s][1]) for s in s_rapid], colors["桜町線(快速)"], lw=5.5, zorder=4, label="桜町線(快速)")

    plot_route([(6, 15), (9.8, 15), (9.8, 20), (9.8, 22.2)], colors["晴海坂線"], lw=4.5, label="晴海坂線")
    plot_route([(6, 17.5), (15.8, 17.5), (15.8, 20)], colors["中央新幹線"], lw=4.5, ls='--', label="中央新幹線")
    plot_route([(0, 20), (0, 17.5), (0, 15), (0, 12), (3, 12), (6, 12), (13.8, 12)], colors["東西線"], lw=5, label="東西線")
    plot_route([(18.0, 20), (18.0, 12), (13.8, 12), (13.8, 11), (9.8, 11), (9.8, 9.5), (6.34, 9.5), (6.34, 7), (6.34, 4.5)], colors["霧ヶ峰線"], lw=5, zorder=4, label="霧ヶ峰線(風見野で南辺線へ直通)")
    plot_route([(6.34, 4.5), (13.8, 4.5)], colors["南辺線"], lw=5, zorder=4, label="南辺線(霧ヶ峰線と直通)")
    plot_route([(13.8, 20), (13.8, 12), (11.5, 12), (11.5, 9), (9.8, 9), (9.8, 7.12), (6, 7.12)], colors["新都心線"], lw=5, label="新都心線")
    plot_route([(4.2, 13.5), (6, 12), (9.8, 11), (11.5, 11), (10.6, 8.2), (9.8, 8.2), (9.8, 7)], colors["中央都市線"], lw=4.5, label="中央都市線")
    plot_route([(9.8, 11), (11.5, 9), (13.8, 9), (13.8, 7), (13.8, 4.5)], colors["南北線"], lw=4.5, label="南北線")
    plot_route([(6, 6.88), (9.8, 6.88), (13.8, 6.88), (16.5, 6.88)], colors["東都線"], lw=5, label="東都線")

    plot_route([(4.5, 20), (6, 20)], "#4CAF50", lw=3.2, ls=':', zorder=5, label="徒歩連絡")
    plot_route([(11.5, 9), (11.5, 11)], "#4CAF50", lw=3.2, ls=':', zorder=5)

    station_lines_count = {}
    for line, stas in LINES_STATIONS.items():
        for s in stas:
            station_lines_count[s] = station_lines_count.get(s, 0) + 1

    rapid_stops = set(LINES_STATIONS["桜町線(快速)"])
    local_stops = set(LINES_STATIONS["桜町線(各停)"])

    for sta, (x, y) in coords.items():
        is_transfer = station_lines_count.get(sta, 0) > 1
        is_highlighted = highlight_stations and sta in highlight_stations

        if sta in local_stops or sta in rapid_stops:
            if sta in ["霧ヶ峰湖", "東都", "風見野"]:
                rect = mpatches.FancyBboxPatch(
                    (5.72, y - 0.22), 0.76, 0.44,
                    boxstyle="round,pad=0.05,rounding_size=0.15",
                    facecolor="#FFF9C4" if is_highlighted else "white",
                    edgecolor="#FF0000" if is_highlighted else "#1E293B",
                    linewidth=3 if is_highlighted else 2.2, zorder=6
                )
                ax.add_patch(rect)
            elif sta in local_stops and sta in rapid_stops:
                rect = mpatches.FancyBboxPatch(
                    (5.72, y - 0.22), 0.56, 0.44,
                    boxstyle="round,pad=0.05,rounding_size=0.15",
                    facecolor="#FFF9C4" if is_highlighted else "white",
                    edgecolor="#FF0000" if is_highlighted else "#1E293B",
                    linewidth=3 if is_highlighted else 2.2, zorder=6
                )
                ax.add_patch(rect)
            elif sta in local_stops:
                ax.scatter(5.86, y, s=170, facecolor="#FFF9C4" if is_highlighted else "white",
                           edgecolor="#FF0000" if is_highlighted else colors["桜町線(各停)"],
                           linewidth=2.5, zorder=6)
                if is_transfer:
                    ax.scatter(5.86, y, s=230, facecolor="white", edgecolor="#1E293B", linewidth=2.2, zorder=6)
            elif sta in rapid_stops:
                ax.scatter(6.14, y, s=180, facecolor="#FFF9C4" if is_highlighted else "white",
                           edgecolor="#FF0000" if is_highlighted else colors["桜町線(快速)"],
                           linewidth=2.5, zorder=6)
        else:
            size = 240 if is_transfer else 150
            edge_c = "#FF0000" if is_highlighted else ("#1E293B" if is_transfer else "#334155")
            face_c = "#FFF9C4" if is_highlighted else "white"
            ax.scatter(x, y, s=size, facecolor=face_c, edgecolor=edge_c,
                       linewidth=3 if is_highlighted else 2.2, zorder=6)

        offset_x, offset_y = 0.0, 0.42
        ha, va = 'center', 'bottom'

        if sta in ["一ノ瀬", "境港", "谷上町", "第1拠点", "滝沢", "終宮", "新蒼海宮", "蒼海宮"]:
            offset_x, offset_y, ha, va = 0.0, 0.42, 'center', 'bottom'
        elif sta == "晴海坂":
            offset_x, offset_y, ha, va = -0.35, -0.38, 'right', 'top'
        elif sta == "東晴海坂":
            offset_x, offset_y, ha, va = 0.0, 0.38, 'center', 'bottom'
        elif sta in ["荒山村", "桜町一丁目", "白浜崎", "砂炭江", "霧ヶ峰湖", "東都", "風見野", "北茜ヶ原", "茜ヶ原", "南部海岸", "ポータルシティ"]:
            offset_x, offset_y, ha, va = -0.48, 0.0, 'right', 'center'
        elif sta == "谷上三丁目":
            offset_x, offset_y, ha, va = 0.48, -0.35, 'left', 'top'
        elif sta == "霧ヶ峰":
            offset_x, offset_y, ha, va = -0.48, -0.35, 'right', 'top'
        elif sta in ["桜坂", "緑山"]:
            offset_x, offset_y, ha, va = -0.4, 0.0, 'right', 'center'
        elif sta == "旭ヶ丘":
            offset_x, offset_y, ha, va = 0.0, 0.38, 'center', 'bottom'
        elif sta == "速見":
            offset_x, offset_y, ha, va = -0.35, 0.25, 'right', 'bottom'
        elif sta == "西霧ヶ峰":
            offset_x, offset_y, ha, va = -0.35, 0.35, 'right', 'bottom'
        elif sta == "南新都町":
            offset_x, offset_y, ha, va = 0.35, 0.25, 'left', 'bottom'
        elif sta == "新都町":
            offset_x, offset_y, ha, va = 0.38, -0.15, 'left', 'top'
        elif sta == "朝凪南":
            offset_x, offset_y, ha, va = -0.38, 0.0, 'right', 'center'
        elif sta == "朝凪":
            offset_x, offset_y, ha, va = 0.0, -0.45, 'center', 'top'
        elif sta == "亀浜":
            offset_x, offset_y, ha, va = 0.42, 0.25, 'left', 'bottom'
        elif sta == "七瀬":
            offset_x, offset_y, ha, va = 0.42, 0.25, 'left', 'bottom'
        elif sta == "坂柳":
            offset_x, offset_y, ha, va = 0.0, -0.42, 'center', 'top'
        elif sta == "前哨基地":
            offset_x, offset_y, ha, va = 0.42, 0.0, 'left', 'center'

        label_text = f"★{sta}" if sta in facilities else sta
        if sta == "風見野":
            label_text += " (直通境界)"
        bbox_props = dict(boxstyle="round,pad=0.2", fc="#FEF08A" if is_highlighted else "white",
                          ec="#F59E0B" if is_highlighted else "none", alpha=0.88)

        ax.text(x + offset_x, y + offset_y, label_text, fontsize=10.5, fontweight='bold',
                color='#0F172A', ha=ha, va=va, zorder=8, bbox=bbox_props)

    ax.set_title("水素鉄道 路線図 (ver4.3 - 霧ヶ峰線延伸・南辺線直通対応)", fontsize=18, fontweight='bold', pad=15, color='#0F172A')
    ax.set_xlim(-2.5, 20.0)
    ax.set_ylim(-5.0, 25.5)
    ax.axis('off')

    legend_elements = [Line2D([0], [0], color=c, lw=5, label=name) for name, c in colors.items()]
    legend_elements.append(Line2D([0], [0], color="#4CAF50", lw=3.2, ls=":", label="徒歩連絡"))
    ax.legend(handles=legend_elements, loc='lower right', ncol=3, fontsize=10,
              frameon=True, facecolor='white', edgecolor='#CBD5E1', title="路線凡例 (★は主要施設あり)")

    plt.tight_layout()
    return fig

# ==========================================
# 3. 経路検索グラフ構築 (ver4.3)
# ==========================================
@st.cache_resource
def build_graph():
    G = nx.Graph()
    lines = get_lines_data()
    station_lines = {}
    
    for line_name, edges in lines.items():
        for u, v, w in edges:
            G.add_edge(f"{u}|{line_name}", f"{v}|{line_name}", weight_fast=w, weight_trans=1, line=line_name, is_transfer=False)
            station_lines.setdefault(u, set()).add(line_name)
            station_lines.setdefault(v, set()).add(line_name)
            
    for sta, slines in station_lines.items():
        sorted_slines = sorted(list(slines))
        for i in range(len(sorted_slines)):
            for j in range(i+1, len(sorted_slines)):
                line_a = sorted_slines[i]
                line_b = sorted_slines[j]
                if sta == "風見野" and {line_a, line_b} == {"霧ヶ峰線", "南辺線"}:
                    G.add_edge(f"{sta}|{line_a}", f"{sta}|{line_b}", weight_fast=0, weight_trans=0, line="直通", is_transfer=False)
                else:
                    G.add_edge(f"{sta}|{line_a}", f"{sta}|{line_b}", weight_fast=30, weight_trans=10000, line="乗り換え", is_transfer=True)

    walks = [("谷上町", "谷上三丁目", 10), ("新都町", "南新都町", 10)]
    for u, v, w in walks:
        if u in station_lines and v in station_lines:
            for l_u in station_lines[u]:
                for l_v in station_lines[v]:
                    G.add_edge(f"{u}|{l_u}", f"{v}|{l_v}", weight_fast=w, weight_trans=10000, line="徒歩連絡", is_transfer=True)
                    
    G.add_edge("砂炭江|桜町線(各停)", "西霧ヶ峰|南北線", weight_fast=110, weight_trans=0, line="南北線(直通)", is_transfer=False)
    G.add_edge("砂炭江|桜町線(各停)", "亀浜|東西線", weight_fast=94, weight_trans=0, line="東西線(直通)", is_transfer=False)
    G.add_edge("砂炭江|桜町線(各停)", "亀浜|新都心線", weight_fast=94, weight_trans=0, line="新都心線(直通)", is_transfer=False)
    
    return G, station_lines

# ==========================================
# 4. 都市工学モデルによる人口・乗降客数推計 (NEW)
# ==========================================
@st.cache_data
def simulate_ridership():
    G_base, station_lines = build_graph()
    coords = get_station_coords()
    facilities = get_facilities()
    all_stations = list(station_lines.keys())

    # 施設重要度ウェイト（拠点・空港・主要トラップほど人が集まる）
    facility_weights = {
        "亀浜": 2.4,         # 空港・第二拠点中心部・竹製造機
        "第1拠点": 2.1,      # 第1拠点
        "朝凪": 2.0,         # 第3拠点周辺
        "一ノ瀬": 1.8,       # たかのり拠点
        "新蒼海宮": 1.8,     # 吉岡拠点
        "桜町一丁目": 1.7,   # 初期スポーン最寄り
        "谷上町": 1.6,       # 初拠点付近
        "荒山村": 1.6,       # 村人交易所
        "終宮": 1.6,         # エンドポータル
        "ポータルシティ": 1.5, # ネザー要塞
        "蒼海宮": 1.4,       # ガーディアントラップ
        "東晴海坂": 1.4,     # 天空トラップ
        "霧ヶ峰": 1.5,       # 羊毛製造機
        "霧ヶ峰湖": 1.35,    # 畑・牧場
        "前哨基地": 1.35,    # 前哨基地
        "茜ヶ原": 1.3,       # メサ
        "境港": 1.3          # ブランチマイニング場
    }

    # Step 1: 各駅の基礎ポテンシャル（路線数＋優等列車ボーナス＋施設魅力度）
    base_mass = {}
    for s in all_stations:
        lines = station_lines[s]
        line_score = len(lines) ** 1.35
        if "中央新幹線" in lines:
            line_score += 1.6
        if "桜町線(快速)" in lines:
            line_score += 0.9
        fac_mult = facility_weights.get(s, 1.0)
        base_mass[s] = line_score * fac_mult

    # Step 2: 周辺の都会度（重力モデルによる空間ポテンシャル）
    # 周囲に大規模駅が密集しているほど、単独駅でも「山手線内の駅」のように都会度が上がる
    urban_index = {}
    for s1 in all_stations:
        x1, y1 = coords[s1]
        surround_potential = 0.0
        for s2 in all_stations:
            if s1 == s2:
                continue
            x2, y2 = coords[s2]
            dist = math.hypot(x1 - x2, y1 - y2)
            # 距離減衰（近い駅の規模が強く影響する）
            surround_potential += base_mass[s2] / ((dist * 0.45 + 1.2) ** 1.75)
        urban_index[s1] = surround_potential

    # 都会度偏差値（40〜78程度に正規化）
    max_u, min_u = max(urban_index.values()), min(urban_index.values())
    urban_score = {}
    for s in all_stations:
        norm = (urban_index[s] - min_u) / (max_u - min_u) if max_u > min_u else 0.5
        urban_score[s] = round(38.0 + norm * 37.0, 1)

    # Step 3: 全駅ペア間のOD交通量（重力モデル）と経路上の乗り換え・通過集計
    # 駅ごとの直接乗降（出発・到着）と、乗り換え利用を分けて集計
    direct_passengers = {s: 0.0 for s in all_stations}
    transfer_passengers = {s: 0.0 for s in all_stations}
    through_passengers = {s: 0.0 for s in all_stations}

    # 駅の総合発生集中力 = 基礎規模 × (1 + 周辺の都会度効果)
    station_power = {
        s: base_mass[s] * (0.55 + 0.95 * ((urban_score[s] - 35.0) / 40.0) ** 1.4)
        for s in all_stations
    }

    for i, s1 in enumerate(all_stations):
        for s2 in all_stations[i+1:]:
            G_tmp = G_base.copy()
            for l in station_lines[s1]:
                G_tmp.add_edge("ORIG", f"{s1}|{l}", weight_fast=0)
            for l in station_lines[s2]:
                G_tmp.add_edge(f"{s2}|{l}", "DEST", weight_fast=0)

            try:
                path = nx.shortest_path(G_tmp, "ORIG", "DEST", weight="weight_fast")
                travel_time = nx.shortest_path_length(G_tmp, "ORIG", "DEST", weight="weight_fast")
                
                # 重力モデル: 2駅の都市力積 ÷ 所要時間の減衰
                od_flow = (station_power[s1] * station_power[s2]) / ((travel_time + 35.0) ** 1.15)
                
                # 起終点駅の直接乗降
                direct_passengers[s1] += od_flow
                direct_passengers[s2] += od_flow

                # 経路上の乗り換え・通過を解析
                actual_nodes = path[1:-1]
                visited_stas = []
                for idx in range(len(actual_nodes) - 1):
                    u, v = actual_nodes[idx], actual_nodes[idx + 1]
                    u_sta, u_line = u.split('|')
                    v_sta, v_line = v.split('|')
                    if u_sta == v_sta and u_line != v_line:
                        # 乗り換え発生（直通運転は乗換カウント0.35倍の通過扱い、通常乗換は両路線で乗降計上）
                        edge_d = G_base.get_edge_data(u, v)
                        if edge_d and edge_d.get("is_transfer", False):
                            transfer_passengers[u_sta] += od_flow * 2.1
                        else:
                            transfer_passengers[u_sta] += od_flow * 0.4
                    elif u_sta != v_sta:
                        if u_sta not in (s1, s2) and u_sta not in visited_stas:
                            through_passengers[u_sta] += od_flow * 0.18
                            visited_stas.append(u_sta)
            except nx.NetworkXNoPath:
                continue

    # Step 4: 現実の首都圏・政令指定都市スケールにスケーリング
    # 12路線36駅を有する広域都市圏として、都市圏総人口 約185万人、1日総乗降客数 約360万人規模に設定
    raw_totals = {
        s: direct_passengers[s] * 1.0 + transfer_passengers[s] * 1.15 + through_passengers[s] * 0.25
        for s in all_stations
    }
    scale_factor = 3650000.0 / sum(raw_totals.values())

    records = []
    for s in all_stations:
        dir_pax = int(round(direct_passengers[s] * scale_factor, -1))
        trf_pax = int(round((transfer_passengers[s] * 1.15 + through_passengers[s] * 0.25) * scale_factor, -1))
        total_pax = dir_pax + trf_pax
        
        # 駅周辺の定住人口推計（拠点・住宅地性格と都会度から算出）
        fac_text = facilities.get(s, "一般駅・住宅街")
        pop_ratio = 0.48 if len(station_lines[s]) <= 2 else 0.34
        if "拠点" in fac_text or "村" in fac_text:
            pop_ratio *= 1.35
        est_pop = int(round((dir_pax * pop_ratio + urban_score[s] * 180), -1))

        # 駅の性格タイプ分類
        line_cnt = len(station_lines[s])
        if line_cnt >= 4:
            sta_type = "🏙️ 中枢メガターミナル"
        elif line_cnt == 3:
            sta_type = "🏢 主要乗換ターミナル"
        elif line_cnt == 2:
            sta_type = "🔄 接続・乗換駅"
        else:
            if urban_score[s] >= 58.0:
                sta_type = "🚃 都心近郊・単独駅 (山手線型)"
            elif urban_score[s] >= 48.0:
                sta_type = "🏘️ 中核ベッドタウン駅"
            else:
                sta_type = "🌲 郊外・ローカル駅"

        records.append({
            "駅名": s,
            "よみ": get_station_kana().get(s, ""),
            "1日乗降客数": total_pax,
            "うち定期・直接利用": dir_pax,
            "うち乗換・通過加算": trf_pax,
            "乗換率(%)": round(trf_pax / total_pax * 100, 1) if total_pax > 0 else 0.0,
            "周辺都会度(偏差値)": urban_score[s],
            "駅勢圏人口(推計)": est_pop,
            "所属路線数": line_cnt,
            "駅タイプ": sta_type,
            "主な施設・拠点": fac_text
        })

    df = pd.DataFrame(records).sort_values("1日乗降客数", ascending=False).reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = "順位"
    return df

# ==========================================
# 5. UIメイン処理
# ==========================================
def main():
    st.set_page_config(page_title="Minecraft鉄道 乗り換え案内 ver4.3", layout="wide")
    st.title("🚃 水素鉄道 乗り換え案内 ＆ 路線図メーカー ver4.3")
    
    G_base, station_lines = build_graph()
    station_kana = get_station_kana()
    facilities = get_facilities()
    line_colors = get_line_colors()
    
    sorted_stations = sorted(list(station_lines.keys()), key=lambda x: station_kana.get(x, x))
    station_options = [f"{s} ({station_kana.get(s, '')})" for s in sorted_stations]

    tab_search, tab_map, tab_ranking, tab_info = st.tabs([
        "🔍 経路検索",
        "🗺️ 路線図（画像保存）",
        "📊 駅別乗降客数ランキング",
        "🏢 各路線・駅・施設一覧"
    ])

    highlight_stas = set()

    with tab_search:
        st.markdown("### 出発・到着駅と条件を選択")
        col1, col2 = st.columns(2)
        
        default_start = [opt for opt in station_options if opt.startswith("荒山村")][0] if any(opt.startswith("荒山村") for opt in station_options) else station_options[0]
        default_end = [opt for opt in station_options if opt.startswith("前哨基地")][0] if any(opt.startswith("前哨基地") for opt in station_options) else station_options[1]
        
        start_str = col1.selectbox("出発駅", station_options, index=station_options.index(default_start))
        end_str = col2.selectbox("到着駅", station_options, index=station_options.index(default_end))
        
        start_sta = start_str.split(' ')[0]
        end_sta = end_str.split(' ')[0]

        search_mode = st.radio("優先する条件", ["最速（時間を優先／快速優先）", "乗り換え回数（乗換の少なさを優先）"], horizontal=True)

        if st.button("経路を検索", type="primary", use_container_width=True):
            if start_sta == end_sta:
                st.warning("出発駅と到着駅が同じです。")
            else:
                G = G_base.copy()
                for line in station_lines[start_sta]:
                    G.add_edge("START", f"{start_sta}|{line}", weight_fast=0, weight_trans=0, line="乗車", is_transfer=False)
                for line in station_lines[end_sta]:
                    G.add_edge(f"{end_sta}|{line}", "END", weight_fast=0, weight_trans=0, line="降車", is_transfer=False)

                weight_key = "weight_fast" if "最速" in search_mode else "weight_trans"

                try:
                    path = nx.shortest_path(G, "START", "END", weight=weight_key)
                    
                    steps = []
                    transfer_count = 0
                    total_ride_time = 0 
                    actual_path = path[1:-1]

                    for node in actual_path:
                        highlight_stas.add(node.split('|')[0])

                    for i in range(len(actual_path)-1):
                        u, v = actual_path[i], actual_path[i+1]
                        data = G.get_edge_data(u, v)
                        u_sta = u.split('|')[0]
                        v_sta = v.split('|')[0]
                        cost = data.get('weight_fast', 0)
                        
                        if data['is_transfer']:
                            transfer_count += 1
                            steps.append({
                                "from": u_sta, "to": v_sta, "line": data['line'], 
                                "is_transfer": True, "is_direct": False, "intermediates": [], "time": cost
                            })
                        elif u_sta == v_sta and not data['is_transfer']:
                            steps.append({
                                "from": u_sta, "to": v_sta, "line": data['line'],
                                "is_transfer": False, "is_direct": True, "intermediates": [], "time": cost
                            })
                        else:
                            total_ride_time += cost 
                            if steps and not steps[-1]['is_transfer'] and not steps[-1]['is_direct'] and steps[-1]['line'] == data['line']:
                                steps[-1]['to'] = v_sta
                                steps[-1]['intermediates'].append(u_sta)
                                steps[-1]['time'] += cost
                            else:
                                steps.append({
                                    "from": u_sta, "to": v_sta, "line": data['line'], 
                                    "is_transfer": False, "is_direct": False, "intermediates": [], "time": cost
                                })
                    
                    def round_time_str(seconds):
                        rounded = int((seconds + 5) // 10) * 10
                        if rounded == 0:
                            return "0秒"
                        m, s = divmod(rounded, 60)
                        return f"{m}分{s}秒" if m > 0 else f"{s}秒"
                    
                    total_time_formatted = round_time_str(total_ride_time)
                    st.success(f"乗換: **{transfer_count}回** ｜ 総乗車時間: **{total_time_formatted}**")
                    st.divider()
                    
                    for step in steps:
                        if step['is_transfer']:
                            if step['line'] == "徒歩連絡":
                                st.markdown(f"<div style='text-align: center; color: #4CAF50; font-weight: bold; margin: 15px 0;'>🚶 {step['from']}駅から {step['to']}駅へ徒歩移動</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='text-align: center; color: gray; margin: 15px 0;'>↑↓ {step['from']}駅で乗り換え</div>", unsafe_allow_html=True)
                        elif step['is_direct']:
                            st.markdown(f"<div style='text-align: center; color: #ff4b4b; font-weight: bold; margin: 15px 0;'>✨ {step['from']}駅から直通（乗り換え不要・そのまま乗車）</div>", unsafe_allow_html=True)
                        else:
                            color = line_colors.get(step['line'], "#555555")
                            ride_time_formatted = round_time_str(step['time'])
                            dir_str = get_direction(step['line'], step['from'], step['to'])
                            dir_label = f" [{dir_str}]" if dir_str else ""
                            
                            with st.container():
                                st.markdown(
                                    f"<div style='border-left: 6px solid {color}; padding-left: 15px; margin: 10px 0;'>"
                                    f"<h4 style='margin: 0 0 5px 0;'>{step['from']}駅</h4>"
                                    f"<p style='margin: 0; color: {color}; font-weight: bold;'>↓ {step['line']}{dir_label} （乗車時間: {ride_time_formatted}）</p>"
                                    f"</div>",
                                    unsafe_allow_html=True
                                )
                                
                                if step['intermediates']:
                                    with st.expander(f"途中駅（{len(step['intermediates'])}駅）"):
                                        for inter in step['intermediates']:
                                            st.write(f"・ {inter}駅")
                                            
                                st.markdown(
                                    f"<div style='border-left: 6px solid {color}; padding-left: 15px; margin: 10px 0;'>"
                                    f"<h4 style='margin: 5px 0 0 0;'>{step['to']}駅</h4>"
                                    f"</div>",
                                    unsafe_allow_html=True
                                )

                except nx.NetworkXNoPath:
                    st.error("経路が見つかりませんでした。")

    with tab_map:
        st.markdown("### 水素鉄道 直交グリッド路線図")
        fig = draw_railway_map(highlight_stations=highlight_stas if highlight_stas else None)
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
        buf.seek(0)
        st.download_button(
            label="📥 路線図を高画質PNG画像としてダウンロード",
            data=buf,
            file_name="suiso_railway_map_v4_3.png",
            mime="image/png",
            type="primary"
        )

    with tab_ranking:
        st.markdown("### 📊 水素鉄道 都市圏人口・駅別1日乗降客数ランキング")
        st.caption(
            "路線網のトポロジー（媒介中心性）・周辺の都会度（空間重力モデル）・接続路線数・拠点施設の重要度から、"
            "現実の都市圏（山手線内の単独駅と郊外路線の単独駅の差、巨大乗換ターミナルの集中など）を忠実に再現した推計データです。"
        )

        df_rank = simulate_ridership()
        total_world_pop = int(df_rank["駅勢圏人口(推計)"].sum())
        total_daily_pax = int(df_rank["1日乗降客数"].sum())
        top_sta = df_rank.iloc[0]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🌏 水素鉄道圏 推計総人口", f"{total_world_pop:,} 人", "3大拠点＋12路線都市圏")
        m2.metric("🚃 全駅1日延べ乗降客数", f"{total_daily_pax:,} 人/日", "乗り換え・直通流動含む")
        m3.metric("👑 最大ターミナル駅", f"{top_sta['駅名']}駅", f"{int(top_sta['1日乗降客数']):,} 人/日")
        m4.metric("🏙️ 最高都会度エリア", f"{df_rank.sort_values('周辺都会度(偏差値)', ascending=False).iloc[0]['駅名']}周辺", f"都会度偏差値 {df_rank['周辺都会度(偏差値)'].max()}")

        st.divider()

        # 上位15駅のグラフ表示（直接利用 vs 乗換利用の積み上げ横棒グラフ）
        st.markdown("#### 🏆 駅別乗降客数 トップ15（直接乗降 ＋ 乗換加算の内訳）")
        top15 = df_rank.head(15).iloc[::-1]
        fig_bar, ax_bar = plt.subplots(figsize=(12, 6), dpi=130)
        fig_bar.patch.set_facecolor('#F8FAFC')
        ax_bar.set_facecolor('#F8FAFC')

        ax_bar.barh(top15["駅名"], top15["うち定期・直接利用"], color="#3B82F6", label="駅自体の乗降客（周辺の都会度・施設・住民）")
        ax_bar.barh(top15["駅名"], top15["うち乗換・通過加算"], left=top15["うち定期・直接利用"], color="#F59E0B", label="乗り換え・直通境界客")

        for idx, row in top15.iterrows():
            ax_bar.text(row["1日乗降客数"] + 3000, row["駅名"], f"{int(row['1日乗降客数']):,}人 ({row['所属路線数']}路線)", va='center', fontsize=9.5, fontweight='bold', color='#1E293B')

        ax_bar.set_xlim(0, df_rank["1日乗降客数"].max() * 1.18)
        ax_bar.set_xlabel("1日あたり乗降客数（人）")
        ax_bar.grid(axis='x', linestyle='--', alpha=0.5)
        ax_bar.legend(loc="lower right")
        plt.tight_layout()
        st.pyplot(fig_bar)

        st.divider()

        # 全36駅のランキングテーブル
        st.markdown("#### 📋 全36駅 詳細ランキング一覧")
        filter_type = st.selectbox(
            "駅のタイプで絞り込み",
            ["すべて表示", "単独駅（1路線のみ）で都会度による差を見る", "乗換駅（2路線以上）のみ表示"]
        )

        df_display = df_rank.copy()
        if "単独駅" in filter_type:
            df_display = df_display[df_display["所属路線数"] == 1]
        elif "乗換駅" in filter_type:
            df_display = df_display[df_display["所属路線数"] >= 2]

        st.dataframe(
            df_display.style.format({
                "1日乗降客数": "{:,} 人",
                "うち定期・直接利用": "{:,} 人",
                "うち乗換・通過加算": "{:,} 人",
                "乗換率(%)": "{:.1f} %",
                "周辺都会度(偏差値)": "{:.1f}",
                "駅勢圏人口(推計)": "{:,} 人"
            }),
            use_container_width=True,
            height=600
        )

        with st.expander("💡 このランキングの算出ロジック（都市工学・交通モデル）を見る"):
            st.markdown("""
            - **周辺の都会度（空間重力モデル）**：同じ「1路線しか通っていない駅」でも、周囲に東都・霧ヶ峰・西霧ヶ峰・朝凪などの大ターミナルが密集している駅（例：**速見駅・朝凪南駅・南新都町駅**など）は、山手線内の単独駅と同様に周辺ポテンシャルが高く評価され、郊外末端の単独駅（坂柳・緑山など）と比べて数倍の乗降客数になります。
            - **乗り換え客の集中（媒介中心性モデル）**：全36駅・1,260通りの最短経路をすべて計算し、実際に乗り換えが発生するハブ駅（**霧ヶ峰・東都・亀浜・西霧ヶ峰・朝凪**など）に乗り換え客がリアルに加算されます。
            - **施設・拠点ボーナス**：3人のプレイヤー拠点や空港・村人交易所・トラップなどの主要施設がある駅は、目的地としての吸引力（昼間流入人口）が高く設定されています。
            """)

    with tab_info:
        st.markdown("### 各路線の停車駅案内")
        selected_line = st.selectbox("路線を選択", list(LINES_STATIONS.keys()))
        if selected_line:
            stations_with_suffix = [f"{s}駅" for s in LINES_STATIONS[selected_line]]
            st.write(" → ".join(stations_with_suffix))
            if selected_line in ["霧ヶ峰線", "南辺線"]:
                st.caption("※霧ヶ峰線と南辺線は風見野駅で相互直通運転を行っています。")

        st.divider()

        st.markdown("### 駅の接続路線を調べる")
        selected_str = st.selectbox("駅を選択", station_options, key="station_info")
        target_sta = selected_str.split(' ')[0]
        
        if target_sta in station_lines:
            lines = sorted(list(station_lines[target_sta]))
            with st.container(border=True):
                st.markdown(f"**{target_sta}駅 ({station_kana[target_sta]})** の接続路線")
                for line in lines:
                    st.markdown(f"- {line}")

        st.divider()

        st.markdown("### 施設・拠点から最寄り駅を探す")
        with st.expander("主要施設・拠点一覧を表示", expanded=True):
            for sta in sorted_stations:
                if sta in facilities:
                    st.markdown(f"- **{sta}駅** …… {facilities[sta]}")

if __name__ == "__main__":
    main()