import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.graph_objects as go

from style import *
from data_io import load_daily, load_summary, load_clusters, load_livingarea
st.set_page_config(page_title="臺鐵車站行為分群", page_icon="🚉", layout="wide")

daily = load_daily()
summary = load_summary()
clusters = load_clusters()
living = load_livingarea()

station = st.radio("案例站", CASES, horizontal=True)
overlay = st.checkbox("疊上南港對照") if station == "汐科" else False

row = clusters[clusters["name"] == station].iloc[0]
color = CLUSTER_COLOR[row["cluster_name"]]

s = daily[daily["name"] == station].sort_values("date")

fig_a = go.Figure()

if overlay:
    ng = daily[daily["name"] == "南港"].sort_values("date")
    fig_a.add_trace(go.Scatter(
        x=ng["date"], y=ng["total"], mode="lines", name="南港",
        line=dict(color=CONTRAST_GREY, width=0.8), opacity=0.8,
    ))

fig_a.add_trace(go.Scatter(
    x=s["date"], y=s["total"], mode="lines", name=station,
    line=dict(color=color, width=1),
))

roll = s.set_index("date")["total"].rolling(28, center=True, min_periods=14).mean()
fig_a.add_trace(go.Scatter(
    x=roll.index, y=roll.values, mode="lines", name="28 日移動平均",
    line=dict(color="#0b0b0b", width=1.5)
))

fig_a.add_vrect(
    x0=QUAKE[0], x1=QUAKE[1],
    fillcolor="#e1e0d9", opacity=0.5, line_width=0,
    annotation_text="0403 地震敏感度排除區間", annotation_position="top left",
)

if row["cluster_name"] != "通勤型":
    peak = s.loc[s["total"].idxmax()]
    fig_a.add_annotation(
        x=peak["date"], y=peak["total"],
        text=f"最高 {peak['date']:%Y/%m/%d}  {peak['total']:,.0f}",
        showarrow=True, arrowhead=2, ax=0, ay=-30,
    )

fig_a.update_layout(
    title=f"{station} | {row['cluster_name']} 逐日進出站人次 2024/1-2026/7",
    height=380,
    **base_layout(),
)

st.plotly_chart(fig_a, use_container_width=True)

col_b, col_c = st.columns(2)

with col_b:
    dow = summary[(summary["station"] == station) & (summary["kind"] == "dow")]
    dow = dow.set_index("key").reindex(DOW_LABEL)

    opacities = [1.0] * 5 + [0.55] * 2

    fig_b = go.Figure(go.Bar(
        x=DOW_LABEL, y=dow["value"],
        marker=dict(color=color, opacity=opacities),
    ))
    fig_b.update_layout(
        title=f"星期型態<br><sub>週末比 {row['f2a_weekend_ratio']:.2f}・週五比 {row['f2b_friday_ratio']:.2f}</sub>",
        height=340, **base_layout(),
    )
    st.plotly_chart(fig_b, use_container_width=True)

with col_c:
    mon = summary[(summary["station"] == station) & (summary["kind"] == "month")].copy()
    mon[["year", "month"]] = mon["key"].str.split("-", expand=True).astype(int)

    fig_c = go.Figure()
    for yr, op in [(2024, 0.45), (2025, 0.7), (2026, 1.0)]:
        m = mon[mon["year"] == yr].sort_values("month")
        fig_c.add_trace(go.Scatter(
            x=m["month"], y=m["value"], mode="lines+markers", name=str(yr),
            line=dict(color=color), opacity=op, marker=dict(size=5),
        ))
    fig_c.update_layout(
        title="月別日均（三年）", height=340,
        xaxis=dict(tickmode="linear", dtick=1, title="月"),
        **base_layout(),
    )
    st.plotly_chart(fig_c, use_container_width=True)

lv = living[living["station"] == station].iloc[0]

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("人口 500 m", f"{lv['pop_500']:,.0f}")
c2.metric("人口 1 km", f"{lv['pop_1km']:,.0f}")
c3.metric("POI 1 km", f"{lv['poi_1km']:,.0f}")
c4.metric("餐飲 1 km", f"{lv['food_1km']:,.0f}")
c5.metric("超商 500 m", f"{lv['conv_500']:,.0f}")
c6.metric("每坪中位數", f"{lv['price_ping']/10000:.0f} 萬",
          help=f"{lv['town']}，{lv['price_n']:,.0f} 筆")

d1, d2, *_ = st.columns(6)
d1.metric("站流 ÷ 1 km 人口", f"{row['mean_total'] / lv['pop_1km']:.2f}",
          help="大於 1 表示外來客為主")
d2.metric("餐飲 ÷ 萬人次", f"{lv['food_1km'] / row['mean_total'] * 10000:.0f}",
          help="每萬人次對應的餐飲店家數")

st.caption(
    "人口：戶籍 2024-12，最小統計區面積加權；"
    "POI：© OpenStreetMap contributors，2026-08-27，鄉區覆蓋偏低；"
    "房價：內政部實價登錄 2025 年，行政區層級"
)
st.caption(FOOTER)