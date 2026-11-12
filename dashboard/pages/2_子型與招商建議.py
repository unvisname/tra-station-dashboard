import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from style import *
from data_io import load_station, load_subtype_rules, load_subtype_advice

st.set_page_config(page_title="子型與招商建議", layout="wide")
st.title("子型與招商建議")
st.caption("同一站型內，依土地使用與產業組成的規則再細分子型，對應不同的招商主方案。")

NO_SPLIT_CLUSTERS = ("春季活動型", "寒暑假觀光型（集集線）")
PCT_FEATS = {"built_share", "bsh_comm", "bsh_resi", "office_share",
             "retfood_share", "nature_share"}
LOG_FEATS = {"mean_total"}
OP_TXT = {">=": "≥", "<": "<"}


def fmt_thr(feat, thr):
    if feat in PCT_FEATS:
        return f"{thr * 100:g}%"
    if feat == "mean_total":
        return f"{thr:,.0f}"
    return f"{thr:g}"


def one_cond(row):
    return f"{row['label']} {OP_TXT[row['op']]} {fmt_thr(row['feature'], row['threshold'])}"


def rule_text(r):
    parts, seen = [], set()
    for _, row in r.iterrows():
        g = row["or_group"]
        if g:
            if g in seen:
                continue
            seen.add(g)
            grp = r[r["or_group"] == g]
            parts.append("（" + " 或 ".join(one_cond(x) for _, x in grp.iterrows()) + "）")
        else:
            parts.append(one_cond(row))
    return "、".join(parts)


df = load_station()
rules = load_subtype_rules()
advice = load_subtype_advice()

if df["subtype"].isna().all():
    st.warning("subtype 還是空的：請先跑 st_04_subtype_rules.py，再跑 db_01_merge.py。")
    st.stop()

c1, c2 = st.columns(2)
clusters = list(CLUSTER_ORDER)
cluster = c1.selectbox("群", clusters, index=clusters.index("通勤型"))
d = df[df["cluster_name"] == cluster].copy().reset_index(drop=True)
order = SUBTYPE_ORDER[cluster]
pick = c2.selectbox("找車站", ["（不選）"] + d["name"].tolist())
sel = None if pick == "（不選）" else pick

counts = d["subtype"].value_counts().reindex(order, fill_value=0)
if counts.sum() != len(d):
    st.error(f"子型站數加總 {counts.sum()} ≠ 群內站數 {len(d)}，請檢查子型檔。")

sel_sub = None
if sel:
    sel_sub = d.loc[d["name"] == sel, "subtype"].iloc[0]
    st.info(f"**{sel}站**：屬於 **{sel_sub}**")


def proposal(sub):
    a = advice[(advice["cluster_name"] == cluster) & (advice["subtype"] == sub)]
    return a["main_proposal"].iloc[0] if len(a) and a["main_proposal"].iloc[0] else "（主方案待填）"


st.subheader("子型規則卡")
r_c = rules[rules["cluster_name"] == cluster]
lines = []
for s in order:
    dot = f'<span style="color:{SUBTYPE_COLOR[s]};font-size:1.2em">●</span>'
    if s == "不細分":
        txt = "站數少，不再細分，沿用整群建議"
    elif s == "未符合核心條件":
        txt = "沿用第一層建議"
    else:
        txt = f"{rule_text(r_c[r_c['subtype'] == s])}　→ {proposal(s)}"
    lines.append(f"{dot} <b>{s}</b>（{counts[s]} 站）：{txt}")
st.markdown("<br>".join(lines), unsafe_allow_html=True)

if cluster not in NO_SPLIT_CLUSTERS:
    st.subheader("規則特徵分布")
    st.caption("每個點是一站，依子型上色；虛線是門檻（顏色＝用到這條門檻的子型）。空值的站不畫。")
    d["_jit"] = np.random.default_rng(0).uniform(-1, 1, len(d))
    feats = list(dict.fromkeys(r_c["feature"]))
    cols = st.columns(3)
    for i, f in enumerate(feats):
        is_log = f in LOG_FEATS
        hv = ".1%" if f in PCT_FEATS else (".2f" if f == "hub_gap" else ",.0f")
        fig = go.Figure()
        for s in order:
            p = d[(d["subtype"] == s) & d[f].notna()]
            fig.add_trace(go.Scatter(
                x=p[f], y=p["_jit"], mode="markers", name=s, text=p["name"],
                marker=dict(color=SUBTYPE_COLOR[s], size=7, opacity=0.75),
                hovertemplate="%{text}<br>%{x:" + hv + "}<extra>" + s + "</extra>",
            ))
        if sel and pd.notna(d.loc[d["name"] == sel, f].iloc[0]):
            p = d[d["name"] == sel]
            fig.add_trace(go.Scatter(
                x=p[f], y=p["_jit"], mode="markers+text", text=[sel],
                textposition="top center", hoverinfo="skip",
                marker=dict(color=SUBTYPE_COLOR[sel_sub], size=16,
                            line=dict(color="black", width=2)),
            ))
        conds = r_c[r_c["feature"] == f]
        for _, row in conds.iterrows():
            fig.add_vline(x=row["threshold"], line_dash="dash", line_width=1.5,
                          line_color=SUBTYPE_COLOR[row["subtype"]])
        fig.update_layout(base_layout())
        fig.update_layout(title=dict(text=conds["label"].iloc[0], font=dict(size=14)),
                          height=230, showlegend=False,
                          margin=dict(l=10, r=10, t=40, b=30))
        fig.update_yaxes(visible=False, range=[-1.6, 1.9])
        if f in PCT_FEATS:
            fig.update_xaxes(tickformat=".0%")
        if is_log:
            fig.update_xaxes(type="log")
        with cols[i % 3]:
            st.plotly_chart(fig, use_container_width=True)
            st.caption("門檻：" + "；".join(
                f"{row['subtype']} {OP_TXT[row['op']]} {fmt_thr(f, row['threshold'])}"
                for _, row in conds.iterrows()))

    st.subheader("子型比較（規則沒用到的變數）")
    st.caption("規則沒用到的變數，各子型之間也有差異，表示子型不只是門檻切出來的。")
    comp = (d.groupby("subtype")
              .agg(站數=("sta_code", "size"),
                   日均人次中位數=("mean_total", "median"),
                   稅籍餐飲中位數=("food_tax_1km", "median"),
                   Google餐廳中位數=("gm_food_1km", "median"),
                   人口中位數=("pop_1km", "median"),
                   名單站比例=("on_list_tax", "mean"),
                   臺鐵出租比例=("tra_lease", "mean"))
              .reindex(order))
    comp.index.name = "子型"
    st.dataframe(
        comp.style.format({"站數": "{:.0f}", "日均人次中位數": "{:,.0f}",
                           "稅籍餐飲中位數": "{:,.1f}", "Google餐廳中位數": "{:,.0f}","人口中位數": "{:,.0f}",
                           "名單站比例": "{:.0%}", "臺鐵出租比例": "{:.0%}"},
                          na_rep="—"),
        use_container_width=True,
    )
else:
    st.info("站數少，不再細分，下方直接顯示整群建議。")

st.subheader("招商建議表")
COLS = {"subtype": "子型", "main_proposal": "主方案", "flow_profile": "人流特性",
        "suitable": "適合業態", "unsuitable": "不適合業態",
        "reference": "參考案例", "example_stations": "候選站舉例"}
a = advice[advice["cluster_name"] == cluster]
if a.empty:
    st.warning("subtype_advice.csv 還沒有這一群的列。")
else:
    show = a.reindex(columns=list(COLS)).rename(columns=COLS)
    show["_o"] = show["子型"].map({s: i for i, s in enumerate(order)})
    show = show.sort_values("_o").drop(columns="_o")

    def hl(row):
        on = sel_sub is not None and row["子型"] == sel_sub
        return ["background-color:#fff1e8;border:2px solid #eb6834;font-weight:bold"
                if on else "" for _ in row]

    st.table(show.style.apply(hl, axis=1).hide(axis="index"))

st.subheader("各子型站名")
for s in order:
    names = d.loc[d["subtype"] == s, "name"].tolist()
    with st.expander(f"{s}（{len(names)} 站）"):
        st.write("、".join(names) if names else "（無）")

st.divider()
st.markdown(FOOTER, unsafe_allow_html=True)
st.caption(DATA_ASOF)