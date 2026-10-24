import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import io

# 日本語フォントの設定（Windows / Mac / Linux 自動対応）
plt.rcParams['font.sans-serif'] = [
    'Meiryo', 'Yu Gothic', 'MS Gothic', 'Hiragino Sans', 'Hiragino Kaku Gothic ProN',
    'IPAexGothic', 'IPAGothic', 'Noto Sans CJK JP', 'VL Gothic', 'DejaVu Sans'
]
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 1. 路線・駅名・施設・座標データ (ver4.1)
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
    "霧ヶ峰線": ["蒼海宮", "亀浜", "西霧ヶ峰", "霧ヶ峰湖"],
    "新都心線": ["終宮", "亀浜", "新都町", "朝凪", "東都"],
    "中央都市線": ["速見", "霧ヶ峰", "西霧ヶ峰", "南新都町", "朝凪南", "朝凪"],
    "東都線": ["東都", "朝凪", "七瀬", "坂柳"],
    "南辺線": ["風見野", "前哨基地"],
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
        "新都心線": "#8B4513",
        "中央都市線": "#228B22",
        "東都線": "#00CED1",
        "南辺線": "#8A2BE2",
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
            ("蒼海宮", "亀浜", 197), ("亀浜", "西霧ヶ峰", 22), ("西霧ヶ峰", "霧ヶ峰湖", 40)
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
        "南辺線": [
            ("風見野", "前哨基地", 62)
        ],
        "中央新幹線": [
            ("白浜崎", "新蒼海宮", 44)
        ],
        "晴海坂線": [
            ("砂炭江", "晴海坂", 57), ("晴海坂", "東晴海坂", 25)
        ]
    }

# 直交グリッド座標データ (中央線＝縦軸 X=4, 桜町線＝横軸 Y=10 で垂直に交差)
def get_base_station_coords():
    return {
        "一ノ瀬": (4, 15), "境港": (4, 13), "谷上町": (4, 11.2), "第1拠点": (4, 8.2),
        "晴海坂": (4, 6.5), "滝沢": (4, 4.8), "終宮": (4, 3.2), "新蒼海宮": (4, 1.6),
        "蒼海宮": (4, 0), "東晴海坂": (2, 6.5),
        "荒山村": (0, 10), "桜町一丁目": (2, 10), "谷上三丁目": (4, 10), "白浜崎": (6.5, 10),
        "砂炭江": (9, 10), "霧ヶ峰": (12, 10), "霧ヶ峰湖": (14.5, 10), "東都": (17, 10),
        "風見野": (19.5, 10), "北茜ヶ原": (21.5, 10), "茜ヶ原": (23.5, 10), "南部海岸": (25.5, 10),
        "ポータルシティ": (27.5, 10),
        "桜坂": (6.5, 15), "緑山": (9, 15), "旭ヶ丘": (12, 13), "速見": (10.5, 11.5),
        "西霧ヶ峰": (13.5, 6.5), "亀浜": (12, 3.2), "新都町": (15, 4.8), "南新都町": (13.5, 4.8),
        "朝凪南": (15, 6.5), "朝凪": (17, 6.5), "七瀬": (17, 3.2), "坂柳": (17, 1.0),
        "前哨基地": (19.5, 3.2)
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
# 2. 路線図描画関数（中央線×桜町線 垂直交差版）
# ==========================================
def draw_railway_map(highlight_stations=None, swap_axes=False):
    base_coords = get_base_station_coords()
    colors = get_line_colors()
    facilities = get_facilities()

    def tr(pt):
        return (pt[1], pt[0]) if swap_axes else (pt[0], pt[1])

    coords = {sta: tr(pt) for sta, pt in base_coords.items()}

    fig_size = (16, 22) if swap_axes else (22, 14)
    fig, ax = plt.subplots(figsize=fig_size, dpi=150)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')
    ax.grid(True, which='both', color='#E2E8F0', linestyle='-', linewidth=0.8, zorder=0)

    def plot_route(pts, color, lw=5, ls='-', zorder=3, label=None):
        t_pts = [tr(p) for p in pts]
        xs = [p[0] for p in t_pts]
        ys = [p[1] for p in t_pts]
        ax.plot(xs, ys, color=color, linewidth=lw, linestyle=ls,
                solid_capstyle='round', solid_joinstyle='round', zorder=zorder, label=label)

    # 1. 中央線
    plot_route([base_coords[s] for s in LINES_STATIONS["中央線"]], colors["中央線"], lw=6.5, zorder=4, label="中央線")

    # 2. 桜町線(各停)
    s_local = LINES_STATIONS["桜町線(各停)"]
    plot_route([(base_coords[s][0], 10.14) for s in s_local], colors["桜町線(各停)"], lw=5.5, zorder=4, label="桜町線(各停)")

    # 3. 桜町線(快速)
    s_rapid = LINES_STATIONS["桜町線(快速)"]
    plot_route([(base_coords[s][0], 9.86) for s in s_rapid], colors["桜町線(快速)"], lw=5.5, zorder=4, label="桜町線(快速)")

    # 4〜12. 各路線（1行記述で構文エラーを防止）
    plot_route([(9, 10), (9, 6.5), (4, 6.5), (2, 6.5)], colors["晴海坂線"], lw=4.5, label="晴海坂線")
    plot_route([(6.5, 10), (6.5, 1.6), (4, 1.6)], colors["中央新幹線"], lw=4.5, ls='--', label="中央新幹線")
    plot_route([(4, 15), (6.5, 15), (9, 15), (12, 15), (12, 13), (12, 10), (12, 3.2)], colors["東西線"], lw=5, label="東西線")
    plot_route([(4, 0), (12, 0), (12, 3.2), (13.5, 3.2), (13.5, 6.5), (14.5, 6.5), (14.5, 10)], colors["霧ヶ峰線"], lw=4.5, label="霧ヶ峰線")
    plot_route([(4, 3.2), (12, 3.2), (12, 4.8), (15, 4.8), (16.88, 4.8), (16.88, 6.5), (16.88, 10)], colors["新都心線"], lw=5, label="新都心線")
    plot_route([(10.5, 11.5), (12, 10), (13.5, 10), (13.5, 6.5), (13.5, 4.8), (14.2, 4.8), (15, 6.5), (17, 6.5)], colors["中央都市線"], lw=4.5, label="中央都市線")
    plot_route([(13.5, 6.5), (15, 4.8), (15, 3.2), (17, 3.2), (19.5, 3.2)], colors["南北線"], lw=4.5, label="南北線")
    plot_route([(17.12, 10), (17.12, 6.5), (17.12, 3.2), (17.12, 1.0)], colors["東都線"], lw=5, label="東都線")
    plot_route([(19.5, 10), (19.5, 3.2)], colors["南辺線"], lw=4.5, label="南辺線")

    # 徒歩連絡
    plot_route([(4, 11.2), (4, 10)], "#4CAF50", lw=3, ls=':', zorder=5, label="徒歩連絡")
    plot_route([(15, 4.8), (13.5, 4.8)], "#4CAF50", lw=3, ls=':', zorder=5)

    # 駅の描画
    station_lines_count = {}
    for line, stas in LINES_STATIONS.items():
        for s in stas:
            station_lines_count[s] = station_lines_count.get(s, 0) + 1

    rapid_stops = set(LINES_STATIONS["桜町線(快速)"])
    local_stops = set(LINES_STATIONS["桜町線(各停)"])

    for sta, (bx, by) in base_coords.items():
        x, y = coords[sta]
        is_transfer = station_lines_count.get(sta, 0) > 1
        is_highlighted = highlight_stations and sta in highlight_stations

        if sta in local_stops or sta in rapid_stops:
            if sta in local_stops and sta in rapid_stops:
                rx = x - 0.2 if not swap_axes else 9.72
                ry = 9.72 if not swap_axes else y - 0.2
                rw = 0.4 if not swap_axes else 0.56
                rh = 0.56 if not swap_axes else 0.4
                rect = mpatches.FancyBboxPatch(
                    (rx, ry), rw, rh,
                    boxstyle="round,pad=0.05,rounding_size=0.15",
                    facecolor="#FFF9C4" if is_highlighted else "white",
                    edgecolor="#FF0000" if is_highlighted else "#1E293B",
                    linewidth=3 if is_highlighted else 2.2, zorder=6
                )
                ax.add_patch(rect)
            elif sta in local_stops:
                lx, ly = tr((bx, 10.14))
                ax.scatter(lx, ly, s=170, facecolor="#FFF9C4" if is_highlighted else "white",
                           edgecolor="#FF0000" if is_highlighted else colors["桜町線(各停)"],
                           linewidth=2.5, zorder=6)
                if is_transfer:
                    ax.scatter(lx, ly, s=230, facecolor="white", edgecolor="#1E293B", linewidth=2.2, zorder=6)
            elif sta in rapid_stops:
                rx, ry = tr((bx, 9.86))
                ax.scatter(rx, ry, s=180, facecolor="#FFF9C4" if is_highlighted else "white",
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

        if not swap_axes:
            if sta in ["境港", "第1拠点", "滝沢", "終宮", "新蒼海宮", "蒼海宮"]:
                offset_x, offset_y, ha, va = -0.45, 0.0, 'right', 'center'
            elif sta == "谷上町":
                offset_x, offset_y, ha, va = -0.45, 0.1, 'right', 'center'
            elif sta == "晴海坂":
                offset_x, offset_y, ha, va = 0.45, 0.25, 'left', 'bottom'
            elif sta == "東晴海坂":
                offset_x, offset_y, ha, va = 0.0, 0.38, 'center', 'bottom'
            elif sta == "谷上三丁目":
                offset_x, offset_y, ha, va = -0.35, -0.48, 'right', 'top'
            elif sta in ["荒山村", "桜町一丁目", "白浜崎", "砂炭江", "霧ヶ峰湖", "東都", "風見野", "北茜ヶ原", "茜ヶ原"]:
                offset_x, offset_y, ha, va = 0.0, 0.48, 'center', 'bottom'
            elif sta == "霧ヶ峰":
                offset_x, offset_y, ha, va = -0.35, 0.48, 'right', 'bottom'
            elif sta in ["南部海岸", "ポータルシティ"]:
                offset_x, offset_y, ha, va = 0.0, -0.45, 'center', 'top'
            elif sta in ["旭ヶ丘", "西霧ヶ峰"]:
                offset_x, offset_y, ha, va = -0.4, 0.0, 'right', 'center'
            elif sta == "南新都町":
                offset_x, offset_y, ha, va = -0.4, -0.1, 'right', 'center'
            elif sta == "新都町":
                offset_x, offset_y, ha, va = 0.35, -0.25, 'left', 'top'
            elif sta == "朝凪南":
                offset_x, offset_y, ha, va = 0.0, 0.38, 'center', 'bottom'
            elif sta in ["朝凪", "七瀬", "坂柳", "前哨基地"]:
                offset_x, offset_y, ha, va = 0.45, 0.0, 'left', 'center'
            elif sta == "亀浜":
                offset_x, offset_y, ha, va = -0.4, -0.35, 'right', 'top'
        else:
            if sta in ["一ノ瀬", "境港", "谷上町", "第1拠点", "晴海坂", "滝沢", "終宮", "新蒼海宮", "蒼海宮"]:
                offset_x, offset_y, ha, va = 0.0, 0.45, 'center', 'bottom'
            elif sta in local_stops or sta in rapid_stops:
                offset_x, offset_y, ha, va = 0.5, 0.0, 'left', 'center'

        label_text = f"★{sta}" if sta in facilities else sta
        bbox_props = dict(boxstyle="round,pad=0.2", fc="#FEF08A" if is_highlighted else "white",
                          ec="#F59E0B" if is_highlighted else "none", alpha=0.88)

        ax.text(x + offset_x, y + offset_y, label_text, fontsize=10.5, fontweight='bold',
                color='#0F172A', ha=ha, va=va, zorder=8, bbox=bbox_props)

    ax.set_title("水素鉄道 路線図 (ver4.1 - 中央線・桜町線 直交レイアウト)", fontsize=18, fontweight='bold', pad=15, color='#0F172A')
    if not swap_axes:
        ax.set_xlim(-1.5, 29.5)
        ax.set_ylim(-1.5, 16.5)
    else:
        ax.set_xlim(-1.5, 16.5)
        ax.set_ylim(-1.5, 29.5)
    ax.axis('off')

    legend_elements = [Line2D([0], [0], color=c, lw=5, label=name) for name, c in colors.items()]
    legend_elements.append(Line2D([0], [0], color="#4CAF50", lw=3, ls=":", label="徒歩連絡"))
    ax.legend(handles=legend_elements, loc='lower left', ncol=4, fontsize=10,
              frameon=True, facecolor='white', edgecolor='#CBD5E1', title="路線凡例 (★は主要施設あり)")

    plt.tight_layout()
    return fig

# ==========================================
# 3. 経路検索グラフ構築 (ver4.1)
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
# 4. UIメイン処理
# ==========================================
def main():
    st.set_page_config(page_title="Minecraft鉄道 乗り換え案内 ver4.1", layout="wide")
    st.title("🚃 水素鉄道 乗り換え案内 ＆ 路線図メーカー ver4.1")
    
    G_base, station_lines = build_graph()
    station_kana = get_station_kana()
    facilities = get_facilities()
    line_colors = get_line_colors()
    
    sorted_stations = sorted(list(station_lines.keys()), key=lambda x: station_kana.get(x, x))
    station_options = [f"{s} ({station_kana.get(s, '')})" for s in sorted_stations]

    tab_search, tab_map, tab_info = st.tabs(["🔍 経路検索", "🗺️ 路線図（画像保存）", "🏢 各路線・駅・施設一覧"])

    highlight_stas = set()

    with tab_search:
        st.markdown("### 出発・到着駅と条件を選択")
        col1, col2 = st.columns(2)
        
        default_start = [opt for opt in station_options if opt.startswith("荒山村")][0] if any(opt.startswith("荒山村") for opt in station_options) else station_options[0]
        default_end = [opt for opt in station_options if opt.startswith("東都 ")][0] if any(opt.startswith("東都 ") for opt in station_options) else station_options[1]
        
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
                            st.markdown(f"<div style='text-align: center; color: #ff4b4b; font-weight: bold; margin: 15px 0;'>✨ {step['from']}駅から直通（そのまま乗車）</div>", unsafe_allow_html=True)
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
        orientation = st.radio(
            "路線図の向きを選択",
            ["パターンA：桜町線が横（東西）・中央線が縦（南北）", "パターンB：中央線が横（東西）・桜町線が縦（南北）"],
            horizontal=True
        )
        swap_axes = "パターンB" in orientation

        fig = draw_railway_map(highlight_stations=highlight_stas if highlight_stas else None, swap_axes=swap_axes)
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
        buf.seek(0)
        st.download_button(
            label="📥 路線図を高画質PNG画像としてダウンロード",
            data=buf,
            file_name="suiso_railway_map_v4_1.png",
            mime="image/png",
            type="primary"
        )

    with tab_info:
        st.markdown("### 各路線の停車駅案内")
        selected_line = st.selectbox("路線を選択", list(LINES_STATIONS.keys()))
        if selected_line:
            stations_with_suffix = [f"{s}駅" for s in LINES_STATIONS[selected_line]]
            st.write(" → ".join(stations_with_suffix))

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