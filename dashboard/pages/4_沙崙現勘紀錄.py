import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from style import *
from data_io import PROC

st.set_page_config(page_title="沙崙現勘紀錄", layout="wide")
st.title("沙崙現勘紀錄")
st.caption("2026/11/11（週三）08:39–18:28，團隊 1 人在沙崙站三樓大廳現場計數")

VIDEO = Path(__file__).resolve().parents[1] / "assets" / "shalun_replay.mp4"
HOURLY = PROC / "shalun_hourly.csv"


@st.cache_data
def load_hourly():
    return pd.read_csv(HOURLY, dtype={"hour": str})


col1, col2 = st.columns([2, 1])

with col1:
    if VIDEO.exists():
        st.video(str(VIDEO), muted=True, loop=True)
        st.caption("影片 1 秒約等於實際 8 分鐘；一個點＝一位旅客")
    else:
        st.warning("找不到回放影片（dashboard/assets/shalun_replay.mp4）。")

with col2:
    st.metric("出站往高鐵方向", "約八成以上")
    st.caption("含高鐵、Outlet、會展，不是轉乘比例")
    st.metric("候車座位", "32 座")
    st.caption("觀察時段同時入座最多約 10 人")
    st.metric("每班車到站後出站", "約 90 人")
    st.caption("21 班中位數")

st.subheader("逐時剪票口進出站")
if HOURLY.exists():
    h = load_hourly()
    labels = [f"{hr}*" if m < 60 else hr for hr, m in zip(h["hour"], h["observed_min"])]
    i_in = h["gate_in"].idxmax()
    i_out = h["gate_out"].idxmax()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=h["gate_in"], name="進站", marker_color="#2a78d6",
        text=[f"{v:,}" if i == i_in else "" for i, v in h["gate_in"].items()],
        textposition="outside",
        hovertemplate="%{x} 點 進站：%{y:,} 人次<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=labels, y=h["gate_out"], name="出站", marker_color="#eb6834",
        text=[f"{v:,}" if i == i_out else "" for i, v in h["gate_out"].items()],
        textposition="outside",
        hovertemplate="%{x} 點 出站：%{y:,} 人次<extra></extra>",
    ))
    fig.update_layout(base_layout())
    fig.update_layout(barmode="group", height=400,
                      legend=dict(orientation="h", y=1.1, x=0))
    fig.update_xaxes(title="時", type="category")
    fig.update_yaxes(title="人次",
                     range=[0, max(h["gate_in"].max(), h["gate_out"].max()) * 1.15])
    st.plotly_chart(fig, width="stretch")
    st.caption("* 觀察不足 1 小時（08 點 21 分鐘、11–12 點中斷 14 分鐘、18 點 28 分鐘）")
else:
    st.warning("找不到逐時資料（data/processed/shalun_hourly.csv）。")

st.info(
    "**限制**\n"
    "- 單一平日、觀察者 1 人；計數有漏，比例只取概數\n"
    "- 「往高鐵方向」含轉乘高鐵、Outlet、會展中心，當天沒有分開記，不是轉乘高鐵比例\n"
    "- 當天是 TASTI 2026（大臺南會展中心）最後一天，人次可能偏高\n"
    "- 10 小時剪票口約 3,655 人次，不能和官方全日平均（週三 5,089）直接比"
)

st.markdown(
    "沙崙在稅籍版名單上（潛力 100／供給 0），臺鐵 115 年 2 月出租表為「無」；"
    "現場也看到站內沒有零售空間，臺鐵便當櫃設在高鐵台南站大廳。"
)
st.markdown("計數由團隊現場執行；計數工具與回放影片由 AI 協助製作。")

st.divider()
st.caption("資料來源：本團隊 2026/11/11 沙崙站現場計數")