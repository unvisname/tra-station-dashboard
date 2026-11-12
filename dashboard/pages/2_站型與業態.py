import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from style import *
from data_io import load_clusters, load_business
from components import business_table_html

st.set_page_config(page_title="臺鐵車站行為分群", page_icon="🚉", layout="wide")

df = load_clusters()
business = load_business()

names = sorted(df["name"])
name = st.selectbox("車站", names, index=names.index("汐科"))

SIZE_LABEL = {">=10000": "日均 ≥ 1 萬", "<10000": "日均 < 1 萬"}
row = df[df["name"] == name].iloc[0]

if row["cluster_name"] == "通勤型":
    label = "通勤型 >1 萬" if row["mean_total"] >= 10000 else "通勤型 <1 萬"
elif row["cluster_name"].startswith("寒暑假"):
    label = "寒暑假觀光型"  
else:
    label = row["cluster_name"]

biz = business[business["label"] == label].iloc[0]

color = CLUSTER_COLOR[row["cluster_name"]]

head, m1, m2, m3 = st.columns([2, 1, 1, 1])

with head:
    st.markdown(
        f'<span style = "background:{color};color:#fff;'
        f'padding: 4px 10px; border-radius:6px">{row["cluster_name"]}</span>'
        f'　<span style="color:#898781">{SIZE_LABEL[row["size_band"]]}</span>',
        unsafe_allow_html=True,
    )

m1.metric("日均", f"{row['mean_total']:,.0f}")
m2.metric("週末比", f"{row['f2a_weekend_ratio']:.2f}")
m3.metric("週五比", f"{row['f2b_friday_ratio']:.2f}")

st.write("**人流性質（此站型平均）**：", biz["flow_profile"])

left, right = st.columns(2)

with left:
    st.markdown("#### 適合業態")
    st.markdown("\n".join(f"- {x}" for x in biz["suitable"].split("、")))

with right:
    st.markdown("#### 不適合")
    st.markdown("\n".join(f"- {x}" for x in biz["unsuitable"].split("、")))

st.write("**對照案例**：", biz["reference"])

st.markdown("#### 同型車站（前 10，依日均）")

if label.startswith("通勤型"):
    same = df[(df["cluster_name"] == "通勤型") & (df["size_band"] == row["size_band"])]
else:
    same = df[df["cluster_name"] == row["cluster_name"]]

st.dataframe(
    same.nlargest(10, "mean_total")[["name", "mean_total", "f2a_weekend_ratio"]]
        .rename(columns={"name": "站名", "mean_total": "日均", "f2a_weekend_ratio": "週末比"}),
    hide_index=True,
    column_config={
        "日均": st.column_config.NumberColumn(format="%,.0f"),
        "週末比": st.column_config.NumberColumn(format="%.2f"),
    },
)

with st.expander("完整業態表（六種站型）", expanded=False):
    st.markdown(business_table_html(business, current_label=label), unsafe_allow_html=True)
    st.caption("站型依分群結果與規模帶；業態為本作品建議；群特徵數字為群內中位數（首頁群表為平均值）")

st.caption(FOOTER)