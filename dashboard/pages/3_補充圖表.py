import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

st.set_page_config(page_title="補充圖表", layout="wide")

st.title("補充圖表")
st.caption("本頁為企劃書柒章之附錄頁，收錄附圖 1–8 之原圖，供放大檢視。")

BASE = Path(__file__).resolve().parents[2] / "assets" / "supp"
ITEMS = [
    ("附圖1　全網前20大站日均運量（2024–2025）——規模排序與本作品行為分類之對照",
     ["fig02_top20_stations_2024_2025.png"]),
    ("附圖2　白沙屯周邊三站逐日運量三年疊圖（1–7月）——進香尖峰逐年移動且三站同步之原始證據",
     ["fig14_festival_daily.png"]),
    ("附圖3　月別振幅取對數前後之分布——說明特徵工程取對數之必要",
     ["fig15_f4a_log_effect.png"]),
    ("附圖4　階層式分群樹狀圖——分支結構與K-means五群一致之交叉佐證",
     ["dendrogram.png"]),
    ("附圖5　儀表板站型總覽表頁",
     ["dash_01b_map.png"]),
    ("附圖6　儀表板案例站頁：汐科（疊南港對照）逐日曲線",
     ["dash_02_xike_daily.png"]),
    ("附圖7　儀表板案例站頁：白沙屯逐日與星期×月別分布",
     ["dash_03_baishatun_daily.png", "dash_04_baishatun_dow_month.png"]),
    ("附圖8　儀表板站型與業態頁（完整業態表）",
     ["dash_06a_business_table.png"]),
]

for caption, files in ITEMS:
    st.subheader(caption)
    for fname in files:
        p = BASE / fname
        if p.exists():
            st.image(str(p), width="stretch")
        else:
            st.warning(f"找不到圖檔：{fname}")
    st.divider()
