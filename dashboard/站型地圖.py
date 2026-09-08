import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from style import *
from data_io import load_clusters, load_profile

st.set_page_config(page_title="臺鐵車站行為分群", page_icon="🚉", layout="wide")

df = load_clusters()

sel_clusters = st.sidebar.multiselect("車站類型", CLUSTER_ORDER, default=CLUSTER_ORDER)
min_total = st.sidebar.slider("日均運量至少", 0, 60000, 0, step=500)

names = sorted(df["name"])
sel_name = st.sidebar.selectbox("查看車站", names, index=names.index("汐科"))

shown = df[df["cluster_name"].isin(sel_clusters) & (df["mean_total"] >= min_total)]

shown = shown.assign(
    size_px=(shown["f1_log_scale"] - df["f1_log_scale"].min() + 0.3) ** 2 *6
)

fig = px.scatter_map(
    shown,
    lat="lat",
    lon="lon",
    color="cluster_name",
    size="size_px",
    hover_name="name",
    hover_data={
        "cluster_name": True,
        "mean_total": ":,.0f",
        "f2a_weekend_ratio": ":.2f",
        "f2b_friday_ratio": ":.2f",
        "lat": False,
        "lon": False,
        "size_px": False,
    },
    color_discrete_map=CLUSTER_COLOR,
    category_orders={"cluster_name": CLUSTER_ORDER},
    map_style="open-street-map",
    zoom=7,
    center={"lat": 23.6, "lon": 120.9},
    height=640,
)
fig.update_layout(**base_layout())
fig.update_layout(legend_title_text="站型",
                  legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,.85)"),
                  margin=dict(l=0, r=0, t=10, b=0))

row = df[df["name"] == sel_name].iloc[0]

fig.add_trace(go.Scattermap(
    lat=[row["lat"]], lon=[row["lon"]], mode="markers",
    marker=dict(size=24, color="#0b0b0b"), hoverinfo="skip", showlegend=False,
))
fig.add_trace(go.Scattermap(
    lat=[row["lat"]], lon=[row["lon"]], mode="markers",
    marker=dict(size=16, color=CLUSTER_COLOR[row["cluster_name"]]),
    name=f"選中：{sel_name}", hoverinfo="skip",
))

left, right = st.columns([3, 1])

profile = (
    load_profile()
    .set_index("cluster_name")
    .loc[CLUSTER_ORDER]
    .reset_index()
    [["cluster_name", "size", "mean_total", "f2a_weekend_ratio", "f2b_friday_ratio"]]
    .rename(columns={"cluster_name": "群", "size": "站數", "mean_total": "日均",
                     "f2a_weekend_ratio": "週末比", "f2b_friday_ratio": "週五比"})
)

st.caption("各群站數與群內平均值（2024/1–2026/7）")
st.dataframe(
    profile,
    hide_index=True,
    column_config={
        "日均": st.column_config.NumberColumn(format="%,.0f"),
        "週末比": st.column_config.NumberColumn(format="%.2f"),
        "週五比": st.column_config.NumberColumn(format="%.2f"),
    },
)

st.caption(FOOTER)

with left:
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader(sel_name)
    st.markdown(
        f'<span style="background:{CLUSTER_COLOR[row["cluster_name"]]};color:#fff;'
        f'padding:4px 10px;border-radius:6px">{row["cluster_name"]}</span>',
        unsafe_allow_html=True,
    )
    st.metric("日均進出", f"{row['mean_total']:,.0f}",
              help="2024/1-2026/7 每日進站＋出站人次平均")
    st.metric("週末比", f"{row['f2a_weekend_ratio']:.2f}",
              help="週末日均 ÷ 平日（週一至週四）日均")
    st.metric("週五比", f"{row['f2b_friday_ratio']:.2f}",
              help="週五日均 ÷ 平日平均")
    st.metric("月別振幅", f"{row['f4a_month_amplitude']:.2f}",
              help="全年最高月日均 ÷ 最低月日均")

    n_same = (df["cluster_name"] == row["cluster_name"]).sum()
    st.caption(f"同為{row['cluster_name']}的車站共 {n_same} 站")