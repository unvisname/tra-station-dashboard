import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from style import *
from data_io import load_station, load_daily_all, load_subtype_advice

st.set_page_config(page_title="車站體檢卡", layout="wide")
st.title("車站體檢卡")
st.caption("任選一站，一頁看完人流、生活圈與招商建議")

FULL_DAYS = pd.date_range(WINDOW[0], WINDOW[1], freq="D")
X_TITLE = "供給百分位（稅籍餐飲 ÷ 每萬人次，群內）"
Y_TITLE = "潛力百分位（日均人次 ÷ 1 km 人口，群內）"

df = load_station()
daily = load_daily_all()
advice = load_subtype_advice()


def badge(text, color):
    return (f'<span style="background:{color};color:#fff;padding:3px 12px;'
            f'border-radius:12px;font-size:0.95em">{text}</span>')


def fmt(v, spec):
    return "—" if pd.isna(v) else f"{v:{spec}}"


names = sorted(df["name"])
station = st.selectbox("選擇車站", names, index=names.index("沙崙"))
row = df[df["name"] == station].iloc[0]
cluster = row["cluster_name"]
c_color = CLUSTER_COLOR[cluster]
subtype = row["subtype"]
s = daily[daily["sta_code"] == row["sta_code"]].sort_values("date")

h1, h2, h3, h4 = st.columns(4)
with h1:
    st.subheader(f"{station}站")
    st.markdown(badge(cluster, c_color), unsafe_allow_html=True)
with h2:
    st.caption("子型")
    st.markdown(badge(subtype, SUBTYPE_COLOR.get(subtype, SUBTYPE_GREY)),
                unsafe_allow_html=True)
h3.metric("潛力供給名單", "是" if row["on_list_tax"] == 1 else "否")
h4.metric("臺鐵出租空間", "有" if row["tra_lease"] == 1 else "無",
          help="臺鐵 115 年 2 月旅運販賣空間出租表；只有有／無")
if station == "沙崙":
    st.page_link("pages/4_沙崙現勘紀錄.py", label="看沙崙現勘紀錄 →")

st.subheader("人流")

ts = s.set_index("date")["total"].reindex(FULL_DAYS)
ma = ts.rolling(28, min_periods=14).mean()

fig_a = go.Figure()
fig_a.add_trace(go.Scatter(
    x=ts.index, y=ts.values, mode="lines", name="每日",
    line=dict(color=c_color, width=1), opacity=0.35,
    hovertemplate="%{x|%Y/%m/%d}：%{y:,.0f} 人次<extra></extra>",
))
fig_a.add_trace(go.Scatter(
    x=ma.index, y=ma.values, mode="lines", name="28 日平均",
    line=dict(color=c_color, width=2.5),
    hovertemplate="%{x|%Y/%m/%d} 28 日平均：%{y:,.0f}<extra></extra>",
))
fig_a.add_vrect(x0=QUAKE[0], x1=QUAKE[1], fillcolor=CONTRAST_GREY, opacity=0.12,
                line_width=0, annotation_text="0403 地震影響期間",
                annotation_position="top left")
if cluster != "通勤型" and ts.notna().any():
    peak = ts.idxmax()
    fig_a.add_annotation(x=peak, y=ts[peak],
                         text=f"最高 {peak:%Y/%m/%d}<br>{ts[peak]:,.0f} 人次",
                         showarrow=True, arrowhead=2, ax=0, ay=-40)
fig_a.update_layout(base_layout())
fig_a.update_layout(
    title=f"{station}｜{cluster}　逐日進出站人次 2024/1–2026/7",
    height=420, legend=dict(orientation="h", y=1.1, x=0),
)
fig_a.update_yaxes(title="人次")
st.plotly_chart(fig_a, width="stretch")

n_days = s["date"].nunique()
if n_days < len(FULL_DAYS):
    st.caption(f"這站有 {len(FULL_DAYS) - n_days} 天沒有資料，曲線有斷點。")

col_b, col_c = st.columns(2)

with col_b:
    dow = s.groupby("dow")["total"].mean().reindex(range(7))
    fig_b = go.Figure(go.Bar(
        x=DOW_LABEL, y=dow.values, marker_color=c_color,
        marker_opacity=[1] * 5 + [0.45] * 2,
        hovertemplate="週%{x}：%{y:,.0f} 人次<extra></extra>",
    ))
    fig_b.update_layout(base_layout())
    fig_b.update_layout(
        title=(f"星期型態（日均人次）<br><sub>週末比 {fmt(row['f2a_weekend_ratio'], '.2f')}"
               f"｜週五比 {fmt(row['f2b_friday_ratio'], '.2f')}</sub>"),
        height=360, showlegend=False,
    )
    st.plotly_chart(fig_b, width="stretch")

with col_c:
    mon = s.groupby(["year", "month"])["total"].mean().reset_index()
    years = sorted(mon["year"].unique())
    greys = ["#c9c7c0", "#a3a19a"]
    fig_c = go.Figure()
    for i, y in enumerate(years):
        m = mon[mon["year"] == y]
        last = i == len(years) - 1
        fig_c.add_trace(go.Scatter(
            x=m["month"], y=m["total"], mode="lines+markers", name=str(y),
            line=dict(color=c_color if last else greys[i % len(greys)],
                      width=2.5 if last else 1.8),
            hovertemplate=f"{y} 年" + " %{x} 月：%{y:,.0f} 人次<extra></extra>",
        ))
    fig_c.update_layout(base_layout())
    fig_c.update_layout(title="月別（日均人次）", height=360,
                        legend=dict(orientation="h", y=1.12, x=0))
    fig_c.update_xaxes(tickvals=list(range(1, 13)),
                       ticktext=[f"{k}月" for k in range(1, 13)])
    st.plotly_chart(fig_c, width="stretch")

st.subheader("生活圈（1 km）")
r1 = st.columns(4)
r1[0].metric("1 km 人口", fmt(row["pop_1km"], ",.0f"),
             help="戶籍 2024-12，最小統計區面積加權")
r1[1].metric("稅籍餐飲（估）", fmt(row["food_tax_1km"], ",.0f"),
             help="財政部稅籍登記，村里面積加權粗估")
r1[2].metric("OSM 餐飲", fmt(row["food_osm_1km"], ",.0f"),
             help="偏鄉漏登較多")
r1[3].metric("Google 餐廳（至少）", fmt(row["gm_food_1km"], ",.0f"),
             help="2026/11/7 搜尋「餐廳」，清單有載入上限")
r2 = st.columns(4)
r2[0].metric("建築用地占比", fmt(row["built_share"], ".0%"), help="國土利用調查")
r2[1].metric("商業占建築用地", fmt(row["bsh_comm"], ".0%"))
r2[2].metric("住宅占建築用地", fmt(row["bsh_resi"], ".0%"))
r2[3].metric("稅籍餐飲 ÷ 萬人次", fmt(row["supply_tax"], ",.1f"),
             help="矩陣供給軸的原始值")
if row["tax_no_vill_share"] > 0.2:
    st.caption("這站周邊稅籍地址有兩成以上沒寫村里，稅籍數字較不準。")

left, right = st.columns([3, 2])

with left:
    g = df[df["cluster_name"] == cluster]
    others = g[g["name"] != station]
    fig_m = go.Figure()
    fig_m.add_trace(go.Scatter(
        x=others["supply_pct_tax"], y=others["potential_pct"], mode="markers",
        marker=dict(color=CONTRAST_GREY, size=6, opacity=0.6), text=others["name"],
        hovertemplate="%{text}<br>潛力 %{y:.0f}／供給 %{x:.0f}<extra></extra>",
        showlegend=False,
    ))
    fig_m.add_trace(go.Scatter(
        x=[row["supply_pct_tax"]], y=[row["potential_pct"]], mode="markers",
        marker=dict(color="#0b0b0b", size=18), hoverinfo="skip", showlegend=False,
    ))
    fig_m.add_trace(go.Scatter(
        x=[row["supply_pct_tax"]], y=[row["potential_pct"]], mode="markers+text",
        marker=dict(color=c_color, size=14), text=[station],
        textposition="top center", cliponaxis=False,
        hovertemplate=f"{station}<br>" + "潛力 %{y:.0f}／供給 %{x:.0f}<extra></extra>",
        showlegend=False,
    ))
    fig_m.add_vline(x=25, line_dash="dash", line_color=CONTRAST_GREY)
    fig_m.add_hline(y=50, line_dash="dash", line_color=CONTRAST_GREY)
    fig_m.update_layout(base_layout())
    fig_m.update_layout(title=f"在{cluster}內的位置", height=360)
    fig_m.update_xaxes(title=X_TITLE, range=[-3, 103])
    fig_m.update_yaxes(title=Y_TITLE, range=[-3, 103])
    st.plotly_chart(fig_m, width="stretch")
    st.caption(f"潛力 {fmt(row['potential_pct'], '.0f')}／"
               f"供給 {fmt(row['supply_pct_tax'], '.0f')}（群內百分位）")

with right:
    st.subheader("招商建議")
    a = advice[(advice["cluster_name"] == cluster) & (advice["subtype"] == subtype)]
    if a.empty or not a.iloc[0]["main_proposal"]:
        st.info("這個子型的招商建議尚未填入")
    else:
        a = a.iloc[0]
        st.markdown(f"**主方案**：{a['main_proposal']}")
        st.markdown(f"**人流特性**：{a['flow_profile']}")
        st.markdown(f"**適合業態**：{a['suitable']}")
        st.markdown(f"**不適合業態**：{a['unsuitable']}")
        with st.expander("參考案例"):
            st.markdown(a["reference"] or "（尚未填入）")

st.divider()
st.markdown(FOOTER, unsafe_allow_html=True)
st.caption(DATA_ASOF)