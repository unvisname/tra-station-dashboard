import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from style import *
from data_io import load_station

st.set_page_config(page_title="潛力供給矩陣", layout="wide")
st.title("潛力供給矩陣")
st.caption("左上角＝人流潛力高、周邊餐飲供給少：被低估、值得先去看的車站。")

df = load_station()

c1, c2, c3, c4 = st.columns([2, 3, 3, 2])
clusters = list(CLUSTER_ORDER)
cluster = c1.selectbox("群", clusters, index=clusters.index("通勤型"))
p_thr = c2.slider("潛力門檻（群內百分位 ≥）", 0, 100, 50)
s_thr = c3.slider("供給門檻（群內百分位 ≤）", 0, 100, 25)
min_flow = c4.selectbox("站流下限（日均人次 ≥）", [0, 100, 300, 500, 1000], index=0)


def apply_list(frame):
    return (frame["potential_pct"] >= p_thr) & (frame["supply_pct_tax"] <= s_thr)


d = df[(df["cluster_name"] == cluster) & (df["mean_total"] >= min_flow)].copy()
d["on_list_now"] = apply_list(d)
d["lease_txt"] = np.where(d["tra_lease"] == 1, "有", "無")
d["sub_txt"] = d["subtype"].fillna("—")

n_list = int(d["on_list_now"].sum())
share = n_list / len(d) * 100 if len(d) else 0

all_d = df[df["mean_total"] >= min_flow]
n_all = int(apply_list(all_d).sum())

HOVER = ("<b>%{customdata[0]}</b><br>"
         "子型：%{customdata[1]}<br>"
         "日均人次：%{customdata[2]:,.0f}<br>"
         "1 km 人口：%{customdata[3]:,.0f}<br>"
         "稅籍餐飲（1 km，估）：%{customdata[4]:,.0f}<br>"
         "Google 餐廳（1 km）：%{customdata[6]:,.0f}<br>"
         "臺鐵出租：%{customdata[5]}<br>"
         "潛力 %{y:.0f}／供給 %{x:.0f}<extra></extra>")

left, right = st.columns([3, 1])

with right:
    st.metric("名單站", f"{n_list} 站")
    st.caption(f"占群內 {share:.0f}%（顯示中 {len(d)} 站）")
    st.caption(f"五群合計：{n_all} 站")

with left:
    fig = go.Figure()
    for is_list, color, label in [(False, "#2a78d6", "其他站"), (True, "#eb6834", "名單站")]:
        p = d[d["on_list_now"] == is_list]
        fig.add_trace(go.Scatter(
            x=p["supply_pct_tax"], y=p["potential_pct"], mode="markers", name=label,
            marker=dict(color=color, size=10 if is_list else 7, opacity=0.85),
            customdata=p[["name", "sub_txt", "mean_total", "pop_1km",
                          "food_tax_1km", "lease_txt", "gm_food_1km"]].values,
            hovertemplate=HOVER,
        ))
    fig.add_vline(x=s_thr, line_dash="dash", line_color="#898781")
    fig.add_hline(y=p_thr, line_dash="dash", line_color="#898781")
    fig.add_annotation(x=0, y=101, xref="x", yref="y", text="被低估",
                       showarrow=False, xanchor="left", yanchor="top",
                       font=dict(size=15, color="#eb6834"))
    fig.update_layout(base_layout())
    fig.update_layout(height=520, legend=dict(orientation="h", y=1.08, x=0))
    fig.update_xaxes(title="供給百分位（稅籍餐飲 ÷ 每萬人次，群內）", range=[-3, 103])
    fig.update_yaxes(title="潛力百分位（日均人次 ÷ 1 km 人口，群內）", range=[-3, 103])
    st.plotly_chart(fig, use_container_width=True)
    if cluster == "寒暑假觀光型（集集線）":
        st.caption("站數少，僅供參考。")

st.subheader("名單")
t = d[d["on_list_now"]].sort_values("potential_pct", ascending=False)
out = pd.DataFrame({
    "站名": t["name"],
    "子型": t["sub_txt"],
    "日均人次": t["mean_total"].round(0),
    "潛力百分位": t["potential_pct"].round(1),
    "供給百分位": t["supply_pct_tax"].round(1),
    "稅籍餐飲（1 km，估）": t["food_tax_1km"].round(0),
    "Google 餐廳（1 km）": t["gm_food_1km"],
    "臺鐵出租": t["lease_txt"],
    "提醒": np.where(t["tax_no_vill_share"] > 0.2, "地址資料不完整", ""),
})
st.dataframe(out, hide_index=True, use_container_width=True)
st.download_button(
    "下載 CSV",
    out.to_csv(index=False).encode("utf-8-sig"),
    file_name=f"名單_{cluster}_潛力{p_thr}_供給{s_thr}.csv",
    mime="text/csv",
)

with st.expander("說明"):
    st.markdown(
        "- **潛力**＝日均進出站人次 ÷ 1 km 人口，在同一群內換成百分位（0–100）。\n"
        "- **供給**＝1 km 內稅籍餐飲家數（依村里面積加權粗估）÷ 每萬人次，在同一群內換成百分位。\n"
        "- 名單條件：潛力 ≥ 門檻 且 供給 ≤ 門檻；預設 50／25 出自企劃書。\n"
        "- 百分位是群內算的，所以矩陣一次只畫一群。\n"
        "- 對照：改用 OSM 餐飲時名單 34 站，兩版重疊 20 站。OSM 偏鄉漏登較多，所以改以稅籍為主。\n"
        "- Google 餐廳數是輔助參考（2026/11/7 以「餐廳」搜尋，1 km 內去重，只用家數），"
        "清單有載入上限，請讀成「至少 N 家」；235 站與稅籍排序相關 0.83。\n"
        "- 「地址資料不完整」：稅籍地址沒寫村里的比例超過 20%，這些站的稅籍估計較不準。"
    )

st.divider()
st.markdown(FOOTER, unsafe_allow_html=True)
st.caption(DATA_ASOF)